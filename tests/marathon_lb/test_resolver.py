# third-party imports
import mock

# local imports
from shpkpr.marathon_lb import resolver


def _mock_gethostbyname_ex(aliaslist=None, ipaddrlist=None):
    """Returns a mocked socket.gethostbyname_ex function for testing use
    """
    if aliaslist is None:
        aliaslist = []
    if ipaddrlist is None:
        ipaddrlist = ['127.0.0.1']
    return lambda hostname: (hostname, aliaslist, ipaddrlist)


@mock.patch('socket.gethostbyname_ex')
def test_resolve(gethostbyname_ex):
    ipaddrlist = ['127.0.0.1', '127.0.0.2']
    gethostbyname_ex.side_effect = _mock_gethostbyname_ex(ipaddrlist=ipaddrlist)

    actual_urls = resolver.resolve('http://foobar.com:1234')
    expected_urls = ['http://127.0.0.1:1234', 'http://127.0.0.2:1234']

    assert actual_urls == expected_urls
