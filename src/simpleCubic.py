#!/usr/bin/env python
# -*- coding: utf-8 -*-
import salome, GEOM, SMESH, SALOMEDS
from salome.geom import geomBuilder
from salome.smesh import smeshBuilder
import math
import os, sys

class simpleCubic:
    def __init__(self, name = None):
        self.name = name if type(name) != None else "simpleCubic"
        self.geometry = None
        self.mesh = None
        self.boundary = None

    def geometryCreate(self, alpha):
        geompy = geomBuilder.New()
        
        #
        R_0 = 1
        R = R_0 / (1 - alpha)
        R_fillet = 0.1

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
        sphere = geompy.MakeSpherePntR(vtx[0], R)
        sphere = geompy.MakeMultiTranslation2D(sphere, None, 2, 3, None, 2, 3)
        sphere = geompy.MakeTranslation(sphere, -2, 0, 0)
        sphere2 = geompy.MakeTranslation(sphere, 0, 0, 2)
        
        sphere = geompy.ExtractShapes(sphere, geompy.ShapeType["SOLID"], True)
        sphere2 = geompy.ExtractShapes(sphere2, geompy.ShapeType["SOLID"], True)
        
        sphere = geompy.MakeFuseList(sphere + sphere2, True, True)
        sphere = geompy.MakeFilletAll(sphere, R_fillet)
        
        self.geometry = geompy.MakeCutList(box, [sphere], True)
        
        geompy.addToStudy(self.geometry, self.name)

    def boundaryCreate(self, direction):
        geompy = geomBuilder.New()
        #
        #   D /\ B  A(1, 1, 0)  \vec{n}(1, 1, 0)
        #    /  \   B(3, 3, 0)  \vec{n}(1, 1, 0)
        #    \  /   C(3, 1, 0)  \vec{n}(-1, 1, 0)
        #   A \/ C  D(1, 3, 0)  \vec{n}(-1, 1, 0)
        #
        
        center = geompy.MakeVertex(2, 2, 1)
        rot = [0, 0, 45]

        if direction == "100":
            norm = geompy.MakeVector(center, 
                geompy.MakeVertexWithRef(center, 0, 0, 1))
            vstep = math.sqrt(2)
            hstep = 1
        
        elif direction == "001":
            norm = geompy.MakeVector(center, 
                geompy.MakeVertexWithRef(center, 1, 0, 0))
            vstep = 1
            hstep = math.sqrt(2)
        
        def createGroup(shape, name):
            group = geompy.CreateGroup(self.geometry, 
                geompy.ShapeType["FACE"], name)
            gip = geompy.GetInPlace(self.geometry, shape, True)
            faces = geompy.SubShapeAll(gip, geompy.ShapeType["FACE"])
            geompy.UnionList(group, faces)

            return group
        
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
        planes = geompy.ExtractShapes(box, 
            geompy.ShapeType["FACE"], True)
        planecommon = []

        for plane in planes:
            planecommon.append(geompy.MakeCommonList([self.geometry, plane], True))

        planegroup = geompy.CreateGroup(self.geometry, geompy.ShapeType["FACE"])
        for planecom in planecommon:
            faces = geompy.SubShapeAllIDs(planecom, geompy.ShapeType["FACE"]) 
            geompy.UnionIDs(planegroup, faces)
        
        
        # Prepare faces
        #vtx.append(geompy.MakeVertex(2, 2, 2))
        #vtx.append(geompy.MakeVertexWithRef(vtx[3], 0, 0, 1))
        #vec2 = geompy.MakeVector(vtx[3], vtx[4])
        plane = geompy.MakePlane(center, norm, 5)
        
        plane2 = geompy.MakeTranslationVectorDistance(plane, norm, vstep)
        common2 = geompy.MakeCommonList([self.geometry, plane2], True)
        inlet = createGroup(common2, "inlet")

        plane3 = geompy.MakeTranslationVectorDistance(plane, norm, -vstep)
        common3 = geompy.MakeCommonList([self.geometry, plane3], True)
        outlet = createGroup(common3, "outlet")
        
        symetryPlane = geompy.CutListOfGroups([planegroup], [inlet, outlet])

        PoreGroup = geompy.CreateGroup(self.geometry, geompy.ShapeType["FACE"])
        faces = geompy.SubShapeAllIDs(self.geometry, geompy.ShapeType["FACE"]) 
        geompy.UnionIDs(PoreGroup, faces)
        
        wall = geompy.CutListOfGroups([PoreGroup], [inlet, outlet, symetryPlane])
        
        self.boundary = {
            "inlet": inlet,
            "outlet": outlet,
            "symetryPlane": symetryPlane,
            "wall": wall
        }

        return self.boundary

    def meshCreate(self):
        smesh = smeshBuilder.New()


        mesh = smesh.Mesh(geomObj)
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
        param.SetMaxSize( 0.1 )
        param.SetFineness( 4 )
        #param.SetGrowthRate( 0.1 )
        #param.SetNbSegPerEdge( 5 )
        #param.SetNbSegPerRadius( 10 )
        param.SetQuadAllowed( 0 )

        vlayer = netgen.ViscousLayers(0.025, 2, 1.1, [],
            1, smeshBuilder.NODE_OFFSET)
        
        mesh.GroupOnGeom(bc[0], 'inlet', SMESH.FACE)
        mesh.GroupOnGeom(bc[1], 'outlet', SMESH.FACE)
        mesh.GroupOnGeom(bc[2], 'wall', SMESH.FACE)

        self.mesh = mesh

        return self.mesh

    def meshCompute(self):
        status = self.mesh.Compute()
        
        if status:
            print("Mesh succesfully computed.")

        else:
            print("Mesh is not computed.")

    def meshExport(self, path):
        exportpath = os.path.join(path, "{}.unv".format(self.name))

        try:
            self.mesh.ExportUNV(exportpath)
        
        except:
            print("Error: Cannot export mesh to '{}'".format(exportpath))

if __name__ == "__main__":
    buildpath = str(sys.argv[1])
    alpha = float(sys.argv[2])
    direction = str(sys.argv[3])

    salome.salome_init()
    sc = simpleCubic("simpleCubic-{}-{}".format(direction, alpha))
    sc.geometryCreate(alpha)
    sc.boundaryCreate(direction)
    #sc.meshCreate()
    #sc.meshCompute()
    #sc.meshExport(build)

    if salome.sg.hasDesktop():
        salome.sg.updateObjBrowser()