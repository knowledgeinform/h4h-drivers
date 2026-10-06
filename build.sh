#!/bin/bash


# Usage:
# ./build.sh                 --> builds ALL services in the docker-compose.yml file (and all base images)
# ./build.sh <service-name>  --> only builds the single service (and all base images)
# optional flag -a causes a --no-cache build


# update time
# ./update_time.sh # still not reliable for some reason!

NO_CACHE_BUILD=false

while getopts "a" opt; do
  case "$opt" in
    a)
      NO_CACHE_BUILD=true
      echo "Building with --no-cache"
      ;;
    \?)
      echo "Unknown option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done

# Remove parsed flags so "$@" only contains positional arguments.
shift $((OPTIND - 1))


# builds a single image via service name
# build_image "service_name"
function buildImage() {
  if [[ "$NO_CACHE_BUILD" == true ]]; then
    echo "Building image with --no-cache"
    DOCKER_IMAGE_TAG=$DOCKER_IMAGE_TAG docker compose build --no-cache $1
  else
    DOCKER_IMAGE_TAG=$DOCKER_IMAGE_TAG docker compose build $1
  fi

  # check the build command's exit code for failure
  ret_code=$?
  if [ $ret_code -ne 0 ]; then
    DOCKER_BUILD_FAIL_LIST+=($1)
  else
    DOCKER_BUILD_CHECKLIST+=($1)
  fi
}

# builds a single base image
function buildBaseImage() {
  # build the image
  if [[ "$NO_CACHE_BUILD" == true ]]; then
    echo "Building base image with --no-cache"
    docker build --no-cache --build-arg IMAGE_TAG=${DOCKER_IMAGE_TAG} -t ${1}:${DOCKER_IMAGE_TAG} -f dockerfiles/${1}.dockerfile .
  else
    docker build --build-arg IMAGE_TAG=${DOCKER_IMAGE_TAG} -t ${1}:${DOCKER_IMAGE_TAG} -f dockerfiles/${1}.dockerfile .
  fi

  # check the build command's exit code for failure
  ret_code=$?
  if [ $ret_code -ne 0 ]; then
    DOCKER_BUILD_FAIL_LIST+=($1)
  else
    DOCKER_BUILD_CHECKLIST+=($1)
  fi
}


# pull the version number from "VERSION.txt" and use that to set the image tag
VERSION=$(head -n 1 VERSION.txt)
echo "Building Version ${VERSION}"
DOCKER_IMAGE_TAG=${VERSION}


# track which builds completed and which builds failed
DOCKER_BUILD_CHECKLIST=() # a list of docker image names built
DOCKER_BUILD_FAIL_LIST=() # a list of failed docker image builds


# set names for base images
H4H_BASE="h4h-base"
H4H_SIM_BASE="h4h-sim-base"
# MAVROS_BASE="h4h-mavros"


# just always build them, it's too easy to forget about this and have annoying stale builds
buildBaseImage "$H4H_BASE"
buildBaseImage "$H4H_SIM_BASE"
# buildBaseImage "$MAVROS_BASE"


# check for single-image build
SERVICE=${1:-""}
if [ -z "$SERVICE" ]; then
  # no SERVICE arg, build everything
  SERVICE_LIST=$(docker compose config --services)
  for SERVICE in $SERVICE_LIST; do
    buildImage "$SERVICE"
  done
else
  # build one image
  buildImage "$SERVICE"
fi


# echo out the build list
echo "+++++++++++++++++++++++++++"
echo "Docker Image Build List:"
echo "---------------------------"
printf "%s\n" "${DOCKER_BUILD_CHECKLIST[@]}"
echo "---------------------------"
echo "+++++++++++++++++++++++++++"

# print out a warning if any images failed
if [[ ${#DOCKER_BUILD_FAIL_LIST[@]} -ne 0 ]]; then
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "Some Images Failed to Build:"
  echo "---------------------------"
  printf "%s\n" "${DOCKER_BUILD_FAIL_LIST[@]}"
  echo "---------------------------"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!"
fi