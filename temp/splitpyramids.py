#!/usr/bin/env python

###
### This file is generated automatically by SALOME v9.6.0 with dump python functionality
###

import sys
import salome

salome.salome_init()
import salome_notebook
notebook = salome_notebook.NoteBook()
sys.path.insert(0, r'/home/nafaryus/projects/anisotrope-cube/temp')

###
### GEOM component
###

import GEOM
from salome.geom import geomBuilder
import math
import SALOMEDS


geompy = geomBuilder.New()

geomObj_1 = geompy.MakeVertex(0, 0, 0)

sk = geompy.Sketcher3D()
sk.addPointsAbsolute(-0.6666667, -0.6666667, -0.1666667)
sk.addPointsAbsolute(-0.3333333, -0.8333333, -0.3333333)
sk.addPointsAbsolute(-0.1666667, -0.6666667, -0.6666667)
sk.addPointsAbsolute(-0.3333333, -0.3333333, -0.8333333)
sk.addPointsAbsolute(-0.6666667, -0.1666667, -0.6666667)
sk.addPointsAbsolute(-0.8333333, -0.3333333, -0.3333333)
sk.addPointsAbsolute(-0.6666667, -0.6666667, -0.1666667)
geomObj_2 = sk.wire()
geomObj_3 = geompy.MakeFaceWires([geomObj_2], 0)
geomObj_4 = geompy.GetNormal(geomObj_3)
geomObj_5 = geompy.MakePrismVecH(geomObj_3, geomObj_4, 1.732050807568877)
geomObj_6 = geompy.MakeScaleTransform(geomObj_3, geomObj_1, 100)
geomObj_7 = geompy.MakeScaleTransform(geomObj_5, geomObj_1, 100)
[geomObj_8,geomObj_9,geomObj_10,geomObj_11,geomObj_12,geomObj_13,geomObj_14,geomObj_15] = geompy.ExtractShapes(geomObj_7, geompy.ShapeType["FACE"], False)
geomObj_16 = geompy.GetNormal(geomObj_8)
geomObj_17 = geompy.GetNormal(geomObj_9)
geomObj_18 = geompy.GetNormal(geomObj_10)
geomObj_19 = geompy.GetNormal(geomObj_11)
geomObj_20 = geompy.GetNormal(geomObj_12)
geomObj_21 = geompy.GetNormal(geomObj_13)
geomObj_22 = geompy.GetNormal(geomObj_14)
geomObj_23 = geompy.GetNormal(geomObj_15)
geomObj_24 = geompy.MakeVectorDXDYDZ(1, 0, 0)
geomObj_25 = geompy.MakeVectorDXDYDZ(0, 1, 0)
geomObj_26 = geompy.MakeVectorDXDYDZ(0, 0, 1)
geomObj_27 = geompy.MakeVectorDXDYDZ(1, 1, 0)
geomObj_28 = geompy.MakeVectorDXDYDZ(1, -1, 0)
geomObj_29 = geompy.MakeVertex(-1, 0, -0.5)
geomObj_30 = geompy.MakeSpherePntR(geomObj_29, 0.3761206282907168)
geomObj_31 = geompy.MakeMultiTranslation2D(geomObj_30, geomObj_27, 0.7071067811865476, 3, geomObj_28, 0.7071067811865476, 3)
geomObj_32 = geompy.MakeMultiTranslation1D(geomObj_31, geomObj_26, 1, 2)
[geomObj_33,geomObj_34,geomObj_35,geomObj_36,geomObj_37,geomObj_38,geomObj_39,geomObj_40,geomObj_41,geomObj_42,geomObj_43,geomObj_44,geomObj_45,geomObj_46,geomObj_47,geomObj_48,geomObj_49,geomObj_50] = geompy.ExtractShapes(geomObj_32, geompy.ShapeType["SOLID"], True)
geomObj_51 = geompy.MakeVertex(-1.5, 0, -1)
geomObj_52 = geompy.MakeSpherePntR(geomObj_51, 0.3761206282907168)
geomObj_53 = geompy.MakeMultiTranslation2D(geomObj_52, geomObj_27, 0.7071067811865476, 4, geomObj_28, 0.7071067811865476, 4)
geomObj_54 = geompy.MakeMultiTranslation1D(geomObj_53, geomObj_26, 1, 3)
[geomObj_55,geomObj_56,geomObj_57,geomObj_58,geomObj_59,geomObj_60,geomObj_61,geomObj_62,geomObj_63,geomObj_64,geomObj_65,geomObj_66,geomObj_67,geomObj_68,geomObj_69,geomObj_70,geomObj_71,geomObj_72,geomObj_73,geomObj_74,geomObj_75,geomObj_76,geomObj_77,geomObj_78,geomObj_79,geomObj_80,geomObj_81,geomObj_82,geomObj_83,geomObj_84,geomObj_85,geomObj_86,geomObj_87,geomObj_88,geomObj_89,geomObj_90,geomObj_91,geomObj_92,geomObj_93,geomObj_94,geomObj_95,geomObj_96,geomObj_97,geomObj_98,geomObj_99,geomObj_100,geomObj_101,geomObj_102] = geompy.ExtractShapes(geomObj_54, geompy.ShapeType["SOLID"], True)
geomObj_103 = geompy.MakeFuseList([geomObj_33, geomObj_34, geomObj_35, geomObj_36, geomObj_37, geomObj_38, geomObj_39, geomObj_40, geomObj_41, geomObj_42, geomObj_43, geomObj_44, geomObj_45, geomObj_46, geomObj_47, geomObj_48, geomObj_49, geomObj_50, geomObj_55, geomObj_56, geomObj_57, geomObj_58, geomObj_59, geomObj_60, geomObj_61, geomObj_62, geomObj_63, geomObj_64, geomObj_65, geomObj_66, geomObj_67, geomObj_68, geomObj_69, geomObj_70, geomObj_71, geomObj_72, geomObj_73, geomObj_74, geomObj_75, geomObj_76, geomObj_77, geomObj_78, geomObj_79, geomObj_80, geomObj_81, geomObj_82, geomObj_83, geomObj_84, geomObj_85, geomObj_86, geomObj_87, geomObj_88, geomObj_89, geomObj_90, geomObj_91, geomObj_92, geomObj_93, geomObj_94, geomObj_95, geomObj_96, geomObj_97, geomObj_98, geomObj_99, geomObj_100, geomObj_101, geomObj_102], False, False)
geomObj_104 = geompy.MakeScaleTransform(geomObj_103, geomObj_1, 100)
geomObj_105 = geompy.MakeFilletAll(geomObj_104, 0.6170130261493888)
geomObj_106 = geompy.MakeCutList(geomObj_7, [geomObj_105])
faceCenteredCubic = geompy.MakeScaleTransform(geomObj_106, geomObj_1, 0.01)
geomObj_107 = geompy.CreateGroup(faceCenteredCubic, geompy.ShapeType["FACE"])
geompy.UnionIDs(geomObj_107, [3, 21, 30, 35, 42, 59, 84, 89, 118, 131, 136, 177, 180, 183, 188, 203, 230, 233, 236, 247, 259, 261, 266, 270, 272, 277, 281, 296, 301, 304, 306, 311, 316, 322, 324, 338, 353, 357, 359, 362, 365, 370, 375, 380, 383, 388, 391, 398, 421, 424, 427, 438, 443, 448, 455, 460, 465, 470, 475, 480, 487, 492, 497, 504, 517, 534, 557, 561, 563, 566, 569, 577, 579, 583, 586, 588, 591, 595, 598, 602, 604])
inlet = geompy.CreateGroup(faceCenteredCubic, geompy.ShapeType["FACE"])
geomObj_108 = geompy.MakeCutList(geomObj_6, [geomObj_105])
geomObj_109 = geompy.MakeScaleTransform(geomObj_108, geomObj_1, 0.01)
geomObj_110 = geompy.GetInPlace(faceCenteredCubic, geomObj_109, True)
[geomObj_111,geomObj_112,geomObj_113,geomObj_114,geomObj_115,geomObj_116] = geompy.SubShapeAll(geomObj_110, geompy.ShapeType["FACE"])
geompy.UnionList(inlet, [geomObj_111, geomObj_112, geomObj_113, geomObj_114, geomObj_115, geomObj_116])
outlet = geompy.CreateGroup(faceCenteredCubic, geompy.ShapeType["FACE"])
geomObj_117 = geompy.MakeCutList(geomObj_15, [geomObj_105])
geomObj_118 = geompy.MakeScaleTransform(geomObj_117, geomObj_1, 0.01)
geomObj_119 = geompy.GetInPlace(faceCenteredCubic, geomObj_118, True)
[geomObj_120,geomObj_121,geomObj_122,geomObj_123,geomObj_124,geomObj_125] = geompy.SubShapeAll(geomObj_119, geompy.ShapeType["FACE"])
geompy.UnionList(outlet, [geomObj_120, geomObj_121, geomObj_122, geomObj_123, geomObj_124, geomObj_125])
symetry0 = geompy.CreateGroup(faceCenteredCubic, geompy.ShapeType["FACE"])
geomObj_126 = geompy.MakeCutList(geomObj_8, [geomObj_105])
geomObj_127 = geompy.MakeScaleTransform(geomObj_126, geomObj_1, 0.01)
geomObj_128 = geompy.GetInPlace(faceCenteredCubic, geomObj_127, True)
[geomObj_129,geomObj_130] = geompy.SubShapeAll(geomObj_128, geompy.ShapeType["FACE"])
geompy.UnionList(symetry0, [geomObj_129, geomObj_130])
symetry1 = geompy.CreateGroup(faceCenteredCubic, geompy.ShapeType["FACE"])
geomObj_131 = geompy.MakeCutList(geomObj_9, [geomObj_105])
geomObj_132 = geompy.MakeScaleTransform(geomObj_131, geomObj_1, 0.01)
geomObj_133 = geompy.GetInPlace(faceCenteredCubic, geomObj_132, True)
[geomObj_134,geomObj_135] = geompy.SubShapeAll(geomObj_133, geompy.ShapeType["FACE"])
geompy.UnionList(symetry1, [geomObj_134, geomObj_135])
symetry2 = geompy.CreateGroup(faceCenteredCubic, geompy.ShapeType["FACE"])
geomObj_136 = geompy.MakeCutList(geomObj_10, [geomObj_105])
geomObj_137 = geompy.MakeScaleTransform(geomObj_136, geomObj_1, 0.01)
geomObj_138 = geompy.GetInPlace(faceCenteredCubic, geomObj_137, True)
[geomObj_139,geomObj_140] = geompy.SubShapeAll(geomObj_138, geompy.ShapeType["FACE"])
geompy.UnionList(symetry2, [geomObj_139, geomObj_140])
symetry3 = geompy.CreateGroup(faceCenteredCubic, geompy.ShapeType["FACE"])
geomObj_141 = geompy.MakeCutList(geomObj_11, [geomObj_105])
geomObj_142 = geompy.MakeScaleTransform(geomObj_141, geomObj_1, 0.01)
geomObj_143 = geompy.GetInPlace(faceCenteredCubic, geomObj_142, True)
[geomObj_144,geomObj_145] = geompy.SubShapeAll(geomObj_143, geompy.ShapeType["FACE"])
geompy.UnionList(symetry3, [geomObj_144, geomObj_145])
symetry4 = geompy.CreateGroup(faceCenteredCubic, geompy.ShapeType["FACE"])
geomObj_146 = geompy.MakeCutList(geomObj_12, [geomObj_105])
geomObj_147 = geompy.MakeScaleTransform(geomObj_146, geomObj_1, 0.01)
geomObj_148 = geompy.GetInPlace(faceCenteredCubic, geomObj_147, True)
[geomObj_149,geomObj_150] = geompy.SubShapeAll(geomObj_148, geompy.ShapeType["FACE"])
geompy.UnionList(symetry4, [geomObj_149, geomObj_150])
symetry5 = geompy.CreateGroup(faceCenteredCubic, geompy.ShapeType["FACE"])
geomObj_151 = geompy.MakeCutList(geomObj_13, [geomObj_105])
geomObj_152 = geompy.MakeScaleTransform(geomObj_151, geomObj_1, 0.01)
geomObj_153 = geompy.GetInPlace(faceCenteredCubic, geomObj_152, True)
[geomObj_154,geomObj_155] = geompy.SubShapeAll(geomObj_153, geompy.ShapeType["FACE"])
geompy.UnionList(symetry5, [geomObj_154, geomObj_155])
wall = geompy.CutListOfGroups([geomObj_107], [inlet, outlet, symetry0, symetry1, symetry2, symetry3, symetry4, symetry5])
[geomObj_107, inlet, geomObj_110, outlet, geomObj_119, symetry0, geomObj_128, symetry1, geomObj_133, symetry2, geomObj_138, symetry3, geomObj_143, symetry4, geomObj_148, symetry5, geomObj_153, wall] = geompy.GetExistingSubObjects(faceCenteredCubic, False)
[geomObj_107, inlet, geomObj_110, outlet, geomObj_119, symetry0, geomObj_128, symetry1, geomObj_133, symetry2, geomObj_138, symetry3, geomObj_143, symetry4, geomObj_148, symetry5, geomObj_153, wall] = geompy.GetExistingSubObjects(faceCenteredCubic, False)
[geomObj_107, inlet, geomObj_110, outlet, geomObj_119, symetry0, geomObj_128, symetry1, geomObj_133, symetry2, geomObj_138, symetry3, geomObj_143, symetry4, geomObj_148, symetry5, geomObj_153, wall] = geompy.GetExistingSubObjects(faceCenteredCubic, False)
geompy.addToStudy( faceCenteredCubic, 'faceCenteredCubic' )
geompy.addToStudyInFather( faceCenteredCubic, inlet, 'inlet' )
geompy.addToStudyInFather( faceCenteredCubic, outlet, 'outlet' )
geompy.addToStudyInFather( faceCenteredCubic, symetry0, 'symetry0' )
geompy.addToStudyInFather( faceCenteredCubic, symetry1, 'symetry1' )
geompy.addToStudyInFather( faceCenteredCubic, symetry2, 'symetry2' )
geompy.addToStudyInFather( faceCenteredCubic, symetry3, 'symetry3' )
geompy.addToStudyInFather( faceCenteredCubic, symetry4, 'symetry4' )
geompy.addToStudyInFather( faceCenteredCubic, symetry5, 'symetry5' )
geompy.addToStudyInFather( faceCenteredCubic, wall, 'wall' )

