# third-party imports
from cached_property import cached_property


class ApplicationStats(object):

    def __init__(self, app_definition, stats):
        self._app_definition = app_definition
        self._stats = stats

    @cached_property
    def listeners(self):
        """Returns all HAProxy listeners for the current application.
        """
        all_listeners = [r for r in self._stats if r.svname not in ["BACKEND", "FRONTEND"]]
        app_listeners = [l for l in all_listeners if l.pxname == self._deployment_label]
        return app_listeners

    def listeners_with_status(self, status):
        """Returns listeners with the given status string.
        """
        return [r for r in self.listeners if r.status == status.upper()]

    @property
    def listener_count(self):
        return len(self.listeners)

    @property
    def _deployment_label(self):
        """Construct and return a label in the format used by HAProxy to
        identify this application.

        This label can be used when filtering the list of HAProxy listeners to
        only those for this application.
        """
        labels = self._app_definition['labels']
        group = labels['HAPROXY_DEPLOYMENT_GROUP']
        port = labels['HAPROXY_0_PORT']
        return "{0}_{1}".format(group, port)
