# stdlib imports
import collections

# third-party imports
import pytest

# local imports
from shpkpr.marathon_lb.stats import Stats


@pytest.fixture
def haproxy_stats(file_fixture):
    csv_data = file_fixture("haproxy/stats.csv")
    return Stats(csv_data)


def test_stats_is_iterable(haproxy_stats):
    assert isinstance(haproxy_stats, collections.Iterable)


def test_stats_can_be_indexed(haproxy_stats):
    try:
        haproxy_stats[0]
        haproxy_stats[-1]
    except IndexError as e:
        pytest.fail("Unable to index `Stats` instance: {0}".format(e))


def test_stats_have_a_length(haproxy_stats):
    try:
        len(haproxy_stats)
    except TypeError as e:
        pytest.fail("`Stats` instance does not have a length: {0}".format(e))


def test_stats_does_not_contain_commented_rows(haproxy_stats):
    for stat in haproxy_stats:
        assert not stat[0].startswith("#")


def test_parse_haproxy_stats_count(haproxy_stats):
    assert len(haproxy_stats) == 31


def test_parse_haproxy_stats_first_row(haproxy_stats):
    assert haproxy_stats[0].pxname == 'http-in'
    assert haproxy_stats[0].svname == 'FRONTEND'


def test_parse_haproxy_stats_last_row(haproxy_stats):
    assert haproxy_stats[-1].pxname == 'http-in'
    assert haproxy_stats[-1].svname == '10_0_6_25_23336'