###
### SMESH component
###

import  SMESH, SALOMEDS
from salome.smesh import smeshBuilder

smesh = smeshBuilder.New()
#smesh.SetEnablePublish( False ) # Set to False to avoid publish in study if not needed or in some particular situations:
                                 # multiples meshes built in parallel, complex and numerous mesh edition (performance)

Mesh_1 = smesh.Mesh(faceCenteredCubic)
NETGEN_1D_2D_3D = Mesh_1.Tetrahedron(algo=smeshBuilder.NETGEN_1D2D3D)
NETGEN_3D_Parameters_1 = NETGEN_1D_2D_3D.Parameters()
NETGEN_3D_Parameters_1.SetMaxSize( 0.05 )
NETGEN_3D_Parameters_1.SetMinSize( 0.005 )
NETGEN_3D_Parameters_1.SetSecondOrder( 0 )
NETGEN_3D_Parameters_1.SetOptimize( 1 )
NETGEN_3D_Parameters_1.SetFineness( 1 )
NETGEN_3D_Parameters_1.SetChordalError( -1 )
NETGEN_3D_Parameters_1.SetChordalErrorEnabled( 0 )
NETGEN_3D_Parameters_1.SetUseSurfaceCurvature( 1 )
NETGEN_3D_Parameters_1.SetFuseEdges( 1 )
NETGEN_3D_Parameters_1.SetQuadAllowed( 0 )
NETGEN_3D_Parameters_1.SetCheckChartBoundary( 88 )
Viscous_Layers_1 = NETGEN_1D_2D_3D.ViscousLayers(0.001,2,1.2,[ 21, 35, 316, 183, 365, 380, 475, 460, 497, 448, 595, 579 ],1,smeshBuilder.SURF_OFFSET_SMOOTH)
#Group_1 = Mesh_1.GroupOnGeom(__NOT__Published__Object__,'',SMESH.FACE)
inlet_1 = Mesh_1.GroupOnGeom(inlet,'inlet',SMESH.FACE)
#Group_3 = Mesh_1.GroupOnGeom(__NOT__Published__Object__,'',SMESH.FACE)
outlet_1 = Mesh_1.GroupOnGeom(outlet,'outlet',SMESH.FACE)
#Group_5 = Mesh_1.GroupOnGeom(__NOT__Published__Object__,'',SMESH.FACE)
symetry0_1 = Mesh_1.GroupOnGeom(symetry0,'symetry0',SMESH.FACE)
#Group_7 = Mesh_1.GroupOnGeom(__NOT__Published__Object__,'',SMESH.FACE)
symetry1_1 = Mesh_1.GroupOnGeom(symetry1,'symetry1',SMESH.FACE)
#Group_9 = Mesh_1.GroupOnGeom(__NOT__Published__Object__,'',SMESH.FACE)
symetry2_1 = Mesh_1.GroupOnGeom(symetry2,'symetry2',SMESH.FACE)
#Group_11 = Mesh_1.GroupOnGeom(__NOT__Published__Object__,'',SMESH.FACE)
symetry3_1 = Mesh_1.GroupOnGeom(symetry3,'symetry3',SMESH.FACE)
#Group_13 = Mesh_1.GroupOnGeom(__NOT__Published__Object__,'',SMESH.FACE)
symetry4_1 = Mesh_1.GroupOnGeom(symetry4,'symetry4',SMESH.FACE)
#Group_15 = Mesh_1.GroupOnGeom(__NOT__Published__Object__,'',SMESH.FACE)
symetry5_1 = Mesh_1.GroupOnGeom(symetry5,'symetry5',SMESH.FACE)
#Group_17 = Mesh_1.GroupOnGeom(__NOT__Published__Object__,'',SMESH.FACE)
wall_1 = Mesh_1.GroupOnGeom(wall,'wall',SMESH.FACE)
isDone = Mesh_1.Compute()
[ Group_1, inlet_1, Group_3, outlet_1, Group_5, symetry0_1, Group_7, symetry1_1, Group_9, symetry2_1, Group_11, symetry3_1, Group_13, symetry4_1, Group_15, symetry5_1, Group_17, wall_1 ] = Mesh_1.GetGroups()
Mesh_4 = smesh.Mesh()
Mesh_2 = smesh.Mesh(faceCenteredCubic)
status = Mesh_2.AddHypothesis(NETGEN_3D_Parameters_1)
status = Mesh_2.AddHypothesis(Viscous_Layers_1)
NETGEN_1D_2D_3D_1 = Mesh_2.Tetrahedron(algo=smeshBuilder.NETGEN_1D2D3D)
#Group_1_1 = Mesh_2.GroupOnGeom(__NOT__Published__Object__,'',SMESH.FACE)
inlet_2 = Mesh_2.GroupOnGeom(inlet,'inlet',SMESH.FACE)
#Group_3_1 = Mesh_2.GroupOnGeom(__NOT__Published__Object__,'',SMESH.FACE)
outlet_2 = Mesh_2.GroupOnGeom(outlet,'outlet',SMESH.FACE)
#Group_5_1 = Mesh_2.GroupOnGeom(__NOT__Published__Object__,'',SMESH.FACE)
symetry0_2 = Mesh_2.GroupOnGeom(symetry0,'symetry0',SMESH.FACE)
#Group_7_1 = Mesh_2.GroupOnGeom(__NOT__Published__Object__,'',SMESH.FACE)
symetry1_2 = Mesh_2.GroupOnGeom(symetry1,'symetry1',SMESH.FACE)
#Group_9_1 = Mesh_2.GroupOnGeom(__NOT__Published__Object__,'',SMESH.FACE)
symetry2_2 = Mesh_2.GroupOnGeom(symetry2,'symetry2',SMESH.FACE)
#Group_11_1 = Mesh_2.GroupOnGeom(__NOT__Published__Object__,'',SMESH.FACE)
symetry3_2 = Mesh_2.GroupOnGeom(symetry3,'symetry3',SMESH.FACE)
#Group_13_1 = Mesh_2.GroupOnGeom(__NOT__Published__Object__,'',SMESH.FACE)
symetry4_2 = Mesh_2.GroupOnGeom(symetry4,'symetry4',SMESH.FACE)
#Group_15_1 = Mesh_2.GroupOnGeom(__NOT__Published__Object__,'',SMESH.FACE)
symetry5_2 = Mesh_2.GroupOnGeom(symetry5,'symetry5',SMESH.FACE)
#Group_17_1 = Mesh_2.GroupOnGeom(__NOT__Published__Object__,'',SMESH.FACE)
wall_2 = Mesh_2.GroupOnGeom(wall,'wall',SMESH.FACE)
isDone = Mesh_2.Compute()
[ Group_1_1, inlet_2, Group_3_1, outlet_2, Group_5_1, symetry0_2, Group_7_1, symetry1_2, Group_9_1, symetry2_2, Group_11_1, symetry3_2, Group_13_1, symetry4_2, Group_15_1, symetry5_2, Group_17_1, wall_2 ] = Mesh_2.GetGroups()
[ Group_1, inlet_1, Group_3, outlet_1, Group_5, symetry0_1, Group_7, symetry1_1, Group_9, symetry2_1, Group_11, symetry3_1, Group_13, symetry4_1, Group_15, symetry5_1, Group_17, wall_1 ] = Mesh_1.GetGroups()
[ Group_1_1, inlet_2, Group_3_1, outlet_2, Group_5_1, symetry0_2, Group_7_1, symetry1_2, Group_9_1, symetry2_2, Group_11_1, symetry3_2, Group_13_1, symetry4_2, Group_15_1, symetry5_2, Group_17_1, wall_2 ] = Mesh_2.GetGroups()
aCriteria = []
aCriterion = smesh.GetCriterion(SMESH.VOLUME,SMESH.FT_ElemGeomType,SMESH.FT_Undefined,SMESH.Geom_PYRAMID)
aCriteria.append(aCriterion)
[ Group_1_1, inlet_2, Group_3_1, outlet_2, Group_5_1, symetry0_2, Group_7_1, symetry1_2, Group_9_1, symetry2_2, Group_11_1, symetry3_2, Group_13_1, symetry4_2, Group_15_1, symetry5_2, Group_17_1, wall_2 ] = Mesh_2.GetGroups()
Mesh_1.Clear()
Mesh_2.Clear()
Mesh_3 = smesh.Mesh(faceCenteredCubic)
status = Mesh_3.AddHypothesis(NETGEN_3D_Parameters_1)
status = Mesh_3.AddHypothesis(Viscous_Layers_1)
NETGEN_1D_2D_3D_2 = Mesh_3.Tetrahedron(algo=smeshBuilder.NETGEN_1D2D3D)
inlet_3 = Mesh_3.GroupOnGeom(inlet,'inlet',SMESH.FACE)
outlet_3 = Mesh_3.GroupOnGeom(outlet,'outlet',SMESH.FACE)
symetry0_3 = Mesh_3.GroupOnGeom(symetry0,'symetry0',SMESH.FACE)
symetry1_3 = Mesh_3.GroupOnGeom(symetry1,'symetry1',SMESH.FACE)
symetry2_3 = Mesh_3.GroupOnGeom(symetry2,'symetry2',SMESH.FACE)
symetry3_3 = Mesh_3.GroupOnGeom(symetry3,'symetry3',SMESH.FACE)
symetry4_3 = Mesh_3.GroupOnGeom(symetry4,'symetry4',SMESH.FACE)
symetry5_3 = Mesh_3.GroupOnGeom(symetry5,'symetry5',SMESH.FACE)
wall_3 = Mesh_3.GroupOnGeom(wall,'wall',SMESH.FACE)
isDone = Mesh_3.Compute()
[ smeshObj_1, inlet_3, smeshObj_2, outlet_3, smeshObj_3, symetry0_3, smeshObj_4, symetry1_3, smeshObj_5, symetry2_3, smeshObj_6, symetry3_3, smeshObj_7, symetry4_3, smeshObj_8, symetry5_3, smeshObj_9, wall_3 ] = Mesh_3.GetGroups()
aCriteria = []
aCriterion = smesh.GetCriterion(SMESH.VOLUME,SMESH.FT_ElemGeomType,SMESH.FT_Undefined,SMESH.Geom_PYRAMID)
aCriteria.append(aCriterion)
Mesh_3.SplitVolumesIntoTetra( Mesh_3.GetIDSource([ 189580, 222102, 189581, 222103, 146658, 146659, 106364, 106365, 146364, 146365, 105266, 105267, 162840, 162841, 189808, 189809, 105172, 105173, 180526, 180527, 154066, 154067, 104882, 104883, 123066, 123067, 123068, 123069, 180640, 222050, 180641, 222051, 162664, 180238, 162665, 180239, 106312, 106313, 154188, 154189, 122780, 122781, 162784, 146726, 162785, 222274, 146727, 162786, 222275, 162787, 189756, 189757, 189458, 189459, 222394, 222395 ], SMESH.VOLUME), 1 )
[ smeshObj_1, inlet_3, smeshObj_2, outlet_3, smeshObj_3, symetry0_3, smeshObj_4, symetry1_3, smeshObj_5, symetry2_3, smeshObj_6, symetry3_3, smeshObj_7, symetry4_3, smeshObj_8, symetry5_3, smeshObj_9, wall_3 ] = Mesh_3.GetGroups()

