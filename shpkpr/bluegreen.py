# stdlib imports
import logging
import time
from datetime import datetime

# third-party imports
import click
import requests

# local imports
from shpkpr import exceptions


logger = logging.getLogger(__name__)


# amount of time (in seconds) between subsequent polls of the load balancer
# during a blue/green deploy.
MARATHON_LB_POLL_INTERVAL = 5


class SwapApplicationTimeout(exceptions.ShpkprException):
    pass


def get_deployment_label(app):
    return get_deployment_group(app) + "_" + app['labels']['HAPROXY_0_PORT']


def _is_app_listener(app, listener):
    return (listener.pxname == get_deployment_label(app) and
            listener.svname not in ['BACKEND', 'FRONTEND'])


def fetch_app_listeners(app, marathon_lb_client):
    haproxy_stats = marathon_lb_client.fetch_stats()
    return [l for l in haproxy_stats if _is_app_listener(app, l)]


def waiting_for_listeners(new_app, old_app, listeners, haproxy_count):
    listener_count = (len(listeners) / haproxy_count)
    return listener_count != new_app['instances'] + old_app['instances']


def get_deployment_target(app):
    return int(app['labels']['HAPROXY_DEPLOYMENT_TARGET_INSTANCES'])


def waiting_for_up_listeners(app, listeners, haproxy_count):
    up_listeners = [l for l in listeners if l.status == 'UP']
    up_listener_count = (len(up_listeners) / haproxy_count)

    return up_listener_count < get_deployment_target(app)


def _has_pending_requests(listener):
    return int(listener.qcur or 0) > 0 or int(listener.scur or 0) > 0


def select_drained_listeners(listeners):
    draining_listeners = [l for l in listeners if l.status == 'MAINT']
    return [l for l in draining_listeners if not _has_pending_requests(l)]


def get_svnames_from_task(task):
    prefix = task['host'].replace('.', '_')
    for port in task['ports']:
        yield(prefix + '_{}'.format(port))


def get_svnames_from_tasks(tasks):
    svnames = []
    for task in tasks:
        svnames += get_svnames_from_task(task)
    return svnames


def find_drained_task_ids(app, listeners, haproxy_count):
    """Return app tasks which have all haproxy listeners down and drained
       of any pending sessions or connections
    """
    tasks = zip(get_svnames_from_tasks(app['tasks']), app['tasks'])
    drained_listeners = select_drained_listeners(listeners)

    drained_task_ids = []
    for svname, task in tasks:
        task_listeners = [l for l in drained_listeners if l.svname == svname]
        if len(task_listeners) == haproxy_count:
            drained_task_ids.append(task['id'])

    return drained_task_ids


def max_wait_exceeded(max_wait, timestamp):
    return (time.time() - timestamp > max_wait)


def check_time_and_sleep(max_wait, timestamp):
    if max_wait_exceeded(max_wait, timestamp):
        raise SwapApplicationTimeout('Max wait Time Exceeded')

    return time.sleep(MARATHON_LB_POLL_INTERVAL)


def swap_bluegreen_apps(force, max_wait, marathon_client, marathon_lb_client,
                        new_app, old_app, timestamp):
    while True:

        check_time_and_sleep(max_wait, timestamp)

        old_app = marathon_client.get_application(old_app['id'])
        new_app = marathon_client.get_application(new_app['id'])

        logger.info("Existing app running {} instances, "
                    "new app running {} instances"
                    .format(old_app['instances'], new_app['instances']))

        try:
            listeners = fetch_app_listeners(new_app, marathon_lb_client)
        except requests.exceptions.RequestException:
            # Restart loop if we hit an exception while loading listeners,
            # this may be normal behaviour
            continue

        logger.info("Found {} app listeners across {} HAProxy instances"
                    .format(len(listeners), marathon_lb_client.instance_count))

        if waiting_on_marathon_lb(marathon_lb_client, new_app, old_app,
                                  listeners):
            continue

        drained_task_ids = find_drained_task_ids(old_app, listeners, marathon_lb_client.instance_count)

        if ready_to_delete_old_app(new_app, old_app, drained_task_ids):
            logger.info("About to delete old app {}".format(old_app['id']))
            return safe_delete_app(force, marathon_client, old_app)


