#!/bin/bash

# stops all docker containers
docker stop $(docker ps -aq)