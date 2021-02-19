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
Pore_0_1 = geompy.MakeCutList(geomObj_17, [geomObj_18], True)
geomObj_19 = geompy.MakeBoxDXDYDZ(2, 2, 2)
geomObj_20 = geompy.MakeTranslation(geomObj_19, 2, 0, 0)
geomObj_21 = geompy.MakeCommonList([Pore_0_1, geomObj_20], True)
geomObj_22 = geompy.MakeVertex(3, 1, 0)
geomObj_23 = geompy.MakeVertex(3, 1, 1)
geomObj_24 = geompy.MakeVector(geomObj_22, geomObj_23)
geomObj_25 = geompy.MakeRotation(geomObj_20, geomObj_24, 45*math.pi/180.0)
geomObj_26 = geompy.MakeVertex(3, 1, 0)
geomObj_27 = geompy.MakeVertex(2, 0, 0)
geomObj_28 = geompy.MakeVector(geomObj_26, geomObj_27)
geomObj_29 = geompy.MakeTranslationVectorDistance(geomObj_25, geomObj_28, 1)
geomObj_30 = geompy.MakeTranslation(geomObj_29, -0.5, 0.5, 0)
geomObj_31 = geompy.MakeCommonList([geomObj_21, geomObj_30], True)
geomObj_32 = geompy.MakeVertex(2, 2, 2)
geomObj_33 = geompy.MakeVertexWithRef(geomObj_32, 0, 0, 1)
geomObj_34 = geompy.MakeVector(geomObj_32, geomObj_33)
geomObj_35 = geompy.MakePlane(geomObj_32, geomObj_34, 5)
geomObj_36 = geompy.MakeCommonList([Pore_0_1, geomObj_35], True)
geomObj_37 = geompy.MakeTranslation(geomObj_35, 0, 0, -2)
geomObj_38 = geompy.MakeCommonList([Pore_0_1, geomObj_37], True)
geomObj_39 = geompy.CreateGroup(Pore_0_1, geompy.ShapeType["FACE"])
geompy.UnionIDs(geomObj_39, [2, 12, 22, 32])
geomObj_40 = geompy.CreateGroup(Pore_0_1, geompy.ShapeType["FACE"])
geompy.UnionIDs(geomObj_40, [2, 12, 22, 32])
geomObj_41 = geompy.CreateGroup(Pore_0_1, geompy.ShapeType["FACE"])
geompy.UnionIDs(geomObj_41, [3, 17, 28, 33, 42, 51, 56, 63, 72, 77, 90, 95, 102, 107, 117, 120, 129, 136, 142, 149, 156, 159, 162, 165])
geomObj_42 = geompy.CutListOfGroups([geomObj_41], [geomObj_39, geomObj_40])
geomObj_43 = geompy.MakeVectorDXDYDZ(1, 0, 0)
geomObj_44 = geompy.MakeVectorDXDYDZ(0, 1, 0)
geomObj_45 = geompy.MakeVectorDXDYDZ(0, 0, 1)
geomObj_46 = geompy.MakeBoxDXDYDZ(2.82842712474619, 2.82842712474619, 2)
geomObj_47 = geompy.MakeRotation(geomObj_46, geomObj_45, 45*math.pi/180.0)
geomObj_48 = geompy.MakeTranslation(geomObj_47, 2, 0, 0)
geomObj_49 = geompy.MakeVertex(2, 0, 0)
geomObj_50 = geompy.MakeVertex(2, 2, 0)
geomObj_51 = geompy.MakeVertex(2, 2, 2)
geomObj_52 = geompy.MakeLineTwoPnt(geomObj_50, geomObj_51)
geomObj_53 = geompy.MakeSpherePntR(geomObj_49, 1.111111111111111)
geomObj_54 = geompy.MakeMultiTranslation1D(geomObj_53, geomObj_44, 2, 3)
geomObj_55 = geompy.MakeCutList(geomObj_48, [geomObj_54], True)
geomObj_56 = geompy.MakeTranslation(geomObj_54, 0, 0, 2)
geomObj_57 = geompy.MakeCutList(geomObj_55, [geomObj_56], True)
geomObj_58 = geompy.MakeRotation(geomObj_54, geomObj_52, 90*math.pi/180.0)
geomObj_59 = geompy.MakeCutList(geomObj_57, [geomObj_58], True)
geomObj_60 = geompy.MakeTranslation(geomObj_58, 0, 0, 2)
geomObj_61 = geompy.MakeCutList(geomObj_59, [geomObj_60], True)
geomObj_62 = geompy.MakeBoxDXDYDZ(2, 2, 2)
geomObj_63 = geompy.MakeTranslation(geomObj_62, 2, 0, 0)
geomObj_64 = geompy.MakeCommonList([geomObj_61, geomObj_63], True)
geomObj_65 = geompy.MakeVertex(3, 1, 0)
geomObj_66 = geompy.MakeVertex(3, 1, 1)
geomObj_67 = geompy.MakeVector(geomObj_65, geomObj_66)
geomObj_68 = geompy.MakeRotation(geomObj_63, geomObj_67, 45*math.pi/180.0)
geomObj_69 = geompy.MakeVertex(3, 1, 0)
geomObj_70 = geompy.MakeVertex(2, 0, 0)
geomObj_71 = geompy.MakeVector(geomObj_69, geomObj_70)
geomObj_72 = geompy.MakeTranslationVectorDistance(geomObj_68, geomObj_71, 1)
geomObj_73 = geompy.MakeTranslation(geomObj_72, -0.5, 0.5, 0)
geomObj_74 = geompy.MakeCommonList([geomObj_64, geomObj_73], True)
geomObj_75 = geompy.MakeVertex(2, 2, 2)
geomObj_76 = geompy.MakeVertexWithRef(geomObj_75, 0, 0, 1)
geomObj_77 = geompy.MakeVector(geomObj_75, geomObj_76)
geomObj_78 = geompy.MakePlane(geomObj_75, geomObj_77, 5)
geomObj_79 = geompy.MakeCommonList([geomObj_61, geomObj_78], True)
geomObj_80 = geompy.MakeTranslation(geomObj_78, 0, 0, -2)
geomObj_81 = geompy.MakeCommonList([geomObj_61, geomObj_80], True)
geomObj_82 = geompy.CreateGroup(geomObj_61, geompy.ShapeType["FACE"])
geompy.UnionIDs(geomObj_82, [2, 12, 22, 32])
geomObj_83 = geompy.CreateGroup(geomObj_61, geompy.ShapeType["FACE"])
geompy.UnionIDs(geomObj_83, [2, 12, 22, 32])
geomObj_84 = geompy.CreateGroup(geomObj_61, geompy.ShapeType["FACE"])
geompy.UnionIDs(geomObj_84, [3, 17, 28, 33, 42, 51, 56, 63, 72, 77, 90, 95, 102, 107, 117, 120, 129, 136, 142, 149, 156, 159, 162, 165])
geomObj_85 = geompy.CutListOfGroups([geomObj_84], [geomObj_82, geomObj_83])
Vertex_1 = geompy.MakeVertex(2, 2, 2)
Vertex_2 = geompy.MakeVertexWithRef(Vertex_1, 0, 0, 1)
Vector_1 = geompy.MakeVector(Vertex_1, Vertex_2)
Plane_1 = geompy.MakePlane(Vertex_1, Vector_1, 5)
[geomObj_86] = geompy.SubShapeAll(Plane_1, geompy.ShapeType["FACE"])
[geomObj_87] = geompy.SubShapeAll(Plane_1, geompy.ShapeType["FACE"])
Common_1 = geompy.MakeCommonList([Pore_0_1, Plane_1], True)
[geomObj_88,geomObj_89,geomObj_90,geomObj_91,geomObj_92,geomObj_93,geomObj_94,geomObj_95,geomObj_96,geomObj_97,geomObj_98,geomObj_99,geomObj_100,geomObj_101,geomObj_102,geomObj_103] = geompy.SubShapeAll(Common_1, geompy.ShapeType["VERTEX"])
[geomObj_104,geomObj_105,geomObj_106,geomObj_107] = geompy.SubShapeAll(Common_1, geompy.ShapeType["FACE"])
[geomObj_108,geomObj_109,geomObj_110,geomObj_111] = geompy.SubShapeAll(Common_1, geompy.ShapeType["FACE"])
[geomObj_112,geomObj_113,geomObj_114,geomObj_115] = geompy.SubShapeAll(Common_1, geompy.ShapeType["FACE"])
[geomObj_116,geomObj_117,geomObj_118,geomObj_119] = geompy.SubShapeAll(Common_1, geompy.ShapeType["FACE"])
[geomObj_120,geomObj_121,geomObj_122,geomObj_123] = geompy.SubShapeAll(Common_1, geompy.ShapeType["FACE"])
geomObj_124 = geompy.GetInPlace(Common_1, Plane_1, True)
[geomObj_125,geomObj_126,geomObj_127,geomObj_128] = geompy.SubShapeAll(geomObj_124, geompy.ShapeType["FACE"])
geomObj_129 = geompy.GetInPlace(Pore_0_1, Common_1, True)
[geomObj_130,geomObj_131,geomObj_132,geomObj_133] = geompy.SubShapeAll(geomObj_129, geompy.ShapeType["FACE"])
geomObj_134 = geompy.GetInPlace(Pore_0_1, Common_1, True)
[geomObj_135,geomObj_136,geomObj_137,geomObj_138] = geompy.SubShapeAll(geomObj_134, geompy.ShapeType["FACE"])
Group_1 = geompy.CreateGroup(Pore_0_1, geompy.ShapeType["FACE"])
geompy.UnionIDs(Group_1, [28, 165, 72, 90])
geomObj_139 = geompy.GetInPlace(Pore_0_1, Common_1, True)
[geomObj_140,geomObj_141,geomObj_142,geomObj_143] = geompy.SubShapeAll(geomObj_139, geompy.ShapeType["FACE"])
[geomObj_144,geomObj_145,geomObj_146,geomObj_147] = geompy.SubShapeAll(geomObj_139, geompy.ShapeType["FACE"])
Group_2 = geompy.CreateGroup(Pore_0_1, geompy.ShapeType["FACE"])
geompy.UnionIDs(Group_2, [28, 165, 72, 90])
geompy.addToStudy( Pore_0_1, 'Pore 0.1' )
geompy.addToStudy( Vertex_1, 'Vertex_1' )
geompy.addToStudy( Vertex_2, 'Vertex_2' )
geompy.addToStudy( Vector_1, 'Vector_1' )
geompy.addToStudy( Plane_1, 'Plane_1' )
geompy.addToStudy( Common_1, 'Common_1' )
geompy.addToStudyInFather( Pore_0_1, Group_1, 'Group_1' )
geompy.addToStudyInFather( Pore_0_1, Group_2, 'Group_2' )

