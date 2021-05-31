#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/.."
cd ${DIR}

if [ "$1" = "clean" ]; then
    git clean -fdx

elif [ "$1" = "init" ]; then
    python -m venv env
    source env/bin/activate
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    deactivate

elif [ "$1" = "run" ]; then
    source ${OPENFOAM}
    source env/bin/activate
    python ${DIR}/anisotropy/anisotropy.py
    deactivate

fi
