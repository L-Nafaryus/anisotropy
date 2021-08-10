import logging

logger = logging.getLogger("anisotropy")

try:
    import GEOM
    from salome.geom import geomBuilder

except ImportError:
    logger.warning("Trying to get SALOME geometry modules outside SALOME environment. Modules won't be imported.")

if globals().get("geomBuilder"):
    geompy = geomBuilder.New()

else:
    geompy = None

def getGeom():
    return geompy


