#!/bin/bash

if [[ $# -ne 3 ]]; then
    printf "Usage: $0 <device-type> <device-id> <action>\nSee switch-gpio-state.py for details.\n"
    exit 2
fi

docker run --network=host --rm switch-gpio-state $1 $2 $3 

