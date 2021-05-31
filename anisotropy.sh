#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ "$1" = "clean" ]; then
    git clean -fdx
    exit 0

elif [ "$1" = "init" ]; then
    python -m venv env
    source env/bin/activate
    python -m pip install --upgrade pip
    python -m pip install requirements.txt

elif [ "$1" = "run" ]; then
    source ${OPENFOAM}
    python ${DIR}/anisotropy/anisotropy.py

fi
