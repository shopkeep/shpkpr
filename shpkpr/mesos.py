"""A collection of mesos-related utils

(mostly extracted from the dcos/dcoscli library)
"""
# third-party imports
from dcos import mesos as dcos_mesos
from dcos import util
from dcos.errors import DCOSException


class MesosClient(dcos_mesos.DCOSClient):
    """Custom Mesos client, overriding to provide different configuration
    mechanism
    """

    def __init__(self, mesos_master_url):
        self._dcos_url = None
        self._timeout = 5
        self._mesos_master_url = mesos_master_url
        self._mesos_master = dcos_mesos.Master(self.get_master_state())

    def get_tasks(self, fltr, completed=False):
        """Return tasks from mesos that match the given filter

        If completed is True, tasks that are no longer running will also be
        returned if available.

        `fltr` does not need to be an exact match and can match multiple
        tasks. Suppose your cluster is running the following tasks:

            hadoop.myjob.12345-1928731
            rails.48271236-1231234
            app-10.89934ht-2398hriwuher
            app-20.9845uih-9823hriu-2938u422

        A fltr value of "app" will match both app-10 and app-20.
        A fltr value of "myjob" will only match the hadoop task.
        A fltr value of "1231234" will only match the rails task.
        """
        return self._mesos_master.tasks(completed=completed, fltr=fltr)


def _mesos_files(tasks, file_, client):
    """Return MesosFile objects for the specified tasks and file name.
    Only include files that satisfy all of the following:
    a) belong to an available slave
    b) have an executor entry on the slave
    """

    # load slave state in parallel
    slaves = _load_slaves_state([task.slave() for task in tasks])

    # some completed tasks may have entries on the master, but none on
    # the slave.  since we need the slave entry to get the executor
    # sandbox, we only include files with an executor entry.
    available_tasks = [task for task in tasks if task.slave() in slaves and task.executor()]

    # create files.
    return [dcos_mesos.MesosFile(file_, task=task, dcos_client=client) for task in available_tasks]


def _load_slaves_state(slaves):
    """Fetch each slave's state.json in parallel, and return the reachable
    slaves.
    """

    reachable_slaves = []
    for job, slave in util.stream(lambda slave: slave.state(), slaves):
        try:
            job.result()
            reachable_slaves.append(slave)
        # job.result() will throw a DCOSException when it is unable to contact
        # a given slave for any reason
        except DCOSException:
            pass

    return reachable_slaves
