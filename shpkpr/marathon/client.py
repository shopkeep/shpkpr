"""A collection of marathon-related utils
"""
# future imports
from __future__ import absolute_import

# third-party imports
import requests

# local imports
from .deployment import DeploymentNotFound
from .deployment import MarathonDeployment
from shpkpr import exceptions


class ClientError(exceptions.ShpkprException):
    pass


class DryRun(exceptions.ShpkprException):
    exit_code = 0


class MarathonClient(object):
    """A thin wrapper around marathon.MarathonClient for internal use
    """

    def __init__(self, marathon_url, username=None, password=None, dry_run=False):
        self._marathon_url = marathon_url
        self._dry_run = dry_run

        self._basic_auth = None
        if None not in [username, password]:
            self._basic_auth = requests.auth.HTTPBasicAuth(username, password)

    def _build_url(self, path):
        return self._marathon_url.rstrip("/") + path

    def _make_request(self, method, path, **kwargs):
        if self._dry_run:
            raise DryRun("Exiting as --dry-run requested")
        request = getattr(requests, method.lower())
        return request(self._build_url(path), auth=self._basic_auth, **kwargs)

    def embed_params(self, entity_type):
        return [
            "{0}.tasks".format(entity_type),
            "{0}.counts".format(entity_type),
            "{0}.deployments".format(entity_type),
            "{0}.lastTaskFailure".format(entity_type),
            "{0}.taskStats".format(entity_type),
        ]

    def get_info(self):
        """ Returns the marathon info from the /info endpoint
        """
        path = "/v2/info"
        response = self._make_request('GET', path)
        if response.status_code == 200:
            return response.json()
        raise ClientError("Unable to retrieve info from marathon")

    def delete_application(self, application_id, force=False):
        """Deletes the Application corresponding with application_id
        """
        path = "/v2/apps/" + application_id
        params = {"force": "true"} if force else {}
        response = self._make_request('DELETE', path, params=params)

        if response.status_code == 200:
            return True
        else:
            return False

    def get_application(self, application_id):
        """Returns detailed information for a single application.
        """
        path = "/v2/apps/" + application_id
        params = {"embed": self.embed_params("app")}
        response = self._make_request('GET', path, params=params)

        if response.status_code == 200:
            application = response.json()['app']
            return application

        # raise an appropriate error if something went wrong
        if response.status_code == 404:
            raise ClientError("Unable to retrieve application details from marathon: does not exist.")

        raise ClientError("Unknown Marathon error: %s\n\n%s" % (response.status_code, response.text))

    def list_applications(self):
        """Return a list of all applications currently deployed to marathon.
        """
        path = "/v2/apps"
        params = {"embed": self.embed_params("apps")}
        response = self._make_request('GET', path, params=params)

        if response.status_code == 200:
            applications = response.json()['apps']
            application_list = []
            for app in applications:
                application_list.append(app)
            return application_list

        raise ClientError("Unknown Marathon error: %s\n\n%s" % (response.status_code, response.text))

    def deploy(self, application_payload, force=False):
        """Deploys the given application(s) to Marathon.
        """
        # if the payload is a list and is one element long then we extract it
        # as we want to treat single app deploys differently. Doing this here
        # helps keep the cmd implementation clean.
        if isinstance(application_payload, (list, tuple)) and len(application_payload) == 1:
            application_payload = application_payload[0]

        # if at this point our payload is a dict then we treat it as a single
        # app, otherwise we treat it as a list of multiple applications to be
        # deployed together.
        if isinstance(application_payload, (list, tuple)):
            path = "/v2/apps/"
        else:
            path = "/v2/apps/" + application_payload['id']

        params = {"force": "true"} if force else {}
        response = self._make_request('PUT', path, params=params, json=application_payload)

        if response.status_code in [200, 201]:
            deployment = response.json()
            return MarathonDeployment(self, deployment['deploymentId'])

        # raise an appropriate error if something went wrong
        if response.status_code == 409:
            deployment_ids = ', '.join([x['id'] for x in response.json()['deployments']])
            raise ClientError("App(s) locked by one or more deployments: %s" % deployment_ids)

        raise ClientError("Unknown Marathon error: %s\n\n%s" % (response.status_code, response.text))

    def get_deployment(self, deployment_id):
        """Returns detailed information for a single deploy
        """
        response = self._make_request('GET', "/v2/deployments")

        if response.status_code == 200:
            for deployment in response.json():
                if deployment['id'] == deployment_id:
                    return deployment
            raise DeploymentNotFound(deployment_id)

        raise ClientError("Unknown Marathon error: %s\n\n%s" % (response.status_code, response.text))
