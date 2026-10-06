#!/bin/bash

# stops only uav containers
docker ps -q --filter "name=uav" | xargs -r docker stop