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
simpleCubic_100_0_1 = geompy.MakeCutList(geomObj_17, [geomObj_18], True)
Sphere_1 = geompy.MakeSphereR(1)
Translation_1 = geompy.MakeTranslation(Sphere_1, 1.9, 0, 0)
geomObj_19 = geompy.MakeGlueFaces([Sphere_1, Translation_1], 1e-07)
Fuse_1 = geompy.MakeFuseList([Sphere_1, Translation_1], True, True)
Fillet_1 = geompy.MakeFilletAll(Fuse_1, 0.1)
Multi_Translation_1 = geompy.MakeMultiTranslation2D(Sphere_1, None, 1.9, 3, None, 1.9, 3)
[Solid_1,Solid_2,Solid_3,Solid_4,Solid_5,Solid_6,Solid_7,Solid_8,Solid_9] = geompy.ExtractShapes(Multi_Translation_1, geompy.ShapeType["SOLID"], True)
Fuse_2 = geompy.MakeFuseList([Solid_1, Solid_2, Solid_3, Solid_4, Solid_5, Solid_6, Solid_7, Solid_8, Solid_9], True, True)
Fillet_2 = geompy.MakeFilletAll(Fuse_2, 0.1)
geompy.addToStudy( simpleCubic_100_0_1, 'simpleCubic-100-0.1' )
geompy.addToStudy( Sphere_1, 'Sphere_1' )
geompy.addToStudy( Translation_1, 'Translation_1' )
geompy.addToStudy( Fuse_1, 'Fuse_1' )
geompy.addToStudy( Fillet_1, 'Fillet_1' )
geompy.addToStudy( Multi_Translation_1, 'Multi-Translation_1' )
geompy.addToStudyInFather( Multi_Translation_1, Solid_1, 'Solid_1' )
geompy.addToStudyInFather( Multi_Translation_1, Solid_2, 'Solid_2' )
geompy.addToStudyInFather( Multi_Translation_1, Solid_3, 'Solid_3' )
geompy.addToStudyInFather( Multi_Translation_1, Solid_4, 'Solid_4' )
geompy.addToStudyInFather( Multi_Translation_1, Solid_5, 'Solid_5' )
geompy.addToStudyInFather( Multi_Translation_1, Solid_6, 'Solid_6' )
geompy.addToStudyInFather( Multi_Translation_1, Solid_7, 'Solid_7' )
geompy.addToStudyInFather( Multi_Translation_1, Solid_8, 'Solid_8' )
geompy.addToStudyInFather( Multi_Translation_1, Solid_9, 'Solid_9' )
geompy.addToStudy( Fuse_2, 'Fuse_2' )
geompy.addToStudy( Fillet_2, 'Fillet_2' )


if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()
