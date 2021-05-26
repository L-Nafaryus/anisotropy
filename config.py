import os, sys
from anisotropy.utils import Logger, struct

PROJECT = "anisotropy"
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
logger = Logger(PROJECT, os.path.join(LOG, f"{ PROJECT }.log"))

###
#   Project variables
##
structures = [
    "simple",
    #"bodyCentered",
    #"faceCentered"
]

simple = struct(
    theta = [0.01, 0.02], #[c * 0.01 for c in range(1, 28 + 1)],
    directions = [
        [1, 0, 0],
        [0, 0, 1],
        [1, 1, 1]
    ],
    fillet = True,
    fineness = 3,
    parameters = struct(
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
    ),
    viscousLayers = struct(
        thickness = 0.005, # 0.01, 0.005 for 0.28, 0.01 for prism
        numberOfLayers = 2,
        stretchFactor = 1.2,
        isFacesToIgnore = True,
        facesToIgnore = None,
        extrusionMethod = None
    )
)

bodyCentered = struct(
    theta = [c * 0.01 for c in range(1, 18 + 1)],
    directions = [
        [1, 0, 0],
        [0, 0, 1],
        [1, 1, 1]
    ],
    fillet = True, 
    fineness = 3,
    parameters = struct(
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
    ),
    viscousLayers = struct(
        thickness = 0.005,
        numberOfLayers = 2,
        stretchFactor = 1.2,
        isFacesToIgnore = True,
        facesToIgnore = None,
        extrusionMethod = None
    )
)

faceCentered = struct(
    theta = [0.06, 0.13], #[c * 0.01 for c in range(1, 13 + 1)]
    directions = [
        #[1, 0, 0],
        #[0, 0, 1],
        [1, 1, 1]
    ],
    fillet = True, 
    fineness = 3,
    parameters = struct(
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
    ),
    viscousLayers = struct(
        thickness = 0.001, # Failing on 0.13-111
        numberOfLayers = 2,
        stretchFactor = 1.2,
        isFacesToIgnore = True,
        facesToIgnore = None,
        extrusionMethod = None
    )
)
