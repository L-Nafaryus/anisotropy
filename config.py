import os, sys
from src import applogger

###
#   Paths
##
ROOT = os.getcwd()
sys.path.append(ROOT)

LOG = os.path.join(ROOT, "logs")
BUILD = os.path.join(ROOT, "build")

###
#   Logger
##
global logger
logger = applogger.Logger()

###
#   Utilities
##
class Parameters:
    """
    [
        "minSize",
        "maxSize",
        "growthRate",
        "nbSegPerEdge",
        "nbSegPerRadius",
        "chordalErrorEnabled",
        "chordalError",
        "secondOrder",
        "optimize",
        "quadAllowed",
        "useSurfaceCurvature",
        "fuseEdges",
        "checkChartBoundary"
    ]
    """
    def __init__(self, **kwargs):
        for (k, v) in kwargs.items():
            setattr(self, k, v)

class ViscousLayers(Parameters):
    """
    [
        "thickness",
        "numberOfLayers",
        "stretchFactor",
        "isFacesToIgnore",
        "facesToIgnore",
        "extrusionMethod"
    ]
    """
    pass

###
#   Project variables
##
structures = [
    "simple",
    "bodyCentered",
    "faceCentered"
]
class simple:
    theta = [c * 0.01 for c in range(1, 28 + 1)]
    directions = [
        [1, 0, 0],
        [0, 0, 1],
        [1, 1, 1]
    ]
    fillet = False
    fineness = 1
    parameters = Parameters(
        minSize = 0.0005,
        maxSize = 0.1,
        growthRate = 0.5,
        nbSegPerEdge = 0.5,
        nbSegPerRadius = 0.5,
        chordalErrorEnabled = False,
        chordalError = -1,
        secondOrder = False,
        optimize = True,
        quadAllowed = False,
        useSurfaceCurvature = True,
        fuseEdges = True,
        checkChartBoundary = False
    )
    viscousLayers = ViscousLayers(
        thickness = 0.001,
        numberOfLayers = 3,
        stretchFactor = 1.2,
        isFacesToIgnore = True,
        facesToIgnore = None,
        extrusionMethod = None
    )


class bodyCentered:
    theta = [c * 0.01 for c in range(1, 13 + 1)]
    directions = [
        [1, 0, 0],
        [0, 0, 1],
        [1, 1, 1]
    ]
    fillet = False
    fineness = 1
    parameters = Parameters(
        minSize = 0.0005,
        maxSize = 0.1,
        growthRate = 0.5,
        nbSegPerEdge = 0.5,
        nbSegPerRadius = 0.5,
        chordalErrorEnabled = False,
        chordalError = -1,
        secondOrder = False,
        optimize = True,
        quadAllowed = False,
        useSurfaceCurvature = True,
        fuseEdges = True,
        checkChartBoundary = False
    )
    viscousLayers = ViscousLayers(
        thickness = 0.001,
        numberOfLayers = 3,
        stretchFactor = 1.2,
        isFacesToIgnore = True,
        facesToIgnore = None,
        extrusionMethod = None
    )


class faceCentered:
    theta = [c * 0.01 for c in range(1, 18 + 1)]
    directions = [
        [1, 0, 0],
        [0, 0, 1],
        [1, 1, 1]
    ]
    fillet = False
    fineness = 1
    parameters = Parameters(
        minSize = 0.0005,
        maxSize = 0.1,
        growthRate = 0.5,
        nbSegPerEdge = 0.5,
        nbSegPerRadius = 0.5,
        chordalErrorEnabled = False,
        chordalError = -1,
        secondOrder = False,
        optimize = True,
        quadAllowed = False,
        useSurfaceCurvature = True,
        fuseEdges = True,
        checkChartBoundary = False
    )
    viscousLayers = ViscousLayers(
        thickness = 0.001,
        numberOfLayers = 3,
        stretchFactor = 1.2,
        isFacesToIgnore = True,
        facesToIgnore = None,
        extrusionMethod = None
    )

