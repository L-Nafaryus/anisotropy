#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ "$1" = "clean" ]; then
    git clean -fdx
    exit 0
fi

python ${DIR}/anisotropy/anisotropy.py
