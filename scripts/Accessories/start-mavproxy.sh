#!/bin/bash

PATH="$PATH:$HOME/.local/bin"

mavproxy.py --master=$MAVPROXY_MASTER_IP --out=$OUT_IP_ONE --out=$OUT_IP_TWO --out=$OUT_IP_THREE