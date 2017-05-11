# stdlib imports
import csv
from collections import namedtuple

# third-party imports
from cached_property import cached_property


class Stats(object):

    def __init__(self, *instance_stats):
        self._raw_stats = instance_stats

    def __iter__(self):
        return (r for r in self._stats)

    def __getitem__(self, i):
        return self._stats[i]

    def __len__(self):
        return len(self._stats)

    @cached_property
    def _stats(self):
        """Parse and aggregate all stats files, caching the result
        """
        _stats = []
        for instance_stats in self._raw_stats:
            _stats.extend(self._parse_instance_stats(instance_stats))
        return _stats

    def _parse_instance_stats(self, instance_stats):
        """Parse a single HAProxy stats CSV file.
        """
        rows = instance_stats.splitlines()
        headers = rows[0].lstrip('# ').rstrip(',\n').split(',')
        csv_reader = csv.reader(rows[1:], quotechar="'")

        Row = namedtuple('Row', headers)
        return [Row(*row[0:-1]) for row in csv_reader if row[0][0] != '#']
