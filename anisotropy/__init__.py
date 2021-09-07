# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

"""anisotropy

*anisotropy* is a ``Python`` package that is the result of science-research work 
on the anisotropy of permeability in the periodic porous media. 
A project uses own wrappers around external applications 
for constructing a shapes and meshes (``Salome``) and computing a flow (``OpenFOAM``).
"""

__license__ = "GPL3"
__version__ = "1.3.0"
__author__ = __maintainer__ = "George Kusayko"
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
    CONFIG = os.path.join(env["ROOT"], "anisotropy/config/default.toml"),
    DOCS = os.path.join(env["ROOT"], "docs")
)
env.update(
    logger_name = "anisotropy",
    db_name = "anisotropy",
    db_path = env["BUILD"],
    salome_timeout = 15 * 60,
    openfoam_template = os.path.join(env["ROOT"], "anisotropy/openfoam/template")
)

del os
