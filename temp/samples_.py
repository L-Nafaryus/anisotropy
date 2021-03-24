from src import geometry_utils
import GEOM

from src import mesh_utils
import SMESH

from src import anisotropeCubic
import salome
import math

import samples

def genMesh(ctype, theta, flowdirection):
    _G = globals()
    
    #for g in _G:
    func = _G.get(ctype)

    if func:
        salome.salome_init()
        func(theta, flowdirection)
        salome.salome_close()

    else:
        raise Exception("Unknown type of the sample function")


def simpleCubic(theta, flowdirection):
    #radius = 1
    #stackAngle = [0.5 * math.pi, 0.5 * math.pi, 0.5 * math.pi]
    theta = theta if theta else 0.1
    #layers = [3, 3, 3]
    #grains = anisotropeCubic.StructuredGrains(radius, stackAngle, theta, layers)
    
    #scale = [2 * math.sqrt(2), 2 * math.sqrt(2), 2]
    flowdirection = flowdirection if flowdirection else [1, 0, 0]
    #style = 0
    #cubic = anisotropeCubic.AnisotropeCubic(scale, grains, style)
    grains, cubic, _ = samples.simpleCubic(theta)
    boundary = geometry_utils.boundaryCreate(cubic, flowdirection, grains)
    
    fineness = 3
    mesh = mesh_utils.meshCreate(cubic, boundary, fineness)
    mesh_utils.meshCompute(mesh)


def bodyCenteredCubic(theta, flowdirection):
    #radius = 1
    #stackAngle = [0.5 * math.pi, 0.25 * math.pi, 0.25 * math.pi]
    theta = theta if theta else 0.1
    #layers = [3, 3, 3]
    #grains = anisotropeCubic.StructuredGrains(radius, stackAngle, theta, layers)
    
    #scale = [2 / math.sqrt(2), 2 / math.sqrt(2), 1]
    flowdirection = flowdirection if flowdirection else [1, 0, 0]
    #style = 0
    #cubic = anisotropeCubic.AnisotropeCubic(scale, grains, style)
    grains, cubic, _ = samples.bodyCenteredCubic(theta)
    boundary = geometry_utils.boundaryCreate(cubic, flowdirection, grains)
    
    fineness = 3
    mesh = mesh_utils.meshCreate(cubic, boundary, fineness)
    mesh_utils.meshCompute(mesh)


def faceCenteredCubic(theta, flowdirection):
    #radius = 1
    #stackAngle = [0.5 * math.pi, 0.5 * math.pi, 0.5 * math.pi]
    theta = theta if theta else 0.1
    #layers = [3, 3, 3]
    #grains = anisotropeCubic.StructuredGrains(radius, stackAngle, theta, layers)
    
    #scale = [1 / math.sqrt(2), 1 / math.sqrt(2), 1]
    flowdirection = flowdirection if flowdirection else [1, 0, 0]
    #style = 0
    #cubic = anisotropeCubic.AnisotropeCubic(scale, grains, style)
    grains, cubic, _ = samples.faceCenteredCubic(theta)
    boundary = geometry_utils.boundaryCreate(cubic, flowdirection, grains)
    
    fineness = 3
    mesh = mesh_utils.meshCreate(cubic, boundary, fineness)
    mesh_utils.meshCompute(mesh)


