try:
    import GEOM
    from salome.geom import geomBuilder

except ImportError:
    print("[Warning] Trying to get SALOME geometry modules outside SALOME environment. Modules won't be imported.")

if globals().get("geomBuilder"):
    geompy = geomBuilder.New()

else:
    geompy = None

def getGeom():
    return geompy


