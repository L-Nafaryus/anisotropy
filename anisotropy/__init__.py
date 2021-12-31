# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

"""anisotropy

*anisotropy* is a ``Python`` package that is the result of science-research work 
on the anisotropy of permeability in the periodic porous media. 
"""

__license__ = "GPL3"
__version__ = "1.2.0"
__author__ = __maintainer__ = "George Kusayko"
__email__ = "gkusayko@gmail.com"
__repository__ = "https://github.com/L-Nafaryus/anisotropy"

###
#   Environment
##
from os import path, environ


PROJECT = path.abspath(path.dirname(__file__))
TMP = "/tmp/anisotropy"

env = {
    "PROJECT": path.abspath(path.dirname(__file__)),
    "TMP": TMP,
    "CWD": TMP,
    "BUILD_DIR": "build",
    "CONF_FILE": "anisotropy.toml",
    "LOG_FILE": "anisotropy.log",
    "DB_FILE": "anisotropy.db"
}


def loadEnv():
    prefix = "ANISOTROPY_"

    for k, v in env.items():
        environ[f"{ prefix }{ k }"] = v


del path, PROJECT, TMP
