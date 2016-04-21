# stdlib imports
import json
import os

# third-party imports
import mock

# local imports
from shpkpr.marathon_lb import get_marathon_lb_urls
from shpkpr.marathon_lb import prepare_deploy
from shpkpr.marathon_lb import scale_new_app_instances
from shpkpr.marathon_lb import parse_haproxy_stats
from shpkpr.marathon_lb import fetch_app_listeners
from shpkpr.marathon_lb import get_svnames_from_tasks
from shpkpr.marathon_lb import find_drained_task_ids


def _load_listeners():
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fixtures', 'haproxy_stats.csv')
    with open(path) as f:
        return parse_haproxy_stats(f.read())


def _load_marathon_apps():
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fixtures', 'bluegreen_apps.json')
    with open(path) as f:
        return json.loads(f.read())['apps']


def _load_blue_app():
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fixtures', 'bluegreen_app_blue.json')
    with open(path) as f:
        return json.loads(f.read())['apps'][0]


@mock.patch('socket.gethostbyname_ex',
            mock.Mock(side_effect=lambda hostname:
                      (hostname, [], ['127.0.0.1', '127.0.0.2'])))
def test_get_marathon_lb_urls():
    marathon_lb_urls = get_marathon_lb_urls('http://foobar.com:9090')

    assert 'http://127.0.0.1:9090' in marathon_lb_urls
    assert 'http://127.0.0.2:9090' in marathon_lb_urls
    assert 'http://127.0.0.3:9090' not in marathon_lb_urls


def test_prepare_deploy_swap_colors():
    previous_apps = _load_marathon_apps()
    blue_app = _load_blue_app()
    initial_instances = 5

    deploy = prepare_deploy(previous_apps, blue_app, initial_instances)

    assert deploy['labels']['HAPROXY_DEPLOYMENT_COLOUR'] == 'green'
    assert deploy['instances'] == initial_instances


def test_prepare_deploy_first_deploy():
    previous_apps = []
    blue_app = _load_blue_app()
    initial_instances = 5

    deploy = prepare_deploy(previous_apps, blue_app, initial_instances)

    assert deploy['labels']['HAPROXY_DEPLOYMENT_COLOUR'] == 'blue'
    assert deploy['instances'] == blue_app['instances']


@mock.patch('shpkpr.cli.logger.Logger')
@mock.patch('shpkpr.marathon.client')
@mock.patch('shpkpr.marathon_lb.scale_marathon_app_instances')
def test_scale_new_app_instances_up_50_percent(scale_marathon_app_instances,
                                               marathon_client, logger):
    """When scaling new_app instances, increase instances by 50% of
       existing instances if we have not yet met or surpassed the amount
       of instances deployed by old_app
    """
    new_app = {
        'instances': 10,
        'labels': {
            'HAPROXY_DEPLOYMENT_TARGET_INSTANCES': 30
        }
    }
    old_app = {'instances': 30}
    scale_new_app_instances(logger, marathon_client, new_app, old_app)

    scale_marathon_app_instances.assert_called_with(
      marathon_client, new_app, 15)


@mock.patch('shpkpr.cli.logger.Logger')
@mock.patch('shpkpr.marathon.client')
@mock.patch('shpkpr.marathon_lb.scale_marathon_app_instances')
def test_scale_new_app_instances_to_target(scale_marathon_app_instances,
                                           marathon_client, logger):
    """When scaling new instances up, if we have met or surpassed the
       amount of instances deployed for old_app, go right to our
       deployment target amount of instances for new_app
    """
    new_app = {
        'instances': 10,
        'labels': {
            'HAPROXY_DEPLOYMENT_TARGET_INSTANCES': 30
        }
    }
    old_app = {'instances': 8}
    scale_new_app_instances(logger, marathon_client, new_app, old_app)

    scale_marathon_app_instances.assert_called_with(
      marathon_client, new_app, 30)


def test_parse_haproxy_stats():
    results = _load_listeners()

    assert results[1].pxname == 'http-in'
    assert results[1].svname == 'IPv4-direct'

    assert results[2].pxname == 'http-out'
    assert results[2].svname == 'IPv4-cached'


@mock.patch('shpkpr.cli.logger.Logger')
@mock.patch('shpkpr.marathon_lb.fetch_combined_haproxy_stats',
            mock.Mock(side_effect=lambda _, __: _load_listeners()))
def test_fetch_app_listeners(logger):
    app = {
            'labels': {
              'HAPROXY_DEPLOYMENT_GROUP': 'foobar',
              'HAPROXY_0_PORT': '8080'
            }
          }

    app_listeners = fetch_app_listeners(logger, app, [])

    assert app_listeners[0].pxname == 'foobar_8080'
    assert len(app_listeners) == 1


def test_get_svnames_from_tasks():
    apps = _load_marathon_apps()
    tasks = apps[0]['tasks']

    task_svnames = get_svnames_from_tasks(tasks)

    assert '10_0_6_25_16916' in task_svnames
    assert '10_0_6_25_31184' in task_svnames


def test_find_drained_task_ids():
    listeners = _load_listeners()
    haproxy_instance_count = 2
    apps = _load_marathon_apps()
    app = apps[0]

    results = find_drained_task_ids(app, listeners, haproxy_instance_count)

    assert app['tasks'][0]['id'] in results  # 2 down, no sessions
    assert app['tasks'][1]['id'] not in results  # 1 up, one down
    assert app['tasks'][2]['id'] not in results  # 2 down, one w/ session
