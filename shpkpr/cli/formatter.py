# stdlib imports
import json

# third-party imports
import yaml


class OutputFormatter(object):
    """OutputFormatter is used to serialise complex Python objects for printing
    to the log.
    """

    def __init__(self, fmt):
        self.fmt = fmt

    def format(self, obj):
        formatters = {
            "json": self.to_json,
            "yaml": self.to_yaml,
        }
        return formatters[self.fmt](obj)

    def to_json(self, obj):
        return json.dumps(obj, indent=4, sort_keys=True)

    def to_yaml(self, obj):
        return yaml.dump(obj, default_flow_style=False)
