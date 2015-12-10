# stdlib imports
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

# third-party imports
import mock
import pytest
from dcos.errors import DCOSException
from dcos.mesos import MesosFile

# local imports
from shpkpr.cli import logger
from shpkpr.files import log_files
from shpkpr.mesos import MesosClient


class MockLogger(logger.Logger):

    def __init__(self):
        self.buffer = StringIO()


class MockFuture(object):

    def result(self):
        return [
            'AAAAA',
            'BBBBB',
            'CCCCC',
        ]


class MockFutureException(object):

    def result(self):
        raise DCOSException("BLAH")


def test_log_files_no_mesos_files():
    ctx = MockLogger()
    with pytest.raises(DCOSException):
        log_files(ctx, [], False, 10)


@mock.patch('shpkpr.mesos.MesosClient.get_master_state')
@mock.patch('dcos.util.stream')
def test_log_files_single_mesos_file(mock_util_stream, mock_get_master_state):
    ctx = MockLogger()
    _file = MesosFile("TestFile", dcos_client=MesosClient(""))

    # mock out the parts of `dcos` that make remote API calls.
    mock_util_stream.return_value = [(MockFuture(), _file)]
    mock_get_master_state.return_value = None

    log_files(ctx, [_file], False, 10)
    assert ctx.buffer.getvalue() == "AAAAA\n" + \
                                    "BBBBB\n" + \
                                    "CCCCC\n"


@mock.patch('shpkpr.mesos.MesosClient.get_master_state')
@mock.patch('dcos.util.stream')
def test_log_files_unreachable_mesos_file(mock_util_stream, mock_get_master_state):
    ctx = MockLogger()
    _file_1 = MesosFile("TestFile_1", dcos_client=MesosClient(""))
    _file_2 = MesosFile("TestFile_2", dcos_client=MesosClient(""))

    # mock out the parts of `dcos` that make remote API calls.
    mock_util_stream.return_value = [(MockFutureException(), _file_1), (MockFuture(), _file_2)]
    mock_get_master_state.return_value = None

    log_files(ctx, [_file_1, _file_2], False, 10)
    assert ctx.buffer.getvalue() == "[2] AAAAA\n" + \
                                    "[2] BBBBB\n" + \
                                    "[2] CCCCC\n"
