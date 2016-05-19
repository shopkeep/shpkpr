"""A collection of marathon-related utils
"""
# future imports
from __future__ import absolute_import

# third-party imports
import json
import requests
from cached_property import cached_property

# local imports
from .deployment import DeploymentNotFound
from .deployment import MarathonDeployment
from .validate import Schema
from .validate import schema_path
from .validate import read_schema_from_file
from shpkpr import exceptions


class ClientError(exceptions.ShpkprException):
    pass


class DryRun(exceptions.ShpkprException):
    exit_code = 0


class MarathonClient(object):
    """A thin wrapper around marathon.MarathonClient for internal use
    """

    def __init__(self, marathon_url, app_schema_path=None, deploy_schema_path=None):
        self._marathon_url = marathon_url
        self._app_schema_path = app_schema_path
        self._deploy_schema_path = deploy_schema_path
        self.dry_run = False

    def _build_url(self, path):
        return self._marathon_url.rstrip("/") + path

    def _make_request(self, method, path, **kwargs):
        if self.dry_run:
            raise DryRun("Exiting as --dry-run requested")
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

    def delete_tasks(self, task_ids, scale=True):
        """Deletes and optionally scales apps for the task_ids given
        """
        path = '/v2/tasks/delete'
        data = json.dumps({'ids': task_ids})
        params = {'scale': scale}
        headers = {'Content-Type': 'application/json'}
        response = self._make_request('POST', path, headers=headers, params=params, data=data)

        if response.status_code == 200:
            return True
        else:
            return False

    def delete_application(self, application_id):
        """Deletes the Application corresponding with application_id
        """
        path = "/v2/apps/" + application_id
        response = self._make_request('DELETE', path)

        if response.status_code == 200:
            return True
        else:
            return False

    def get_application(self, application_id, strip_response=True):
        """Returns detailed information for a single application.
        """
        path = "/v2/apps/" + application_id
        params = {"embed": self.embed_params("app")}
        response = self._make_request('GET', path, params=params)

        if response.status_code == 200:
            application = response.json()['app']
            self.app_schema.validate(application)
            if strip_response:
                return self.app_schema.strip(application)
            else:
                return application

        # raise an appropriate error if something went wrong
        if response.status_code == 404:
            raise ClientError("Unable to retrieve application details from marathon: does not exist.")

        raise ClientError("Unknown Marathon error: %s\n\n%s" % (response.status_code, response.text))

    def list_applications(self, strip_response=True):
        """Return a list of all applications currently deployed to marathon.
        """
        path = "/v2/apps"
        params = {"embed": self.embed_params("apps")}
        response = self._make_request('GET', path, params=params)

        if response.status_code == 200:
            applications = response.json()['apps']
            application_list = []
            for app in applications:
                self.app_schema.validate(app)
                if strip_response:
                    application_list.append(self.app_schema.strip(app))
                else:
                    application_list.append(app)
            return application_list

        raise ClientError("Unknown Marathon error: %s\n\n%s" % (response.status_code, response.text))

    def list_application_ids(self):
        """Returns ids of all applications currently deployed to marathon.
        """

        return sorted([app['id'].lstrip('/') for app in self.list_applications()])

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
            for application in application_payload:
                self.deploy_schema.validate(application)
            path = "/v2/apps/"
        else:
            self.deploy_schema.validate(application_payload)
            path = "/v2/apps/" + application_payload['id']

        params = {"force": "true"} if force else {}
        response = self._make_request('PUT', path, params=params, json=application_payload)

        if response.status_code in [200, 201]:
            deployment = response.json()
            return MarathonDeployment(self, deployment['deploymentId'])

        # raise an appropriate error if something went wrong
        if response.status_code == 409:
            raise ClientError("Unknown Marathon error: %s\n\n%s" % (response.status_code, response.text))
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
