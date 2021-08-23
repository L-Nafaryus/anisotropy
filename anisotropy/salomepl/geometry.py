# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import logging

logger = logging.getLogger("anisotropy")

try:
    import GEOM
    from salome.geom import geomBuilder

except ImportError:
    logger.debug("Trying to get SALOME geometry modules outside SALOME environment. Modules won't be imported.")

if globals().get("geomBuilder"):
    geompy = geomBuilder.New()

else:
    geompy = None

def getGeom():
    return geompy