## some objects were removed
aStudyBuilder = salome.myStudy.NewBuilder()
SO = salome.myStudy.FindObjectIOR(salome.myStudy.ConvertObjectToIOR(smeshObj_8))
if SO: aStudyBuilder.RemoveObjectWithChildren(SO)
SO = salome.myStudy.FindObjectIOR(salome.myStudy.ConvertObjectToIOR(smeshObj_9))
if SO: aStudyBuilder.RemoveObjectWithChildren(SO)
SO = salome.myStudy.FindObjectIOR(salome.myStudy.ConvertObjectToIOR(smeshObj_6))
if SO: aStudyBuilder.RemoveObjectWithChildren(SO)
SO = salome.myStudy.FindObjectIOR(salome.myStudy.ConvertObjectToIOR(smeshObj_7))
if SO: aStudyBuilder.RemoveObjectWithChildren(SO)
SO = salome.myStudy.FindObjectIOR(salome.myStudy.ConvertObjectToIOR(smeshObj_5))
if SO: aStudyBuilder.RemoveObjectWithChildren(SO)
SO = salome.myStudy.FindObjectIOR(salome.myStudy.ConvertObjectToIOR(smeshObj_3))
if SO: aStudyBuilder.RemoveObjectWithChildren(SO)
SO = salome.myStudy.FindObjectIOR(salome.myStudy.ConvertObjectToIOR(smeshObj_4))
if SO: aStudyBuilder.RemoveObjectWithChildren(SO)
SO = salome.myStudy.FindObjectIOR(salome.myStudy.ConvertObjectToIOR(smeshObj_1))
if SO: aStudyBuilder.RemoveObjectWithChildren(SO)
SO = salome.myStudy.FindObjectIOR(salome.myStudy.ConvertObjectToIOR(smeshObj_2))
if SO: aStudyBuilder.RemoveObjectWithChildren(SO)

