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
        salome.salome_init()

    def geometryCreate(self, alpha):
        """
        Create the simple cubic geometry.

        Parameters:
            alpha (float): Sphere intersection parameter which used for cutting spheres from box.
                
                Radius = R_0 / (1 - alpha)
                Should be from 0.01 to 0.13

        Returns:
            Configured geometry.
        """

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

        return self.geometry

    def boundaryCreate(self, direction):
        """
        Create the boundary faces from the geometry.

        Parameters:
            direction (str): Direction of the flow.

                '001' for the flow with normal vector (0, 0, -1) to face.
                '100' for the flow with normal vector (-1, 0, 0) to face.

        Returns:
            boundary (dict):

            {
                "inlet": <GEOM._objref_GEOM_Object>,
                "outlet": <GEOM._objref_GEOM_Object>,
                "symetryPlane": <GEOM._objref_GEOM_Object>,
                "wall": <GEOM._objref_GEOM_Object>
            }

        """
        #
        #      _____    z      |
        #     //////|   |      | flow
        #    ////// |   |___y  f
        #    |    | /   /     
        #    |____|/   /x      direction [0, 0, 1]
        #
        #      _____    z        f
        #     /    /|   |       / flow
        #    /____/ |   |___y  /
        #    |||||| /   /      
        #    ||||||/   /x      direction [1, 0, 0]
        #
        
        geompy = geomBuilder.New() 
        center = geompy.MakeVertex(2, 2, 1)
        rot = [0, 0, 45]

        if direction == "001":
            norm = geompy.MakeVector(center, 
                geompy.MakeVertexWithRef(center, 0, 0, 1))
            vstep = 1
            hstep = math.sqrt(2)
        
        elif direction == "100":
            norm = geompy.MakeVector(center, 
                geompy.MakeVertexWithRef(center, 
                    math.cos((90 + rot[2]) * math.pi / 180.0), 
                    -math.sin((90 + rot[2]) * math.pi / 180.0), 0))
            vstep = math.sqrt(2)
            hstep = 1
        
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
        
        # Bounding box
        box = geompy.MakeBoxDXDYDZ(2 * math.sqrt(2), 2 * math.sqrt(2), 2)
        box = geompy.MakeRotation(box, axes[2], 45 * math.pi / 180.0)
        box = geompy.MakeTranslation(box, 2, 0, 0)
        planes = geompy.ExtractShapes(box, geompy.ShapeType["FACE"], True)

        vplanes = []
        hplanes = []
        for plane in planes:
            planeNorm = geompy.GetNormal(plane)
            angle = abs(geompy.GetAngle(planeNorm, norm))

            if angle == 0 or angle == 180:
                vplanes.append(plane)

            else:
                hplanes.append(plane)
        
        if direction == "001":
            z1 = geompy.GetPosition(vplanes[0])[3]
            z2 = geompy.GetPosition(vplanes[1])[3]

            if z1 > z2:
                inletplane = vplanes[0]
                outletplane = vplanes[1]
            
            else:
                inletplane = vplanes[1]
                outletplane = vplanes[0]

        elif direction == "100":
            x1 = geompy.GetPosition(vplanes[0])[1]
            x2 = geompy.GetPosition(vplanes[1])[1]

            if x1 > x2:
                inletplane = vplanes[0]
                outletplane = vplanes[1]
            
            else:
                inletplane = vplanes[1]
                outletplane = vplanes[0]


        # inlet and outlet
        common1 = geompy.MakeCommonList([self.geometry, inletplane], True)
        inlet = createGroup(common1, "inlet")

        common2 = geompy.MakeCommonList([self.geometry, outletplane], True)
        outlet = createGroup(common2, "outlet")

        # symetryPlane(s)
        symetryPlane = geompy.CreateGroup(self.geometry, geompy.ShapeType["FACE"], "symetryPlane")
        
        for plane in hplanes:
            common3 = geompy.MakeCommonList([self.geometry, plane], True)
            gip = geompy.GetInPlace(self.geometry, common3, True)
            faces = geompy.SubShapeAll(gip, geompy.ShapeType["FACE"])
            geompy.UnionList(symetryPlane, faces)

        # wall
        allgroup = geompy.CreateGroup(self.geometry, geompy.ShapeType["FACE"])
        faces = geompy.SubShapeAllIDs(self.geometry, geompy.ShapeType["FACE"]) 
        geompy.UnionIDs(allgroup, faces)
        wall = geompy.CutListOfGroups([allgroup], [inlet, outlet, symetryPlane], "wall")
        
        self.boundary = {
            "inlet": inlet,
            "outlet": outlet,
            "symetryPlane": symetryPlane,
            "wall": wall
        }

        return self.boundary

    def meshCreate(self, fineness, viscousLayers=None):
        """
        Creates a mesh from a geometry.

        Parameters:
            fineness (int): Fineness of mesh.
                
                0 - Very coarse,
                1 - Coarse,
                2 - Moderate,
                3 - Fine,
                4 - Very fine.

            viscousLayers (dict or None): Defines viscous layers for mesh. 
                By default, inlets and outlets specified without layers.
                
                {
                    "thickness": float,
                    "number": int,
                    "stretch": float
                }

        Returns:
            Configured instance of class <SMESH.SMESH_Mesh>, containig the parameters and boundary groups.

        """
        smesh = smeshBuilder.New()

        mesh = smesh.Mesh(self.geometry)
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
        param.SetFineness(fineness)
        #param.SetGrowthRate( 0.1 )
        #param.SetNbSegPerEdge( 5 )
        #param.SetNbSegPerRadius( 10 )
        param.SetQuadAllowed( 0 )
        
        if not viscousLayers is None:
            vlayer = netgen.ViscousLayers(viscousLayers["thickness"], 
                                          viscousLayers["number"], 
                                          viscousLayers["stretch"], 
                                          [self.boundary["inlet"], self.boundary["outlet"]],
                                          1, smeshBuilder.NODE_OFFSET)
        
        for name, boundary in self.boundary.items():
            mesh.GroupOnGeom(boundary, name, SMESH.FACE)

        self.mesh = mesh

        return self.mesh

    def meshCompute(self):
        """Compute the mesh."""
        status = self.mesh.Compute()
        
        if status:
            print("Mesh succesfully computed.")

        else:
            print("Mesh is not computed.")

    def meshExport(self, path):
        """
        Export the mesh in a file in UNV format.

        Parameters:
            path (string): full path to the expected directory.
        """
        exportpath = os.path.join(path, "{}.unv".format(self.name))

        try:
            self.mesh.ExportUNV(exportpath)
        
        except:
            print("Error: Cannot export mesh to '{}'".format(exportpath))

if __name__ == "__main__":
    buildpath = str(sys.argv[1])
    alpha = float(sys.argv[2])
    direction = str(sys.argv[3])

    sc = simpleCubic("simpleCubic-{}-{}".format(direction, alpha))
    sc.geometryCreate(alpha)
    sc.boundaryCreate(direction)
    sc.meshCreate(2, {
        "thickness": 0.02,
        "number": 2,
        "stretch": 1.1
    })
    sc.meshCompute()
    #sc.meshExport(build)

    if salome.sg.hasDesktop():
        salome.sg.updateObjBrowser()
