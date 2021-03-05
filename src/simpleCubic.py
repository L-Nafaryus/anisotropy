#!/usr/bin/env python
# -*- coding: utf-8 -*-
import salome, GEOM, SMESH, SALOMEDS
from salome.geom import geomBuilder
from salome.smesh import smeshBuilder
import math
import os, sys
import logging
import time
from datetime import timedelta

class simpleCubic:
    def __init__(self, name = None):
        self.name = name if type(name) != None else "simpleCubic"
        self.geometry = None
        self.geometrybbox = None
        self.mesh = None
        self.boundary = None
        
        self.rombus = None
        self.rombusbbox = None

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
        R_fillet = 0

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
        sphere3 = geompy.MakeTranslation(sphere2, 0, 0, 2)
        
        sphere = geompy.ExtractShapes(sphere, geompy.ShapeType["SOLID"], True)
        sphere2 = geompy.ExtractShapes(sphere2, geompy.ShapeType["SOLID"], True)
        sphere3 = geompy.ExtractShapes(sphere3, geompy.ShapeType["SOLID"], True)

        sphere = geompy.MakeFuseList(sphere + sphere2 + sphere3, True, True)
        
        if not R_fillet == 0:
            sphere = geompy.MakeFilletAll(sphere, R_fillet)
        
        self.geometry = geompy.MakeCutList(box, [sphere], True)
        self.geometrybbox = box

        geompy.addToStudy(self.geometry, self.name)
        
        # Rombus
        h = 2

        sk = geompy.Sketcher3D()
        sk.addPointsAbsolute(0, 0, h * 2)
        sk.addPointsAbsolute(h, 0, h)
        sk.addPointsAbsolute(h, h, 0) 
        sk.addPointsAbsolute(0, h, h)
        sk.addPointsAbsolute(0, 0, h * 2)

        a3D_Sketcher_1 = sk.wire()
        Face_1 = geompy.MakeFaceWires([a3D_Sketcher_1], 1)
        Vector_1 = geompy.MakeVectorDXDYDZ(h, h, 0)
        rombus = geompy.MakePrismVecH(Face_1, Vector_1, 2 * math.sqrt(2))
        geompy.addToStudy(rombus, "romb")
        
        self.rombus = geompy.MakeCutList(rombus, [sphere], True)
        self.rombusbbox = rombus

        Operators = ["FixShape"]
        Parameters = ["FixShape.Tolerance3d"]
        Values = ["1e-7"]
        PS = geompy.ProcessShape(self.rombusbbox, Operators, Parameters, Values)
        self.rombusbbox = PS

        geompy.addToStudy(self.rombus, "rombus")

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
        rot = [0, 0, 45]
        buffergeometry = self.geometry

        if direction == "001":
            center = geompy.MakeVertex(2, 2, 1)

            norm = geompy.MakeVector(center, 
                geompy.MakeVertexWithRef(center, 0, 0, 1))
            
            vstep = 1
            hstep = math.sqrt(2)
        
        elif direction == "100":
            center = geompy.MakeVertex(2, 2, 1)

            norm = geompy.MakeVector(center, 
                geompy.MakeVertexWithRef(center, 
                    -math.cos((90 + rot[2]) * math.pi / 180.0), 
                    math.sin((90 + rot[2]) * math.pi / 180.0), 0))

            vstep = math.sqrt(2)
            hstep = 1

        elif direction == "111":
            center = geompy.MakeVertex(2, 2, 2)

            norm = geompy.MakeVector(center,
                geompy.MakeVertexWithRef(center,
                    -math.cos((90 + rot[2]) * math.pi / 180.0),
                    math.sin((90 + rot[2]) * math.pi / 180.0), math.sqrt(2) / 2))
            
            vstep = math.sqrt(2)
            hstep = 1 
        
        geompy.addToStudy(norm, "normalvector")

        def createGroup(shape, name):
            self.geometry = self.rombus

            group = geompy.CreateGroup(self.geometry, 
                geompy.ShapeType["FACE"], name)
            gip = geompy.GetInPlace(self.geometry, shape, True)
            faces = geompy.SubShapeAll(gip, geompy.ShapeType["FACE"])
            geompy.UnionList(group, faces)

            return group
        
        # xyz axes
        #axes = [
        #    geompy.MakeVectorDXDYDZ(1, 0, 0),
        #    geompy.MakeVectorDXDYDZ(0, 1, 0),
        #    geompy.MakeVectorDXDYDZ(0, 0, 1)
        #]
        
        # Bounding box
        #box = geompy.MakeBoxDXDYDZ(2 * math.sqrt(2), 2 * math.sqrt(2), 2)
        #box = geompy.MakeRotation(box, axes[2], 45 * math.pi / 180.0)
        #box = geompy.MakeTranslation(box, 2, 0, 0)
        if direction == "111":
            box = self.rombusbbox

        else:
            box = self.geometrybbox
        
        planes = geompy.ExtractShapes(box, geompy.ShapeType["FACE"], True)

        inletplane = None
        outletplane = None
        hplanes = []
        n = 0
        for plane in planes:
            planeNorm = geompy.GetNormal(plane)
            n += 1
            geompy.addToStudy(planeNorm, "normalplane-{}".format(n))
            angle = abs(geompy.GetAngle(planeNorm, norm))
            logging.info("angle = {}".format(angle))

            if angle == 0:
                outletplane = plane

            elif angle == 180:
                inletplane = plane

            else:
                hplanes.append(plane)

        if salome.sg.hasDesktop():
            salome.sg.updateObjBrowser()

        logging.info("hplanes = {}".format(len(hplanes)))

        
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
            logging.info("Mesh succesfully computed.")

        else:
            logging.warning("Mesh is not computed.")

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
            logging.error("Cannot export mesh to '{}'".format(exportpath))

if __name__ == "__main__":
    # Arguments
    buildpath = str(sys.argv[1])
    alpha = float(sys.argv[2])
    direction = str(sys.argv[3])
    
    name = "simpleCubic-{}-{}".format(direction, alpha)

    # Logger
    logging.basicConfig(
        level=logging.INFO, 
        format="%(levelname)s: %(message)s",
        handlers = [
            logging.StreamHandler(),
            logging.FileHandler(os.path.join(buildpath, "{}.log".format(name)))
        ])
    start_time = time.monotonic()
       
    # Simple cubic
    sc = simpleCubic(name)
    
    logging.info("Creating the geometry ...")
    sc.geometryCreate(alpha)
    
    logging.info("Extracting boundaries ...")
    sc.boundaryCreate(direction)
    
    logging.info("Creating the mesh ...")
    sc.meshCreate(2, {
        "thickness": 0.02,
        "number": 2,
        "stretch": 1.1
    })
    sc.meshCompute()
    
    logging.info("Exporting the mesh ...")
    sc.meshExport(buildpath)
    
    end_time = time.monotonic()
    logging.info("Elapsed time: {}".format(timedelta(seconds=end_time - start_time)))
    logging.info("Done.")
    
    if salome.sg.hasDesktop():
        salome.sg.updateObjBrowser()
