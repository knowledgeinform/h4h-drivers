#!/usr/bin/env bash
set -e

#docker  cannot see /dev/cu.* on macos
#on your host run:
#   socat TCP-LISTEN:5000,reuseaddr,fork,raw,echo=0 \
#         /dev/cu.usbserial-XXXXX,raw,echo=0
# expose it as /dev/ttyGPS inside the container:
socat PTY,link=/dev/ttyGPS,raw,echo=0 TCP:host.docker.internal:5000 &
exec "$@"
