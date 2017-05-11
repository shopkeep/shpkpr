# third-party imports
import requests
from cached_property import cached_property

# local imports
from . import resolver
from . import stats


class MarathonLBClient(object):
    """A high-level client used to interact with a set of load-balanced
    Marathon-LB instances.
    """

    def __init__(self, url):
        self.url = url

    @cached_property
    def urls(self):
        """Resolves the provided URL using DNS and returns a list of URLs that
        can be used to contact each individual Marathon-LB instance in a
        load-balanced set.
        """
        return resolver.resolve(self.url)

    @property
    def instance_count(self):
        """Number of Marathon-LB instances
        """
        return len(self.urls)

    def is_reloading(self):
        """Returns a boolean indicating whether any of the configured
        Marathon-LB instances is currently reloading.

        If an instance doesn't return exactly one process ID then it's either
        starting up, dead, or reloading.
        """
        for instance, pids in self._fetch_pids().items():
            if not len(pids) == 1:
                return True
        return False

    def fetch_stats(self):
        """Returns an iterable containing aggregated statistics from all
        configured Marathon-LB instances.

        See https://cbonte.github.io/haproxy-dconv/1.7/management.html#9.1 for a
        detailed breakdown of exactly what is available in the returned CSV and
        what the values in each column mean.
        """
        instance_stats = []
        for url in self.urls:
            instance_stats.append(self._fetch_instance_stats(url))
        return stats.Stats(*instance_stats)

    def _fetch_pids(self):
        """Fetch active PIDs from all Marathon-LB instances.
        """
        pids = {}
        for url in self.urls:
            pids[url] = self._fetch_instance_pids(url)
        return pids

    def _fetch_instance_pids(self, url):
        """Fetch a list of active PIDs from a single Marathon-LB instance.
        """
        response = requests.get(url + "/_haproxy_getpids")
        if not response.status_code == requests.codes.ok:
            return []
        return response.text.split()

    def _fetch_instance_stats(self, url):
        """Fetch statistics from a single Marathon-LB instance in CSV format.
        """
        response = requests.get(url + "/haproxy?stats;csv")
        response.raise_for_status()
        return response.text
