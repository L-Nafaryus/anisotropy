import salome
salome.salome_init()

import GEOM
from salome.geom import geomBuilder
geompy = geomBuilder.New()

import SMESH, SALOMEDS
from salome.smesh import smeshBuilder
smesh = smeshBuilder.New()

import math

axes = [
    geompy.MakeVectorDXDYDZ(1, 0, 0),
    geompy.MakeVectorDXDYDZ(0, 1, 0),
    geompy.MakeVectorDXDYDZ(0, 0, 1)
]

vtx = [
    geompy.MakeVertex(1 / math.sqrt(2), -1 / math.sqrt(2), 0.5),
    geompy.MakeVertex(-1 / math.sqrt(2), 1 / math.sqrt(2), -0.5),
    geompy.MakeVertex(-1, -1, -0.5),
    geompy.MakeVertex(-0.5, -0.5, 0)
]

box = geompy.MakeBoxTwoPnt(vtx[0], vtx[1])
box = geompy.MakeRotation(box, axes[2], 45 * math.pi / 180.0)

#alpha = [ x * 0.01 for x in range(1, 28 + 1) ]
alpha=[0.15]

#for coef in alpha:
spheres = geompy.MakeSpherePntR(vtx[2], math.sqrt(3) / 4 / (1 - alpha[0]))
spheres = geompy.MakeMultiTranslation2D(spheres, axes[0], 1, 3, axes[1], 1, 3)
spheres = geompy.MakeMultiTranslation1D(spheres, axes[2], 1, 2)

spheres2 = geompy.MakeSpherePntR(vtx[3], math.sqrt(3) / 4 / (1 - alpha[0]))
spheres2 = geompy.MakeMultiTranslation2D(spheres2, axes[0], 1, 3, axes[1], 1, 3)

Pore = geompy.MakeCutList(box, [spheres, spheres2], False)

geompy.addToStudy(Pore, 'Pore')

box2 = geompy.MakeBoxTwoPnt(vtx[0], geompy.MakeVertex(0, 0, 0))
box2 = geompy.MakeRotation(box2, axes[2], 45 * math.pi / 180.0)
Segment1_8 = geompy.MakeCommonList([Pore, box2], True)

geompy.addToStudy(Segment1_8, 'Segment1_8')

if salome.sg.hasDesktop():
    salome.sg.updateObjBrowser()