###
### SMESH component
###

import  SMESH, SALOMEDS
from salome.smesh import smeshBuilder

smesh = smeshBuilder.New()
#smesh.SetEnablePublish( False ) # Set to False to avoid publish in study if not needed or in some particular situations:
                                 # multiples meshes built in parallel, complex and numerous mesh edition (performance)

mesh_unv = smesh.CreateMeshesFromUNV(r'/home/nafaryus/projects/anisotrope-cube/build/simple-cubic/0.1/mesh.unv')
wall = mesh_unv.GetGroups()[ 0 ]
[ wall ] = mesh_unv.GetGroups()
mesh_unv_1 = smesh.CreateMeshesFromUNV(r'/home/nafaryus/projects/anisotrope-cube/build/simple-cubic/0.15/mesh.unv')
wall_1 = mesh_unv_1.GetGroups()[ 0 ]
[ wall_1 ] = mesh_unv_1.GetGroups()
mesh_unv_2 = smesh.CreateMeshesFromUNV(r'/home/nafaryus/projects/anisotrope-cube/build/simple-cubic/0.2/mesh.unv')
wall_2 = mesh_unv_2.GetGroups()[ 0 ]
[ wall_2 ] = mesh_unv_2.GetGroups()
Pore_0_1_1 = smesh.Mesh(Pore_0_1)
NETGEN_2D3D_1 = Pore_0_1_1.Tetrahedron(algo=smeshBuilder.NETGEN_1D2D3D)
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
NETGEN_Parameters.SetFineness( 3 )
NETGEN_Parameters.SetQuadAllowed( 0 )
ViscousLayers_0_025 = NETGEN_2D3D_1.ViscousLayers(0.025,5,1.1,[],1,smeshBuilder.NODE_OFFSET)
inlet = Pore_0_1_1.GroupOnGeom(__NOT__Published__Object__,'inlet',SMESH.FACE)
outlet = Pore_0_1_1.GroupOnGeom(__NOT__Published__Object__,'outlet',SMESH.FACE)
wall_3 = Pore_0_1_1.GroupOnGeom(__NOT__Published__Object__,'wall',SMESH.FACE)
isDone = Pore_0_1_1.Compute()
try:
  Pore_0_1_1.ExportUNV( r'asd/mesh.unv' )
  pass
