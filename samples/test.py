import salome
salome.salome_init()

import GEOM
from salome.geom import geomBuilder
geompy = geomBuilder.New()

from math import pi, sqrt

def simpleCubic(theta = 0.01, fillet = False):
    
    ###
    #   Parameters
    ##
    r0 = 1.0
    L = 2 * r0

    radius = r0 / (1 - theta)
    xn, yn, zn = 3, 3, 3 
    
    length = L * sqrt(2)
    width = L * sqrt(2)
    height = L

    ###
    #   Bounding box
    ##
    # YZ 
    sk = geompy.Sketcher3D()
    sk.addPointsAbsolute(width, 0, 0)
    sk.addPointsAbsolute(0, length, 0)
    sk.addPointsAbsolute(0, length, height)
    sk.addPointsAbsolute(width, 0, height)
    sk.addPointsAbsolute(width, 0, 0)
    
    inletface = geompy.MakeFaceWires([sk.wire()], True)
    vecflow = geompy.GetNormal(inletface)
    cubic = geompy.MakePrismVecH(inletface, vecflow, width)

    faces = geompy.ExtractShapes(cubic, geompy.ShapeType["FACE"], False)
    symetryface = []

    for face in faces:
        norm = geompy.GetNormal(face)
        angle = round(geompy.GetAngle(norm, vecflow), 0)

        if (angle == 0 or angle == 180) and not face == inletface:
            outletface = face
        
        else:
            symetryface.append(face)
    
    ###
    #   Grains
    ##
    ox = geompy.MakeVectorDXDYDZ(1, 0, 0)
    oy = geompy.MakeVectorDXDYDZ(0, 1, 0)
    oz = geompy.MakeVectorDXDYDZ(0, 0, 1)

    grain = geompy.MakeSphereR(radius)
    lattice = geompy.MakeMultiTranslation2D(grain, ox, L, xn, oy, L, yn)
    lattice = geompy.MakeMultiTranslation1D(grains, oz, L, zn)
    
    grains = geompy.ExtractShapes(lattice, geompy.ShapeType["SOLID"], True)
    grains = geompy.MakeFuseList(grains, False, False)

    grains = grains

    ###
    #   Groups
    ##
    shape = geompy.MakeCutList(cubic, [grains])

    sall = geompy.CreateGroup(shape, geompy.ShapeType["FACE"])
    geompy.UnionIDs(sall,
        geompy.SubShapeAllIDs(shape, geompy.ShapeType["FACE"]))

    inlet = geompy.CreateGroup(shape, geompy.ShapeType["FACE"], "inlet")
    inletshape = geompy.MakeCutList(inletface, [grains])
    geompy.UnionList(inlet,
        geompy.SubShapeAll(geompy.GetInPlace(shape, inletshape, True), 
            geompy.ShapeType["FACE"]))



    wall = geompy.CutListOfGroups([sall], [], "wall")
    