## Set names of Mesh objects
smesh.SetName(NETGEN_1D_2D_3D.GetAlgorithm(), 'NETGEN 1D-2D-3D')
smesh.SetName(symetry1_1, 'symetry1')
smesh.SetName(Group_9, 'Group_9')
smesh.SetName(Viscous_Layers_1, 'Viscous Layers_1')
smesh.SetName(NETGEN_3D_Parameters_1, 'NETGEN 3D Parameters_1')
smesh.SetName(Group_1, 'Group_1')
smesh.SetName(inlet_1, 'inlet')
smesh.SetName(Group_3, 'Group_3')
smesh.SetName(outlet_1, 'outlet')
smesh.SetName(Group_5, 'Group_5')
smesh.SetName(symetry0_1, 'symetry0')
smesh.SetName(Group_7, 'Group_7')
smesh.SetName(Mesh_1.GetMesh(), 'Mesh_1')
smesh.SetName(Mesh_2.GetMesh(), 'Mesh_2')
smesh.SetName(Mesh_4.GetMesh(), 'Mesh_4')
smesh.SetName(Mesh_3.GetMesh(), 'Mesh_3')
smesh.SetName(wall_3, 'wall')
smesh.SetName(symetry4_3, 'symetry4')
smesh.SetName(symetry5_3, 'symetry5')
smesh.SetName(symetry2_3, 'symetry2')
smesh.SetName(wall_1, 'wall')
smesh.SetName(symetry3_3, 'symetry3')
smesh.SetName(Group_11, 'Group_11')
smesh.SetName(symetry2_1, 'symetry2')
smesh.SetName(Group_13, 'Group_13')
smesh.SetName(symetry3_1, 'symetry3')
smesh.SetName(Group_15, 'Group_15')
smesh.SetName(symetry1_2, 'symetry1')
smesh.SetName(symetry4_1, 'symetry4')
smesh.SetName(symetry1_3, 'symetry1')
smesh.SetName(Group_9_1, 'Group_9')
smesh.SetName(Group_17, 'Group_17')
smesh.SetName(symetry0_2, 'symetry0')
smesh.SetName(symetry5_1, 'symetry5')
smesh.SetName(Group_7_1, 'Group_7')
smesh.SetName(outlet_2, 'outlet')
smesh.SetName(outlet_3, 'outlet')
smesh.SetName(Group_5_1, 'Group_5')
smesh.SetName(inlet_2, 'inlet')
smesh.SetName(symetry0_3, 'symetry0')
smesh.SetName(Group_3_1, 'Group_3')
smesh.SetName(Group_1_1, 'Group_1')
smesh.SetName(inlet_3, 'inlet')
smesh.SetName(wall_2, 'wall')
smesh.SetName(Group_17_1, 'Group_17')
smesh.SetName(symetry5_2, 'symetry5')
smesh.SetName(Group_15_1, 'Group_15')
smesh.SetName(symetry4_2, 'symetry4')
smesh.SetName(Group_13_1, 'Group_13')
smesh.SetName(symetry3_2, 'symetry3')
smesh.SetName(Group_11_1, 'Group_11')
smesh.SetName(symetry2_2, 'symetry2')


if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()
