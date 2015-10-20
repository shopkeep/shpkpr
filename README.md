deploytool
=======

deploytool is a small Python script designed to be used on Jenkins to assist with deploys of Docker based applications to our staging and production Mesos/Marathon clusters.


### Current Features:

- Check the deployment status of a given Docker image to Marathon
- Block (until a timeout elapses) until a deploy has completed successfully to Marathon


### Future Features:

- JSON templating of Marathon deploy configuration (so we can remove the use of that Perl one-liner throughout core services)
- Performing deployments directly to Marathon (removing the need for `curl`)
- Providing a rich command-line interface to allow developers to easily interact with and get info from the Marathon API


## Usage

`deploytool` is hosted on ShopKeep's private Docker registry and can be pulled from there for use on Jenkins. If you want to build the image locally, you can use Docker:

```bash
$ docker build -t deploytool .
```

To run the image, you'll need to pass 2 command line arguments:

1) `APP_ID`: The ID of the application being checked (as defined on Marathon)
2) `REPOTAG`: The Docker repotag (repository/tag combination) that is expected to be deployed to Marathon

Additionally, if you need to check a Marathon environment other than `staging` you can pass in a custom environment variable that looks like: `MARATHON_API_ENDPOINT="http://cfn-marathon-serenity-mesos-someenv-us-east-1.posrip.com:8080/v2/apps/"`.

```bash
# wait until the given version of the godoc image is deployed
$ docker run -ti deploytool godoc godoc_service:master-7c3baf4ba7986367b5895ac61101cd86f7fcd6b4
Deploy in progress: waiting
Deploy in progress: waiting
Deploy succeeded: exiting
```