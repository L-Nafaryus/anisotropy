import GEOM
from salome.geom import geomBuilder
geompy = geomBuilder.New()

import math

def create(alpha):
    # xyz axes
    axes = [
        geompy.MakeVectorDXDYDZ(1, 0, 0),
        geompy.MakeVectorDXDYDZ(0, 1, 0),
        geompy.MakeVectorDXDYDZ(0, 0, 1)
    ]
    
    # Main box
    box = geompy.MakeBoxDXDYDZ(2 * math.sqrt(2), 2 * math.sqrt(2), 2)
    box = geompy.MakeRotation(box, axes[2], 45 * math.pi / 180.0)
    box = geompy.MakeTranslation(box, 2, 0, 0)
    
    vtx = [
        geompy.MakeVertex(2, 0, 0),
        geompy.MakeVertex(2, 2, 0),
        geompy.MakeVertex(2, 2, 2)
    ]
    
    line = geompy.MakeLineTwoPnt(vtx[1], vtx[2])
    
    # Spheres for cutting
    sphere = geompy.MakeSpherePntR(vtx[0], 1 / (1 - alpha))
    sphere = geompy.MakeMultiTranslation1D(sphere, axes[1], 2, 3)
    cut = geompy.MakeCutList(box, [sphere], True)
    
    sphere2 = geompy.MakeTranslation(sphere, 0, 0, 2)
    cut2 = geompy.MakeCutList(cut, [sphere2], True)
    
    sphere3 = geompy.MakeRotation(sphere, line, 90 * math.pi / 180.0)
    cut3 = geompy.MakeCutList(cut2, [sphere3], True)
    
    sphere4 = geompy.MakeTranslation(sphere3, 0, 0, 2)
    
    # Main geometry
    Pore = geompy.MakeCutList(cut3, [sphere4], True)
    geompy.addToStudy(Pore, "PORE")

    #
    #   D /\ B  A(1, 1, 0)  \vec{n}(1, 1, 0)
    #    /  \   B(3, 3, 0)  \vec{n}(1, 1, 0)
    #    \  /   C(3, 1, 0)  \vec{n}(-1, 1, 0)
    #   A \/ C  D(1, 3, 0)  \vec{n}(-1, 1, 0)
    #

    # Prepare faces
    vtx.append(geompy.MakeVertex(2, 2, 2))
    vtx.append(geompy.MakeVertexWithRef(vtx[3], 0, 0, 1))
    vec2 = geompy.MakeVector(vtx[3], vtx[4])
    plane = geompy.MakePlane(vtx[3], vec2, 5)
    common1 = geompy.MakeCommonList([Pore, plane], True)
    plane = geompy.MakeTranslation(plane, 0, 0, -2)
    common2 = geompy.MakeCommonList([Pore, plane], True)
    
    # TODO: make 4 planes A B C D
    Pore = geompy.MakeFillet(Pore, 0.1, geompy.ShapeType["EDGE"], [24, 27, 35])


    # Main groups (inlet, outlet, wall)
    inlet = geompy.CreateGroup(Pore, geompy.ShapeType["FACE"])
    gip = geompy.GetInPlace(Pore, common1, True)
    faces = geompy.SubShapeAll(gip, geompy.ShapeType["FACE"])
    geompy.UnionList(inlet, faces)
    
    outlet = geompy.CreateGroup(Pore, geompy.ShapeType["FACE"])
    gip = geompy.GetInPlace(Pore, common2, True)
    faces = geompy.SubShapeAll(gip, geompy.ShapeType["FACE"]) 
    geompy.UnionList(outlet, faces)
    
    PoreGroup = geompy.CreateGroup(Pore, geompy.ShapeType["FACE"])
    faces = geompy.SubShapeAllIDs(Pore, geompy.ShapeType["FACE"]) 
    geompy.UnionIDs(PoreGroup, faces)
    
    wall = geompy.CutListOfGroups([PoreGroup], [inlet, outlet])
    
    
    return Pore, [inlet, outlet, wall]
