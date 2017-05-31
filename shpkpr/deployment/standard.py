

class StandardDeployment(object):
    """StandardDeployment implements Marathon's basic deployment workflow and
    uses the primitives provided by the Marathon API to perform a standard
    rolling deploy according to application settings.

    This deployment strategy is best suited for non-web-facing applications or
    those that can tolerate minor downtime during deployment e.g. consumer or
    worker applications.
    """

    def __init__(self, marathon_client, timeout, app_definitions, **kw):
        self.marathon_client = marathon_client
        self.timeout = timeout
        self.app_definitions = app_definitions

    def execute(self, force=False):
        """Execute standard Marathon deployment.
        """
        deployment = self.marathon_client.deploy(
            self.app_definitions,
            force=force,
        )
        return deployment.wait(timeout=self.timeout)
