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
    geompy.MakeVectorDXDYDZ(0, 0, 1),
    geompy.MakeVectorDXDYDZ(1, 1, 0),
    geompy.MakeVectorDXDYDZ(1, -1, 0)
]

vtx = [
    geompy.MakeVertex(0, 0, -0.5),
    geompy.MakeVertex(1 / math.sqrt(2), 1 / math.sqrt(2), 0.5),
    geompy.MakeVertex(0.5, 0, 0),
    geompy.MakeVertex(0.5 / math.sqrt(2), 0.5 / math.sqrt(2), 0.5)
]

box = geompy.MakeBoxTwoPnt(vtx[0], vtx[1])
box = geompy.MakeRotation(box, axes[2], -45 * math.pi / 180.0)

#alpha = [ x * 0.01 for x in range(1, 28 + 1) ]
alpha=[0.08]

#for coef in alpha:
spheres = geompy.MakeSpherePntR(vtx[0], math.sqrt(2) / 4 / (1 - alpha[0]))
spheres = geompy.MakeMultiTranslation2D(spheres, axes[3], 1 / math.sqrt(2), 2, axes[4], 1 / math.sqrt(2), 2)
spheres = geompy.MakeMultiTranslation1D(spheres, axes[2], 1, 2)

sphere2 = geompy.MakeSpherePntR(vtx[2], math.sqrt(2) / 4 / (1 - alpha[0]))

PoreFC = geompy.MakeCutList(box, [spheres, sphere2], True)

geompy.addToStudy(PoreFC, 'PoreFC')

box2 = geompy.MakeBoxTwoPnt(geompy.MakeVertex(0, 0, 0), vtx[3])
box2 = geompy.MakeRotation(box2, axes[2], -45 * math.pi / 180.0)
Segment1_8 = geompy.MakeCommonList([PoreFC, box2], True)

geompy.addToStudy(Segment1_8, 'Segment1_8')

mesh = smesh.Mesh(PoreFC)
netgen = mesh.Tetrahedron(algo=smeshBuilder.NETGEN_1D2D3D)

param = netgen.Parameters()
param.SetSecondOrder( 0 )
param.SetOptimize( 1 )
param.SetChordalError( -1 )
param.SetChordalErrorEnabled( 0 )
param.SetUseSurfaceCurvature( 1 )
param.SetFuseEdges( 1 )
param.SetCheckChartBoundary( 0 )
param.SetMinSize( 0.01 )
param.SetMaxSize( 0.02 )
param.SetFineness( 5 )
param.SetGrowthRate( 0.1 )
param.SetNbSegPerEdge( 5 )
param.SetNbSegPerRadius( 10 )
param.SetQuadAllowed( 1 )

#vlayer = netgen.ViscousLayers(0.05, 3, 1.5, [15, 29, 54], 1, smeshBuilder.SURF_OFFSET_SMOOTH)

isDone = mesh.Compute()

if not isDone:
    print("Mesh is not computed")


if salome.sg.hasDesktop():
    salome.sg.updateObjBrowser()
