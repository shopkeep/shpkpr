# stdlib imports
from collections import namedtuple
import csv
from datetime import datetime
import socket
import time

# third-party imports
import click
import requests
import six.moves.urllib as urllib

# local imports
from shpkpr import exceptions


# amount of time (in seconds) between subsequent polls of the load balancer
# during a blue/green deploy.
MARATHON_LB_POLL_INTERVAL = 5


class SwapApplicationTimeout(exceptions.ShpkprException):
    pass


def _get_alias_records(hostname):
    """Return all IPv4 A records for a given hostname
    """
    return socket.gethostbyname_ex(hostname)[2]


def _unparse_url_alias(url, addr):
    """Reassemble a url object into a string but with a new address
    """
    return urllib.parse.urlunparse((url[0],
                                    addr + ":" + str(url.port),
                                    url[2],
                                    url[3],
                                    url[4],
                                    url[5]))


def get_marathon_lb_urls(marathon_lb_url):
    """Return a list of urls for all Aliases of the
       marathon_lb url passed in as an argument
    """
    url = urllib.parse.urlparse(marathon_lb_url)
    addrs = _get_alias_records(url.hostname)
    return [_unparse_url_alias(url, addr) for addr in addrs]


def fetch_haproxy_pids(logger, haproxy_url):
    try:
        response = requests.get(haproxy_url + "/_haproxy_getpids")
        response.raise_for_status()
    except requests.exceptions.RequestException:
        logger.log("Caught exception when retrieving HAProxy"
                   " pids from " + haproxy_url)
        raise

    return response.text.split()


def check_haproxy_reloading(logger, haproxy_url):
    """Return False if haproxy has only one pid, it is not reloading.
       Return True if we catch an exception while making a request to
       haproxy or if more than one pid is returned
    """
    try:
        pids = fetch_haproxy_pids(logger, haproxy_url)
    except requests.exceptions.RequestException:
        # Assume reloading on any error, this should be caught with a timeout
        return True

    if len(pids) > 1:
        logger.log("Waiting for {} pids on {}".format(len(pids), haproxy_url))
        return True

    return False


def any_marathon_lb_reloading(logger, marathon_lb_urls):
    return any([check_haproxy_reloading(logger, url) for url in marathon_lb_urls])


def fetch_haproxy_stats(logger, haproxy_url):
    try:
        response = requests.get(haproxy_url + "/haproxy?stats;csv")
        response.raise_for_status()
    except requests.exceptions.RequestException:
        logger.log("Caught exception when retrieving HAProxy"
                   " stats from " + haproxy_url)
        raise

    return response.text


def fetch_combined_haproxy_stats(logger, marathon_lb_urls):
    s = ''.join([fetch_haproxy_stats(logger, url) for url in marathon_lb_urls])
    return parse_haproxy_stats(s)


def parse_haproxy_stats(csv_data):
    rows = csv_data.splitlines()
    headings = rows.pop(0).lstrip('# ').rstrip(',\n').split(',')
    csv_reader = csv.reader(rows, delimiter=',', quotechar="'")

    Row = namedtuple('Row', headings)

    return [Row(*row[0:-1]) for row in csv_reader if row[0][0] != '#']


def get_deployment_label(app):
    return get_deployment_group(app) + "_" + app['labels']['HAPROXY_0_PORT']


def _is_app_listener(app, listener):
    return (listener.pxname == get_deployment_label(app) and
            listener.svname not in ['BACKEND', 'FRONTEND'])


def fetch_app_listeners(logger, app, marathon_lb_urls):
    haproxy_stats = fetch_combined_haproxy_stats(logger, marathon_lb_urls)
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


def swap_bluegreen_apps(logger, force, max_wait, marathon_client,
                        marathon_lb_url, new_app, old_app, timestamp):
    while True:

        check_time_and_sleep(max_wait, timestamp)

        old_app = marathon_client.get_application(old_app['id'])
        new_app = marathon_client.get_application(new_app['id'])

        logger.log("Existing app running {} instances, "
                   "new app running {} instances"
                   .format(old_app['instances'], new_app['instances']))

        marathon_lb_urls = get_marathon_lb_urls(marathon_lb_url)
        haproxy_count = len(marathon_lb_urls)

        try:
            listeners = fetch_app_listeners(logger, new_app, marathon_lb_urls)
        except requests.exceptions.RequestException:
            # Restart loop if we hit an exception while loading listeners,
            # this may be normal behaviour
            continue

        logger.log("Found {} app listeners across {} HAProxy instances"
                   .format(len(listeners), haproxy_count))

        if waiting_on_marathon_lb(logger, marathon_lb_urls, new_app, old_app,
                                  listeners, haproxy_count):
            continue

        drained_task_ids = \
            find_drained_task_ids(old_app, listeners, haproxy_count)

        if ready_to_delete_old_app(new_app, old_app, drained_task_ids):
            logger.log("About to delete old app {}".format(old_app['id']))
            return safe_delete_app(force, marathon_client, old_app)


def waiting_on_marathon_lb(logger, marathon_lb_urls, new_app, old_app,
                           listeners, haproxy_count):
    if any_marathon_lb_reloading(logger, marathon_lb_urls):
        return True

    if waiting_for_listeners(new_app, old_app, listeners, haproxy_count):
        return True

    if waiting_for_up_listeners(new_app, listeners, haproxy_count):
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
        app['container']['docker']['portMappings'][0]['servicePort'] = \
          int(servicePort)
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
        app['container']['docker']['portMappings'][0]['servicePort'] = \
          int(servicePort)
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
