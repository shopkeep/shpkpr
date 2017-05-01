===========================
Showing Application Details
===========================

``shpkpr show`` allows you to view details of one or all applications that are currently deployed to Marathon::

    $ shpkpr show --help
    Usage: shpkpr show [OPTIONS]

      Shows detailed information for one or all applications.

    Options:
    --output-format [json|yaml]  Serialisation format to use when printing
                                 application data to stdout.
    -a, --application TEXT       ID/name of the application to scale.
    --marathon_url TEXT          URL of the Marathon API to use.  [required]
    --help                       Show this message and exit.

Required Configuration
~~~~~~~~~~~~~~~~~~~~~~

**Marathon URL:**

    URL of the Marathon API to use, e.g. ``http://marathon.mydomain.com:8080``

    * Environment variable: ``SHPKPR_MARATHON_URL``
    * Command-line flag: ``--marathon_url``

Optional Configuration
^^^^^^^^^^^^^^^^^^^^^^

**Application ID:**

    ID of the application to show, e.g. ``my-app``. If not provided ``shpkpr`` will return a list of *all* currently deployed applications.

    * Environment variable: ``SHPKPR_APPLICATION``
    * Command-line flag: ``--application``
    * Default: ``None``

**Output Format:**

    Serialisation format used when printing details to stdout, e.g. ``yaml``

    * Environment variable: ``SHPKPR_OUTPUT_FORMAT``
    * Command-line flag: ``--output-format``
    * Default: ``json``

Examples
~~~~~~~~

::

    $ shpkpr show -a my-app
    {
        "args": null,
        "cmd": null,
        "constraints": [
            [
                "hostname",
                "UNIQUE"
            ]
        ],
        "container": {
            "docker": {
                "forcePullImage": false,
                "image": "my-docker-registry.com/my-app:some-tag",
                "network": "BRIDGE",
                "parameters": [],
                "portMappings": [
                    {
                        "containerPort": 4999,
                        "hostPort": 0,
                        "labels": {},
                        "protocol": "tcp",
                        "servicePort": 11070
                    }
                ],
                "privileged": false
            },
            "type": "DOCKER",
            "volumes": []
        },
        "cpus": 0.1,
        "deployments": [],
        "env": {
            "DEPLOY_ENVIRONMENT": "staging",
            "NEW_RELIC_ENVIRONMENT": "staging",
        },
        "id": "/my-app",
        "instances": 4,
        "mem": 512,
        "tasks": [
            {
                "appId": "/my-app",
                "healthCheckResults": [
                    {
                        "alive": true,
                        "consecutiveFailures": 0,
                        "firstSuccess": "2017-04-19T10:03:59.470Z",
                        "lastFailure": null,
                        "lastFailureCause": null,
                        "lastSuccess": "2017-04-24T13:57:07.387Z",
                        "taskId": "my-app.7b11d1f6-24e7-11e7-83e7-0a9211a8d240"
                    }
                ],
                "host": "10.210.84.170",
                "id": "my-app.7b11d1f6-24e7-11e7-83e7-0a9211a8d240",
                "ipAddresses": [
                    {
                        "ipAddress": "172.17.0.4",
                        "protocol": "IPv4"
                    }
                ],
                "ports": [
                    31039
                ],
                "slaveId": "ef806cb6-4ccd-46ae-b507-c47a793e0379-S13",
                "stagedAt": "2017-04-19T10:03:47.890Z",
                "startedAt": "2017-04-19T10:03:52.157Z",
                "version": "2017-02-23T12:14:50.238Z"
            },
            {
                "appId": "/my-app",
                "healthCheckResults": [
                    {
                        "alive": true,
                        "consecutiveFailures": 0,
                        "firstSuccess": "2017-04-19T10:08:29.979Z",
                        "lastFailure": "2017-04-19T10:17:46.053Z",
                        "lastFailureCause": "AskTimeoutException: Ask timed out on [Actor[akka://marathon/user/IO-HTTP#-1526159107]] after [5000 ms]",
                        "lastSuccess": "2017-04-24T13:57:07.388Z",
                        "taskId": "my-app.1c8db1d0-24e8-11e7-83e7-0a9211a8d240"
                    }
                ],
                "host": "10.210.68.176",
                "id": "my-app.1c8db1d0-24e8-11e7-83e7-0a9211a8d240",
                "ipAddresses": [
                    {
                        "ipAddress": "172.17.0.7",
                        "protocol": "IPv4"
                    }
                ],
                "ports": [
                    31241
                ],
                "slaveId": "ef806cb6-4ccd-46ae-b507-c47a793e0379-S12",
                "stagedAt": "2017-04-19T10:08:18.815Z",
                "startedAt": "2017-04-19T10:08:23.050Z",
                "version": "2017-02-23T12:14:50.238Z"
            },
            {
                "appId": "/my-app",
                "healthCheckResults": [
                    {
                        "alive": true,
                        "consecutiveFailures": 0,
                        "firstSuccess": "2017-04-19T10:13:30.585Z",
                        "lastFailure": null,
                        "lastFailureCause": null,
                        "lastSuccess": "2017-04-24T13:57:07.387Z",
                        "taskId": "my-app.d06e4756-24e8-11e7-83e7-0a9211a8d240"
                    }
                ],
                "host": "10.210.93.193",
                "id": "my-app.d06e4756-24e8-11e7-83e7-0a9211a8d240",
                "ipAddresses": [
                    {
                        "ipAddress": "172.17.0.2",
                        "protocol": "IPv4"
                    }
                ],
                "ports": [
                    31498
                ],
                "slaveId": "ef806cb6-4ccd-46ae-b507-c47a793e0379-S20",
                "stagedAt": "2017-04-19T10:13:20.600Z",
                "startedAt": "2017-04-19T10:13:21.469Z",
                "version": "2017-02-23T12:14:50.238Z"
            },
            {
                "appId": "/my-app",
                "healthCheckResults": [
                    {
                        "alive": true,
                        "consecutiveFailures": 0,
                        "firstSuccess": "2017-04-19T10:29:52.497Z",
                        "lastFailure": null,
                        "lastFailureCause": null,
                        "lastSuccess": "2017-04-24T13:57:07.387Z",
                        "taskId": "my-app.1ca3a37c-24eb-11e7-83e7-0a9211a8d240"
                    }
                ],
                "host": "10.210.59.63",
                "id": "my-app.1ca3a37c-24eb-11e7-83e7-0a9211a8d240",
                "ipAddresses": [
                    {
                        "ipAddress": "172.17.0.2",
                        "protocol": "IPv4"
                    }
                ],
                "ports": [
                    31390
                ],
                "slaveId": "ef806cb6-4ccd-46ae-b507-c47a793e0379-S21",
                "stagedAt": "2017-04-19T10:29:47.450Z",
                "startedAt": "2017-04-19T10:29:48.304Z",
                "version": "2017-02-23T12:14:50.238Z"
            }
        ],
        "tasksRunning": 4,
        "tasksUnhealthy": 0,
        "version": "2017-02-23T12:14:50.238Z"
    }
