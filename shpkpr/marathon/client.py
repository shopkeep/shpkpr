"""A collection of marathon-related utils
"""
# future imports
from __future__ import absolute_import

# third-party imports
import requests
from cached_property import cached_property

# local imports
from .deployment import MarathonDeployment
from .validate import Schema
from .validate import schema_path
from .validate import read_schema_from_file
from shpkpr import exceptions


class ClientError(exceptions.ShpkprException):
    pass


class MarathonClient(object):
    """A thin wrapper around marathon.MarathonClient for internal use
    """

    def __init__(self, marathon_url, app_schema_path=None, deploy_schema_path=None):
        self._marathon_url = marathon_url
        self._app_schema_path = app_schema_path
        self._deploy_schema_path = deploy_schema_path

    def _build_url(self, path):
        return self._marathon_url.rstrip("/") + path

    def _make_request(self, method, path, **kwargs):
        request = getattr(requests, method.lower())
        return request(self._build_url(path), **kwargs)

    def embed_params(self, entity_type):
        return [
            "{0}.tasks".format(entity_type),
            "{0}.counts".format(entity_type),
            "{0}.deployments".format(entity_type),
            "{0}.lastTaskFailure".format(entity_type),
            "{0}.taskStats".format(entity_type),
        ]

    @cached_property
    def app_schema(self):
        if self._app_schema_path is None:
            self._app_schema_path = schema_path("app")
        raw_schema = read_schema_from_file(self._app_schema_path)
        return Schema(raw_schema)

    @cached_property
    def deploy_schema(self):
        if self._deploy_schema_path is None:
            self._deploy_schema_path = schema_path("deploy")
        raw_schema = read_schema_from_file(self._deploy_schema_path)
        return Schema(raw_schema)

    def get_application(self, application_id):
        """Returns detailed information for a single application.
        """
        path = "/v2/apps/" + application_id
        params = {"embed": self.embed_params("app")}
        response = self._make_request('GET', path, params=params)

        if response.status_code == 200:
            application = response.json()['app']
            self.app_schema.validate(application)
            return self.app_schema.strip(application)

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
            stripped_applications = []
            for app in applications:
                self.app_schema.validate(app)
                stripped_applications.append(self.app_schema.strip(app))
            return stripped_applications

        raise ClientError("Unknown Marathon error: %s\n\n%s" % (response.status_code, response.text))

    def list_application_ids(self):
        """Returns ids of all applications currently deployed to marathon.
        """

        return sorted([app['id'].lstrip('/') for app in self.list_applications()])

    def deploy_application(self, application, force=False):
        """Deploys the given application to Marathon.
        """
        self.deploy_schema.validate(application)

        path = "/v2/apps/" + application['id']
        if force:
            params = {"force": "true"}
        else:
            params = {}
        response = self._make_request('PUT', path, params=params, json=application)

        if response.status_code in [200, 201]:
            deployment = response.json()
            return MarathonDeployment(self, application['id'], deployment['deploymentId'], deployment['version'])

        # raise an appropriate error if something went wrong
        if response.status_code == 409:
            raise ClientError("App is locked by one or more deployments: %s" % response.json()['deployments'][0]['id'])

        raise ClientError("Unknown Marathon error: %s\n\n%s" % (response.status_code, response.text))
