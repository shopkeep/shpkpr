# stdlib imports
from collections import Counter

# local imports
from shpkpr import exceptions


class ValidationError(exceptions.ShpkprException):
    exit_code = 2

    def format_message(self):
        return 'Unable to validate deployment: %s' % self.message


class Validator(object):
    """Validator is used to run pre-flight checks on a pending deployment.

    The validation is executed after the template is rendered but before the
    application definition is prepared/transformed for deployment.
    """

    def __init__(self, marathon_client, validators=None):
        if validators is None:
            validators = [AppDefinitionValidator, MarathonStateValidator]
        self.validators = [v(marathon_client) for v in validators]

    def validate(self, app_definition):
        for validator in self.validators:
            validator.validate(app_definition)


class AppDefinitionValidator(object):
    """Ensure that an app definition has the minimum set of labels required for
    a bluegreen deploy.

    These labels ensure shpkpr is able to manage and track "groups" of otherwise
    independent/standalone applications that have previously been deployed to
    Marathon.
    """

    REQUIRED_LABELS = [
        "HAPROXY_DEPLOYMENT_GROUP"
    ]

    ERROR_MESSAGE = "Missing label(s) from application definition: {0}"

    def __init__(self, *args, **kwargs):
        pass

    def validate(self, app_definition):
        missing_labels = []
        labels = app_definition.get('labels', {})
        for required_label in self.REQUIRED_LABELS:
            if required_label in labels:
                continue
            missing_labels.append(required_label)
        if missing_labels:
            msg = self.ERROR_MESSAGE.format(", ".join(missing_labels))
            raise ValidationError(msg)


class MarathonStateValidator(object):
    """Ensure that the application is in a clean state on Marathon before
    deploying.

    This validator checks that exactly one application is running in the target
    deployment group. If more than one application stack (typically both blue
    and green) are detected then it may indicate that another deploy is in
    progress or that a previous failed but wasn't cleaned up. Either way a
    deployment should not continue under those circumstances.
    """

    ERROR_MESSAGE = (
        "More than one active application stack detected on Marathon, please "
        "resolve before continuing with your deploy. This may indicate that "
        "another deploy is already in progress or that a previous one has "
        "failed."
    )

    def __init__(self, marathon_client, *args, **kwargs):
        self.marathon_client = marathon_client

    def validate(self, app_definition):
        def get_deployment_group(app_definition):
            labels = app_definition.get('labels', {})
            return labels.get('HAPROXY_DEPLOYMENT_GROUP')

        app_group = get_deployment_group(app_definition)

        remote_apps = self.marathon_client.list_applications()
        remote_groups = [get_deployment_group(app) for app in remote_apps]

        if Counter(remote_groups)[app_group] > 1:
            raise ValidationError(self.ERROR_MESSAGE)
