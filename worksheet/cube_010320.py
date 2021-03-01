#!/usr/bin/env python

###
### This file is generated automatically by SALOME v9.6.0 with dump python functionality
###

import sys
import salome

salome.salome_init()
import salome_notebook
notebook = salome_notebook.NoteBook()
sys.path.insert(0, r'/home/nafaryus/projects/anisotrope-cube/worksheet')

###
### GEOM component
###

import GEOM
from salome.geom import geomBuilder
import math
import SALOMEDS


geompy = geomBuilder.New()

geomObj_1 = geompy.MakeVectorDXDYDZ(1, 0, 0)
geomObj_2 = geompy.MakeVectorDXDYDZ(0, 1, 0)
geomObj_3 = geompy.MakeVectorDXDYDZ(0, 0, 1)
geomObj_4 = geompy.MakeBoxDXDYDZ(2.82842712474619, 2.82842712474619, 2)
geomObj_5 = geompy.MakeRotation(geomObj_4, geomObj_3, 45*math.pi/180.0)
geomObj_6 = geompy.MakeTranslation(geomObj_5, 2, 0, 0)
geomObj_7 = geompy.MakeVertex(2, 0, 0)
geomObj_8 = geompy.MakeVertex(2, 2, 0)
geomObj_9 = geompy.MakeVertex(2, 2, 2)
geomObj_10 = geompy.MakeLineTwoPnt(geomObj_8, geomObj_9)
geomObj_11 = geompy.MakeSpherePntR(geomObj_7, 1.111111111111111)
geomObj_12 = geompy.MakeMultiTranslation1D(geomObj_11, geomObj_2, 2, 3)
geomObj_13 = geompy.MakeCutList(geomObj_6, [geomObj_12], True)
geomObj_14 = geompy.MakeTranslation(geomObj_12, 0, 0, 2)
geomObj_15 = geompy.MakeCutList(geomObj_13, [geomObj_14], True)
geomObj_16 = geompy.MakeRotation(geomObj_12, geomObj_10, 90*math.pi/180.0)
geomObj_17 = geompy.MakeCutList(geomObj_15, [geomObj_16], True)
geomObj_18 = geompy.MakeTranslation(geomObj_16, 0, 0, 2)
PORE = geompy.MakeCutList(geomObj_17, [geomObj_18], True)
geomObj_19 = geompy.MakeVertex(2, 2, 2)
geomObj_20 = geompy.MakeVertexWithRef(geomObj_19, 0, 0, 1)
geomObj_21 = geompy.MakeVector(geomObj_19, geomObj_20)
geomObj_22 = geompy.MakePlane(geomObj_19, geomObj_21, 5)
geomObj_23 = geompy.MakeCommonList([PORE, geomObj_22], True)
geomObj_24 = geompy.MakeTranslation(geomObj_22, 0, 0, -2)
geomObj_25 = geompy.MakeCommonList([PORE, geomObj_24], True)

inlet = geompy.CreateGroup(PORE, geompy.ShapeType["FACE"])
geomObj_26 = geompy.GetInPlace(PORE, geomObj_23, True)
[geomObj_27,geomObj_28,geomObj_29,geomObj_30] = geompy.SubShapeAll(geomObj_26, geompy.ShapeType["FACE"])
geompy.UnionList(inlet, [geomObj_27, geomObj_28, geomObj_29, geomObj_30])
outlet = geompy.CreateGroup(PORE, geompy.ShapeType["FACE"])
geomObj_31 = geompy.GetInPlace(PORE, geomObj_25, True)
[geomObj_32,geomObj_33,geomObj_34,geomObj_35] = geompy.SubShapeAll(geomObj_31, geompy.ShapeType["FACE"])
geompy.UnionList(outlet, [geomObj_32, geomObj_33, geomObj_34, geomObj_35])

geomObj_36 = geompy.CreateGroup(PORE, geompy.ShapeType["FACE"])
geompy.UnionIDs(geomObj_36, [3, 17, 28, 33, 42, 51, 56, 63, 72, 77, 90, 95, 102, 107, 117, 120, 129, 136, 142, 149, 156, 159, 162, 165])
wall = geompy.CutListOfGroups([geomObj_36], [inlet, outlet])

Fillet_1 = geompy.MakeFillet(PORE, 0.1, geompy.ShapeType["EDGE"], [24, 27, 35, 41, 48, 58, 82, 85, 89, 109, 114, 122, 128, 135, 140, 141, 148, 155])

