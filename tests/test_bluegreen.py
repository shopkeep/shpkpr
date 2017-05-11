# stdlib imports
import json
import os

# third-party imports
import mock

# local imports
from shpkpr.bluegreen import prepare_deploy
from shpkpr.bluegreen import fetch_app_listeners
from shpkpr.bluegreen import get_svnames_from_tasks
from shpkpr.bluegreen import find_drained_task_ids
from shpkpr.marathon_lb.stats import Stats


def _load_listeners():
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fixtures', 'haproxy_stats.csv')
    with open(path) as f:
        return Stats(f.read())


def _load_marathon_apps():
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fixtures', 'bluegreen_apps.json')
    with open(path) as f:
        return json.loads(f.read())['apps']


def _load_blue_app():
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fixtures', 'bluegreen_app_blue.json')
    with open(path) as f:
        return json.loads(f.read())['apps'][0]


def test_prepare_deploy_swap_colors():
    previous_apps = _load_marathon_apps()
    blue_app = _load_blue_app()

    deploy = prepare_deploy(previous_apps, blue_app)

    assert deploy['labels']['HAPROXY_DEPLOYMENT_COLOUR'] == 'green'
    assert deploy['instances'] == blue_app['instances']


def test_prepare_deploy_first_deploy():
    previous_apps = []
    blue_app = _load_blue_app()

    deploy = prepare_deploy(previous_apps, blue_app)

    assert deploy['labels']['HAPROXY_DEPLOYMENT_COLOUR'] == 'blue'
    assert deploy['instances'] == blue_app['instances']


def test_parse_haproxy_stats():
    results = _load_listeners()

    assert results[1].pxname == 'http-in'
    assert results[1].svname == 'IPv4-direct'

    assert results[2].pxname == 'http-out'
    assert results[2].svname == 'IPv4-cached'


def test_fetch_app_listeners():
    marathon_lb_client = mock.Mock()
    marathon_lb_client.fetch_stats.side_effect = _load_listeners

    app = {
        'labels': {
            'HAPROXY_DEPLOYMENT_GROUP': 'foobar',
            'HAPROXY_0_PORT': '8080'
        }
    }

    app_listeners = fetch_app_listeners(app, marathon_lb_client)

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
