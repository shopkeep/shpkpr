# stdlib imports
import re

# third-party imports
import responses

# local imports
from shpkpr.mesos import resolve_leader_url
from shpkpr.mesos import MesosClient


def _mock_valid_redirect():
    responses.add(responses.HEAD,
                  'http://master.example.com:5050/master/redirect',
                  status=307,
                  adding_headers={'Location': '//leader.example.com:5050'})
    responses.add(responses.HEAD,
                  re.compile(r'http://leader\.example\.com:5050/?'),
                  status=200)


@responses.activate
def test_resolve_leader_valid_redirect():
    _mock_valid_redirect()

    leader_url = resolve_leader_url('http://master.example.com:5050')
    assert leader_url == "http://leader.example.com:5050"


@responses.activate
def test_resolve_leader_valid_redirect_with_trailing_slash():
    _mock_valid_redirect()

    leader_url = resolve_leader_url('http://master.example.com:5050/')
    assert leader_url == "http://leader.example.com:5050"


@responses.activate
def test_mesos_client_resolves_leader_url():
    _mock_valid_redirect()

    client = MesosClient('http://master.example.com:5050')
    # testing private members of a class isn't usually encouraged, however, in
    # this case the private members under test are the parts we've overridden
    # from dcos.mesos.DCOSClient and we need to test our implementation.
    assert client._leader_url is None
    assert client._mesos_master_url == "http://leader.example.com:5050"
    assert client._leader_url == "http://leader.example.com:5050"


@responses.activate
def test_mesos_client_caches_leader_url():
    # reset all response mocks to ensure the mesos client will raise an
    # exception if it tries to hit any remote URLs.
    responses.reset()

    client = MesosClient('http://master.example.com:5050')
    client._leader_url = "http://leader.example.com:5050"
    assert client._mesos_master_url == "http://leader.example.com:5050"
