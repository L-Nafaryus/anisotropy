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
    #"simple",
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
    fillet = True
    fineness = 3
    parameters = Parameters(
        minSize = 0.01,
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
        thickness = 0.005, # 0.01, 0.005 for 0.28, 0.01 for prism
        numberOfLayers = 2,
        stretchFactor = 1.2,
        isFacesToIgnore = True,
        facesToIgnore = None,
        extrusionMethod = None
    )


class bodyCentered:
    theta = [c * 0.01 for c in range(1, 18 + 1)]
    directions = [
        [1, 0, 0],
        [0, 0, 1],
        [1, 1, 1]
    ]
    fillet = True 
    fineness = 3
    parameters = Parameters(
        minSize = 0.005,
        maxSize = 0.05,
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
        thickness = 0.005,
        numberOfLayers = 2,
        stretchFactor = 1.2,
        isFacesToIgnore = True,
        facesToIgnore = None,
        extrusionMethod = None
    )


class faceCentered:
    theta = [0.06, 0.13] #[c * 0.01 for c in range(1, 13 + 1)]
    directions = [
        #[1, 0, 0],
        #[0, 0, 1],
        [1, 1, 1]
    ]
    fillet = True 
    fineness = 3
    parameters = Parameters(
        minSize = 0.005,
        maxSize = 0.05,
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
        thickness = 0.001, # Failing on 0.13-111
        numberOfLayers = 2,
        stretchFactor = 1.2,
        isFacesToIgnore = True,
        facesToIgnore = None,
        extrusionMethod = None
    )