def waiting_on_marathon_lb(marathon_lb_client, new_app, old_app,
                           listeners):
    if marathon_lb_client.is_reloading():
        return True

    if waiting_for_listeners(new_app, old_app, listeners, marathon_lb_client.instance_count):
        return True

    if waiting_for_up_listeners(new_app, listeners, marathon_lb_client.instance_count):
        return True

    if waiting_for_drained_listeners(listeners):
        return True

    return False


def ready_to_delete_old_app(new_app, old_app, drained_task_ids):
    return (int(new_app['instances']) == get_deployment_target(new_app) and
            len(drained_task_ids) == int(old_app['instances']))


def waiting_for_drained_listeners(listeners):
    return len(select_drained_listeners(listeners)) < 1


def safe_delete_app(force, marathon_client, app):
    if force or click.confirm("Continue?"):
        marathon_client.delete_application(app['id'])
        return True
    else:
        return False


def get_service_port(app):
    try:
        return \
            int(app['container']['docker']['portMappings'][0]['servicePort'])
    except KeyError:
        return int(app['ports'][0])


def set_service_port(app, servicePort):
    try:
        app['container']['docker']['portMappings'][0]['servicePort'] = int(servicePort)
    except KeyError:
        app['ports'][0] = int(servicePort)

    return app


def validate_app(app):
    if app['id'] is None:
        raise Exception("App doesn't contain a valid App ID")
    if 'labels' not in app:
        raise Exception("No labels found. Please define the"
                        "HAPROXY_DEPLOYMENT_GROUP label")
    if 'HAPROXY_DEPLOYMENT_GROUP' not in app['labels']:
        raise Exception("Please define the "
                        "HAPROXY_DEPLOYMENT_GROUP label")
    if 'HAPROXY_DEPLOYMENT_ALT_PORT' not in app['labels']:
        raise Exception("Please define the "
                        "HAPROXY_DEPLOYMENT_ALT_PORT label")


def set_app_ids(app, colour):
    app['labels']['HAPROXY_APP_ID'] = app['id']
    app['id'] = app['id'] + '-' + colour

    return app


def set_service_ports(app, servicePort):
    app['labels']['HAPROXY_0_PORT'] = str(get_service_port(app))
    try:
        app['container']['docker']['portMappings'][0]['servicePort'] = int(servicePort)
        return app
    except KeyError:
        app['ports'][0] = int(servicePort)
        return app


def select_next_port(app):
    alt_port = int(app['labels']['HAPROXY_DEPLOYMENT_ALT_PORT'])
    if int(app['ports'][0]) == alt_port:
        return int(app['labels']['HAPROXY_0_PORT'])
    else:
        return alt_port


def select_next_colour(app):
    if app['labels'].get('HAPROXY_DEPLOYMENT_COLOUR') == 'blue':
        return 'green'
    else:
        return 'blue'


def sort_deploys(apps):
    return sorted(apps, key=lambda a: a.get('labels', {})
                  .get('HAPROXY_DEPLOYMENT_STARTED_AT', '0'))


def select_last_deploy(apps):
    return sort_deploys(apps).pop()


def get_deployment_group(app):
    return app.get('labels', {}).get('HAPROXY_DEPLOYMENT_GROUP')


def fetch_previous_deploys(marathon_client, app):
    apps = marathon_client.list_applications()
    app_deployment_group = get_deployment_group(app)
    return [a for a in apps if get_deployment_group(a) == app_deployment_group]


def prepare_deploy(previous_deploys, app):
    """ Return a blue or a green version of `app` based on prexisting deploys
    """
    if len(previous_deploys) > 0:
        last_deploy = select_last_deploy(previous_deploys)
        next_colour = select_next_colour(last_deploy)
        next_port = select_next_port(last_deploy)
        deployment_target_instances = last_deploy['instances']
    else:
        next_colour = 'blue'
        next_port = get_service_port(app)
        deployment_target_instances = app['instances']

    app = set_app_ids(app, next_colour)
    app = set_service_ports(app, next_port)
    app['labels']['HAPROXY_DEPLOYMENT_TARGET_INSTANCES'] = \
        str(deployment_target_instances)
    app['labels']['HAPROXY_DEPLOYMENT_COLOUR'] = next_colour
    app['labels']['HAPROXY_DEPLOYMENT_STARTED_AT'] = datetime.now().isoformat()

    return app
