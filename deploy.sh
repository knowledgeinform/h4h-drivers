# pull the Image Tag from the "VERSION.txt" file and set that before running Compose
VERSION=$(head -n 1 VERSION.txt)
echo "Running Version ${VERSION}"

# stop all docker containers
docker stop $(docker ps -aq)

# spin up the containers with the correct version tag
PROFILE=${1:-""}
if [ -z "$PROFILE" ]; then
    # no PROFILE arg, run without specification
    DOCKER_IMAGE_TAG=${VERSION} docker compose up -d --force-recreate
else
    # run with profile
    DOCKER_IMAGE_TAG=${VERSION} docker compose --profile $PROFILE up -d --force-recreate
fi
