# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

"""anisotropy
"""

__license__ = "GPL3"
__version__ = "1.1.0"
__author__ = __maintainer = "George Kusayko"
__email__ = "gkusayko@gmail.com"

###
#   Environment
##
import os

env = dict(
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)
env.update(
    BUILD = os.path.join(env["ROOT"], "build"),
    LOG = os.path.join(env["ROOT"], "logs"),
    CONFIG = os.path.join(env["ROOT"], "anisotropy/config/default.toml")
)
env.update(
    logger_name = "anisotropy",
    db_path = env["BUILD"],
    salome_port = 2810,
    openfoam_template = os.path.join(env["ROOT"], "anisotropy/openfoam/template")
)

del os