except:
  print('ExportUNV() failed. Invalid file name?')
NETGEN_Parameters_1 = smesh.CreateHypothesis('NETGEN_Parameters', 'libNETGENEngine.so')
NETGEN_Parameters_1.SetSecondOrder( 0 )
NETGEN_Parameters_1.SetOptimize( 1 )
NETGEN_Parameters_1.SetChordalError( -1 )
NETGEN_Parameters_1.SetChordalErrorEnabled( 0 )
NETGEN_Parameters_1.SetUseSurfaceCurvature( 1 )
NETGEN_Parameters_1.SetFuseEdges( 1 )
NETGEN_Parameters_1.SetCheckChartBoundary( 0 )
NETGEN_Parameters_1.SetMinSize( 0.01 )
NETGEN_Parameters_1.SetMaxSize( 0.1 )
NETGEN_Parameters_1.SetFineness( 3 )
NETGEN_Parameters_1.SetQuadAllowed( 0 )
ViscousLayers_0_025_1 = smesh.CreateHypothesis('ViscousLayers')
ViscousLayers_0_025_1.SetTotalThickness( 0.025 )
ViscousLayers_0_025_1.SetNumberLayers( 5 )
ViscousLayers_0_025_1.SetStretchFactor( 1.1 )
ViscousLayers_0_025_1.SetFaces( [], 1 )
ViscousLayers_0_025_1.SetMethod( smeshBuilder.NODE_OFFSET )
try:
  pass
except:
  print('ExportUNV() failed. Invalid file name?')


## Set names of Mesh objects
smesh.SetName(wall, 'wall')
smesh.SetName(NETGEN_Parameters, 'NETGEN_Parameters')
smesh.SetName(NETGEN_Parameters_1, 'NETGEN_Parameters')
smesh.SetName(ViscousLayers_0_025, 'ViscousLayers=0.025,5,1.1,[],1')
smesh.SetName(ViscousLayers_0_025_1, 'ViscousLayers=0.025,5,1.1,[],1')
smesh.SetName(NETGEN_2D3D_1.GetAlgorithm(), 'NETGEN_2D3D_1')
smesh.SetName(mesh_unv.GetMesh(), 'mesh.unv')
smesh.SetName(Pore_0_1_1.GetMesh(), 'Pore 0.1')
smesh.SetName(mesh_unv_1.GetMesh(), 'mesh.unv')
smesh.SetName(mesh_unv_2.GetMesh(), 'mesh.unv')
smesh.SetName(wall_1, 'wall')
smesh.SetName(outlet, 'outlet')
smesh.SetName(wall_3, 'wall')
smesh.SetName(wall_2, 'wall')
smesh.SetName(inlet, 'inlet')


if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()
