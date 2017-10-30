#!/usr/bin/env bash

set -o errexit

# Copy everything except dot directories from /src/ to /app/. A notable dot
# directory is '.tox', which we definitely don't want to copy into /app/,
# since it would stomp the one already there. Other dot directories may
# include virtual environments or other machine-specific configurations.
find /src -mindepth 1 -maxdepth 1 \( -type d -name ".*" -prune \) -o -exec cp -r --target-directory=/app -- {} +

# Tox will be run by the "tox" user, so it should own /app/.
find /app -name .tox -prune -o -print0 | xargs -0 chown tox:tox

DOCKER_SOCKET=/var/run/docker.sock
DOCKER_GROUP=docker
REGULAR_USER=tox

if [ -S ${DOCKER_SOCKET} ]; then
    DOCKER_GID=$(stat -c '%g' ${DOCKER_SOCKET})
    groupadd -for -g ${DOCKER_GID} ${DOCKER_GROUP}
    usermod -aG ${DOCKER_GROUP} ${REGULAR_USER}
fi

if [[ "${1}" == "tox" ]]; then
    # If the first argument was "tox" (which is the default), run tox
    # with the "tox" user, passing the remaining arguments right along.
    exec gosu tox "$@"
fi

# If the first argument was not "tox", run whichever command was given.
exec "$@"