inlet_1 = geompy.CreateGroup(Fillet_1, geompy.ShapeType["FACE"])
geompy.UnionIDs(inlet_1, [138, 37, 96, 269])
outlet_1 = geompy.CreateGroup(Fillet_1, geompy.ShapeType["FACE"])
geompy.UnionIDs(outlet_1, [64, 172, 126, 262])
wall_1 = geompy.CutListOfGroups([geomObj_37], [inlet_1, outlet_1])
geompy.addToStudy( PORE, 'PORE' )
geompy.addToStudyInFather( PORE, inlet, 'inlet' )
geompy.addToStudyInFather( PORE, outlet, 'outlet' )
geompy.addToStudyInFather( PORE, wall, 'wall' )
geompy.addToStudy( Fillet_1, 'Fillet_1' )
geompy.addToStudyInFather( Fillet_1, inlet_1, 'inlet' )
geompy.addToStudyInFather( Fillet_1, outlet_1, 'outlet' )
geompy.addToStudyInFather( Fillet_1, wall_1, 'wall' )

###
### SMESH component
###

import  SMESH, SALOMEDS
from salome.smesh import smeshBuilder

smesh = smeshBuilder.New()
#smesh.SetEnablePublish( False ) # Set to False to avoid publish in study if not needed or in some particular situations:
                                 # multiples meshes built in parallel, complex and numerous mesh edition (performance)

PORE_1 = smesh.Mesh(PORE)
NETGEN_2D3D_1 = PORE_1.Tetrahedron(algo=smeshBuilder.NETGEN_1D2D3D)
NETGEN_Parameters = NETGEN_2D3D_1.Parameters()
NETGEN_Parameters.SetSecondOrder( 0 )
NETGEN_Parameters.SetOptimize( 1 )
NETGEN_Parameters.SetChordalError( -1 )
NETGEN_Parameters.SetChordalErrorEnabled( 0 )
NETGEN_Parameters.SetUseSurfaceCurvature( 1 )
NETGEN_Parameters.SetFuseEdges( 1 )
NETGEN_Parameters.SetCheckChartBoundary( 0 )
NETGEN_Parameters.SetMinSize( 0.01 )
NETGEN_Parameters.SetMaxSize( 0.1 )
NETGEN_Parameters.SetFineness( 4 )
NETGEN_Parameters.SetQuadAllowed( 0 )
ViscousLayers_0_025 = NETGEN_2D3D_1.ViscousLayers(0.025,2,1.1,[],1,smeshBuilder.NODE_OFFSET)
inlet_2 = PORE_1.GroupOnGeom(inlet,'inlet',SMESH.FACE)
outlet_2 = PORE_1.GroupOnGeom(outlet,'outlet',SMESH.FACE)
wall_2 = PORE_1.GroupOnGeom(wall,'wall',SMESH.FACE)
isDone = PORE_1.Compute()
try:
  PORE_1.ExportUNV( r'asd/mesh.unv' )
  pass
except:
  print('ExportUNV() failed. Invalid file name?')
NETGEN_Parameters.SetFineness( 3 )
Mesh_1 = smesh.Mesh(Fillet_1)
status = Mesh_1.AddHypothesis(NETGEN_Parameters)
status = Mesh_1.AddHypothesis(ViscousLayers_0_025)
NETGEN_2D3D_1_1 = Mesh_1.Tetrahedron(algo=smeshBuilder.NETGEN_1D2D3D)
inlet_3 = Mesh_1.GroupOnGeom(inlet_1,'inlet',SMESH.FACE)
outlet_3 = Mesh_1.GroupOnGeom(outlet_1,'outlet',SMESH.FACE)
wall_3 = Mesh_1.GroupOnGeom(wall_1,'wall',SMESH.FACE)
ViscousLayers_0_025.SetTotalThickness( 0.05 )
ViscousLayers_0_025.SetNumberLayers( 2 )
ViscousLayers_0_025.SetStretchFactor( 1.1 )
ViscousLayers_0_025.SetMethod( smeshBuilder.SURF_OFFSET_SMOOTH )
ViscousLayers_0_025.SetFaces( [], 1 )
isDone = Mesh_1.Compute()
[ inlet_3, outlet_3, wall_3 ] = Mesh_1.GetGroups()
try:
  Mesh_1.ExportUNV( r'/home/nafaryus/projects/anisotrope-cube/build/simple-cubic/0.1/mesh.unv' )
  pass
except:
  print('ExportUNV() failed. Invalid file name?')


## Set names of Mesh objects
smesh.SetName(NETGEN_2D3D_1.GetAlgorithm(), 'NETGEN_2D3D_1')
smesh.SetName(ViscousLayers_0_025, 'ViscousLayers=0.025,2,1.1,[],1')
smesh.SetName(NETGEN_Parameters, 'NETGEN_Parameters')
smesh.SetName(inlet_2, 'inlet')
smesh.SetName(outlet_2, 'outlet')
smesh.SetName(wall_2, 'wall')
smesh.SetName(PORE_1.GetMesh(), 'PORE')
smesh.SetName(Mesh_1.GetMesh(), 'Mesh_1')
smesh.SetName(wall_3, 'wall')
smesh.SetName(outlet_3, 'outlet')
smesh.SetName(inlet_3, 'inlet')


if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()
