import GEOM
from salome.geom import geomBuilder
geompy = geomBuilder.New()

import math

def create(alpha):
    axes = [
        geompy.MakeVectorDXDYDZ(1, 0, 0),
        geompy.MakeVectorDXDYDZ(0, 1, 0),
        geompy.MakeVectorDXDYDZ(0, 0, 1)
    ]

    box = geompy.MakeBoxDXDYDZ(2 * math.sqrt(2), 2 * math.sqrt(2), 2)
    box = geompy.MakeRotation(box, axes[2], 45 * math.pi / 180.0)
    box = geompy.MakeTranslation(box, 2, 0, 0)

    vtx = [
        geompy.MakeVertex(2, 0, 0),
        geompy.MakeVertex(2, 2, 0),
        geompy.MakeVertex(2, 2, 2)
    ]

    line = geompy.MakeLineTwoPnt(vtx[1], vtx[2])

    sphere = geompy.MakeSpherePntR(vtx[0], 1 / (1 - alpha))
    sphere = geompy.MakeMultiTranslation1D(sphere, axes[1], 2, 3)
    cut = geompy.MakeCutList(box, [sphere], True)

    sphere2 = geompy.MakeTranslation(sphere, 0, 0, 2)
    cut2 = geompy.MakeCutList(cut, [sphere2], True)

    sphere3 = geompy.MakeRotation(sphere, line, 90 * math.pi / 180.0)
    cut3 = geompy.MakeCutList(cut2, [sphere3], True)

    sphere4 = geompy.MakeTranslation(sphere3, 0, 0, 2)
    Pore = geompy.MakeCutList(cut3, [sphere4], True)


    box2 = geompy.MakeBoxDXDYDZ(2, 2, 2)
    box2 = geompy.MakeTranslation(box2, 2, 0, 0)
    Segment1_4 = geompy.MakeCommonList([Pore, box2], True)

    
    vec1 = geompy.MakeVector(geompy.MakeVertex(3, 1, 0), geompy.MakeVertex(3, 1, 1))
    box2 = geompy.MakeRotation(box2, vec1, 45*math.pi/180.0)
    vec2 = geompy.MakeVector(geompy.MakeVertex(3, 1, 0), geompy.MakeVertex(2, 0, 0))
    box2 = geompy.MakeTranslationVectorDistance(box2, vec2, 1)
    box2 = geompy.MakeTranslation(box2, -0.5, 0.5, 0)
    Segment1_8 = geompy.MakeCommonList([Segment1_4, box2], True)

    return Pore, Segment1_4, Segment1_8
