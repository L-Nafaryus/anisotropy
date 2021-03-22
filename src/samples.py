from . import geometry_utils
import GEOM

from . import mesh_utils
import SMESH

from . import anisotropeCubic
import salome
import math

def simpleCubic(theta, flowdirection):
    radius = 1
    stackAngle = [0.5 * math.pi, 0.5 * math.pi, 0.5 * math.pi]
    theta = theta if theta else 0.1
    layers = [3, 3, 3]
    grains = anisotropeCubic.StructuredGrains(radius, stackAngle, theta, layers)
    
    scale = [2 * math.sqrt(2), 2 * math.sqrt(2), 2]
    flowdirection = flowdirection if flowdirection else [1, 0, 0]
    style = 0
    cubic = anisotropeCubic.AnisotropeCubic(scale, grains, style)
    boundary = geometry_utils.boundaryCreate(cubic, flowdirection, grains)
    
    fineness = 3
    mesh = mesh_utils.meshCreate(cubic, boundary, fineness)
    mesh_utils.meshCompute(mesh)


def bodyCenteredCubic(theta, flowdirection):
    radius = 1
    stackAngle = [0.5 * math.pi, 0.25 * math.pi, 0.25 * math.pi]
    theta = theta if theta else 0.1
    layers = [3, 3, 3]
    grains = anisotropeCubic.StructuredGrains(radius, stackAngle, theta, layers)
    
    scale = [2 / math.sqrt(2), 2 / math.sqrt(2), 1]
    flowdirection = flowdirection if flowdirection else [1, 0, 0]
    style = 0
    cubic = anisotropeCubic.AnisotropeCubic(scale, grains, style)
    boundary = geometry_utils.boundaryCreate(cubic, flowdirection, grains)
    
    fineness = 3
    mesh = mesh_utils.meshCreate(cubic, boundary, fineness)
    mesh_utils.meshCompute(mesh)


def faceCenteredCubic(theta, flowdirection):
    radius = 1
    stackAngle = [0.5 * math.pi, 0.5 * math.pi, 0.5 * math.pi]
    theta = theta if theta else 0.1
    layers = [3, 3, 3]
    grains = anisotropeCubic.StructuredGrains(radius, stackAngle, theta, layers)
    
    scale = [1 / math.sqrt(2), 1 / math.sqrt(2), 1]
    flowdirection = flowdirection if flowdirection else [1, 0, 0]
    style = 0
    cubic = anisotropeCubic.AnisotropeCubic(scale, grains, style)
    boundary = geometry_utils.boundaryCreate(cubic, flowdirection, grains)
    
    fineness = 3
    mesh = mesh_utils.meshCreate(cubic, boundary, fineness)
    mesh_utils.meshCompute(mesh)


def genMesh(ctype, theta, flowdirection):
    salome.salome_init()


    salome.salome_close()