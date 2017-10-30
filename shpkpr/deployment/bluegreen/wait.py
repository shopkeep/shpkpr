# stdlib imports
import logging
import time

# local imports
from . import stats
from shpkpr import exceptions


logger = logging.getLogger(__name__)


class SwapApplicationTimeout(exceptions.ShpkprException):
    pass


class Waiter(object):
    """Wait for a bluegreen deployment to complete by inspecting Marathon-LB's
    stats endpoint.

    This process ensures that the new application is up, stable, and serving
    traffic, and also that the old application is no longer being routed to at
    the load-balancer layer.
    """

    # amount of time (in seconds) between subsequent polls of the load balancer
    # whilst waiting for traffic to cut over to the new application.
    MARATHON_LB_POLL_INTERVAL = 5

    def __init__(self, marathon_client, marathon_lb_client, new_app_id, old_app_id):
        self.marathon_client = marathon_client
        self.marathon_lb_client = marathon_lb_client
        self.new_app_id = new_app_id
        self.old_app_id = old_app_id

    def check(self):
        """Check if the cutover is complete
        """
        if self.marathon_lb_client.is_reloading():
            logger.info("Waiting for Marathon-LB to settle (reloading detected)")
            return False

        new_app = self.marathon_client.get_application(self.new_app_id)
        old_app = self.marathon_client.get_application(self.old_app_id)
        app_stats = self._fetch_application_stats(new_app)
        if not self._new_app_is_up(app_stats, new_app):
            logger.info("Waiting for new application to come up")
            return False
        if not self._old_app_is_drained(app_stats, old_app):
            logger.info("Waiting for traffic to drain from old application")
            return False
        return True

    def wait(self, deadline):
        """Repeatedly check if all incoming traffic has been cut over to the new
        application.

        Blocks until success or ``deadline`` is reached.
        """
        _msg = "Waiting for traffic to cut over from `{0}` to `{1}`"
        logger.info(_msg.format(self.old_app_id, self.new_app_id))

        while not self.check():
            if time.time() >= deadline:
                raise SwapApplicationTimeout('Max wait Time Exceeded')
            time.sleep(self.MARATHON_LB_POLL_INTERVAL)

        logger.info("Traffic successfully routed to new application")

    def _fetch_application_stats(self, app_definition):
        """Fetch stats from HAProxy for the current application.
        """
        all_stats = self.marathon_lb_client.fetch_stats()
        return stats.ApplicationStats(app_definition, all_stats)

    def _new_app_is_up(self, app_stats, app):
        """Check that all tasks for the new application are up, are stable, and
        are serving live traffic.
        """
        haproxy_count = self.marathon_lb_client.instance_count
        checker = ListenerCheck(app_stats, app, haproxy_count)
        return checker.check("UP")

    def _old_app_is_drained(self, app_stats, app):
        """Check that all tasks for the old application have been drained and
        are no longer serving live traffic.
        """
        haproxy_count = self.marathon_lb_client.instance_count
        checker = ListenerCheck(app_stats, app, haproxy_count)
        return checker.check("MAINT", predicate=_has_no_pending_requests)


def _has_no_pending_requests(listener):
    """Returns `True` if the given listener has zero currently queued requests
    and zero currently active sessions, `False` otherwise.
    """
    return int(listener.qcur or 0) == 0 and int(listener.scur or 0) == 0


class ListenerCheck(object):

    def __init__(self, app_stats, app, haproxy_count):
        self.app_stats = app_stats
        self.app = app
        self.haproxy_count = haproxy_count

    def check(self, status, predicate=lambda _: True):
        # fetch all listeners with the given status
        listeners = self.app_stats.listeners_with_status(status)
        # filter the list to contain only those listeners for which
        # `predicate(listener)` returns `True`
        listeners = [l for l in listeners if predicate(l)]
        # ensure that task and listener counts match up
        return self._check_listeners_for_tasks(listeners)

    def _check_listeners_for_tasks(self, listeners):
        """Check that the expected number of listeners are present for each task
        belonging to this application.
        """
        for task in self.app["tasks"]:
            if not self._check_listeners_for_task(listeners, task):
                return False
        return True

    def _check_listeners_for_task(self, listeners, task):
        """Check that the expected number of listeners for the given task are
        present.
        """
        # build a service name from the given marathon task which matches the
        # format used by HAProxy's stats CSV
        _prefix = task['host'].replace('.', '_')
        _port = task['ports'][0]
        svname = '{0}_{1}'.format(_prefix, _port)

        # filter listeners to only those for the given task
        listeners = [l for l in listeners if l.svname == svname]
        # ensure there's exactly one listener for each marathon-lb/haproxy
        # instance
        return len(listeners) == self.haproxy_count
