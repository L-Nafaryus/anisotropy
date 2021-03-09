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

        self.spheres = None

        salome.salome_init()

    def geometryCreate(self, alpha, fillet):
        """
        Create the simple cubic geometry.

        Parameters:
            alpha (float): Sphere intersection parameter which used for cutting spheres from box.
                
                Radius = R0 / (1 - alpha)
                Should be from 0.01 to 0.28

            fillet (list): Fillet coefficient.
                
                [fillet1, fillet2]
                0 <= fillet <= 1
                if fillet = [0, 0] then R_fillet = 0

        Returns:
            Configured geometry.
        """

        geompy = geomBuilder.New()
        
        # Parameters
        R0 = 1
        R = R0 / (1 - alpha)
        
        C1 = fillet[0]
        C2 = fillet[1]
        alpha1 = 0.01
        alpha2 = 0.28
        
        Cf = C1 + (C2 - C1) / (alpha2 - alpha1) * (alpha - alpha1)
        R_fillet = Cf * (R0 * math.sqrt(2) - R)
        
        logging.info("geometryCreate: alpha = {}".format(alpha))
        logging.info("geometryCreate: R_fillet = {}".format(R_fillet))

        # xyz axes
        axes = [
            geompy.MakeVectorDXDYDZ(1, 0, 0),
            geompy.MakeVectorDXDYDZ(0, 1, 0),
            geompy.MakeVectorDXDYDZ(0, 0, 1)
        ]
        
        # Main box
        size = [2 * math.sqrt(2), 2 * math.sqrt(2), 2]
        angle = [0, 0, 45]
        pos = [2, 0, 0]
        
        box = geompy.MakeBoxDXDYDZ(size[0], size[1], size[2])

        for n in range(3):
            box = geompy.MakeRotation(box, axes[n], angle[n] * math.pi / 180.0)

        box = geompy.MakeTranslation(box, pos[0], pos[1], pos[2])
        
        #[x, y, z, _, _, _, _, _, _] = geompy.GetPosition(box)
        #pos = [x, y, z]
        
        # Spheres for cutting
        sphere = geompy.MakeSpherePntR(geompy.MakeVertex(pos[0], pos[1], pos[2]), R)
        sphere = geompy.MakeMultiTranslation2D(sphere, None, 2 * R0, 3, None, 2 * R0, 3)
        sphere = geompy.MakeTranslation(sphere, -2 * R0, 0, 0)
        sphere2 = geompy.MakeTranslation(sphere, 0, 0, 2 * R0)
        sphere3 = geompy.MakeTranslation(sphere2, 0, 0, 2 * R0)
        
        sphere = geompy.ExtractShapes(sphere, geompy.ShapeType["SOLID"], True)
        sphere2 = geompy.ExtractShapes(sphere2, geompy.ShapeType["SOLID"], True)
        sphere3 = geompy.ExtractShapes(sphere3, geompy.ShapeType["SOLID"], True)

        sphere = geompy.MakeFuseList(sphere + sphere2 + sphere3, False, False)

                
        if not R_fillet == 0:
            sphere = geompy.MakeFilletAll(sphere, R_fillet)
        
        self.spheres = sphere

        #else:
        #    sphere = sphere + sphere2 + sphere3 #geompy.MakeCompound(sphere + sphere2 + sphere3)
        
        # geompy.RemoveExtraEdges(obj, True)
        self.geometry = geompy.MakeCutList(box, [sphere], True)
        self.geometrybbox = box

        geompy.addToStudy(self.geometry, self.name)
        
        # Rombus
        h = 2
        
        Vertex_2 = geompy.MakeVertex(0, 0, 4)
        Vertex_1 = geompy.MakeVertex(2, 0, 2)
        Vertex_3 = geompy.MakeVertex(2, 2, 0)
        Vertex_4 = geompy.MakeVertex(0, 2, 2)
        Edge_1 = geompy.MakeEdge(Vertex_2, Vertex_1)
        Edge_2 = geompy.MakeEdge(Vertex_1, Vertex_3)
        Edge_3 = geompy.MakeEdge(Vertex_3, Vertex_4)
        Edge_4 = geompy.MakeEdge(Vertex_4, Vertex_2)
        Face_1 = geompy.MakeFaceWires([Edge_1, Edge_2, Edge_3, Edge_4], 1)


        #sk = geompy.Sketcher3D()
        #sk.addPointsAbsolute(0, 0, h * 2)
        #sk.addPointsAbsolute(h, 0, h)
        #sk.addPointsAbsolute(h, h, 0) 
        #sk.addPointsAbsolute(0, h, h)
        #sk.addPointsAbsolute(0, 0, h * 2)

        #a3D_Sketcher_1 = sk.wire()
        #Face_1 = geompy.MakeFaceWires([a3D_Sketcher_1], 1)
        Vector_1 = geompy.MakeVectorDXDYDZ(1, 1, 0)
        rombusbbox = geompy.MakePrismVecH(Face_1, Vector_1, round(2 * math.sqrt(2), 14))

        geompy.addToStudy(rombusbbox, "rombusbbox")
        
        self.rombus = geompy.MakeCutList(rombusbbox, [sphere], True)
        self.rombusbbox = rombusbbox

        geompy.addToStudy(self.rombus, "rombus")

        return self.geometry

    def boundaryCreate(self, direction):
        """
        Create the boundary faces from the geometry.

        Parameters:
            direction (str): Direction of the flow.

                '001' for the flow with normal vector (0, 0, 1) to face.
                '100' for the flow with normal vector (1, 0, 0) to face.
                '111' for (1, 1, 1)

        Returns:
            boundary (dict):

            {
                "inlet": <GEOM._objref_GEOM_Object>,
                "outlet": <GEOM._objref_GEOM_Object>,
                "symetryPlane": <GEOM._objref_GEOM_Object>,
                "wall": <GEOM._objref_GEOM_Object>
            }

        """
        geompy = geomBuilder.New() 
        rot = [0, 0, 45]
        buffergeometry = self.geometry

        # Direction vector
        [x, y, z, _, _, _, _, _, _] = geompy.GetPosition(self.geometry)
        angle = []
        center = geompy.MakeVertex(x, y, z)
        dvec = geompy.MakeVector(center,
            geompy.MakeVertexWithRef(center,
                D[0] * math.cos(angle[0]), 
                D[1] * math.sin(angle[1]), 
                D[2] * math.sin(angle[2])))


        ##
        if direction == "001":
            center = geompy.MakeVertex(2, 2, 1)

            norm = geompy.MakeVector(center, 
                geompy.MakeVertexWithRef(center, 0, 0, 1))
            
            bnorm = geompy.MakeVector(center, 
                geompy.MakeVertexWithRef(center, 
                    -math.cos((90 + rot[2]) * math.pi / 180.0), 
                    math.sin((90 + rot[2]) * math.pi / 180.0), 0)) 
            
            vnorm = geompy.MakeVector(center, 
                geompy.MakeVertexWithRef(center, 
                    -math.cos((0 + rot[2]) * math.pi / 180.0), 
                    math.sin((0 + rot[2]) * math.pi / 180.0), 0))  

            vstep = 1
            hstep = math.sqrt(2)
        
        elif direction == "100":
            center = geompy.MakeVertex(2, 2, 1)

            norm = geompy.MakeVector(center, 
                geompy.MakeVertexWithRef(center, 
                    -math.cos((90 + rot[2]) * math.pi / 180.0), 
                    math.sin((90 + rot[2]) * math.pi / 180.0), 0))

            bnorm = geompy.MakeVector(center, 
                geompy.MakeVertexWithRef(center, 0, 0, 1))

            vnorm = geompy.MakeVector(center, 
                geompy.MakeVertexWithRef(center, 
                    -math.cos((0 + rot[2]) * math.pi / 180.0), 
                    math.sin((0 + rot[2]) * math.pi / 180.0), 0))  

            vstep = math.sqrt(2)
            hstep = 1

        elif direction == "111":
            center = geompy.MakeVertex(2, 2, 2)
            self.geometry = self.rombus

            norm = geompy.MakeVector(center,
                geompy.MakeVertexWithRef(center, 1, 1, 1))
                    #-math.cos((90 + rot[2]) * math.pi / 180.0),
                    #math.sin((90 + rot[2]) * math.pi / 180.0), math.sqrt(2) / 2))
            
            bnorm = geompy.MakeVector(center, 
                geompy.MakeVertexWithRef(center, 1, -1, 1))
                #    -math.cos((90 + rot[2]) * math.pi / 180.0), 
                #    math.sin((90 + rot[2]) * math.pi / 180.0), 0)) 
            
            vnorm = geompy.MakeVector(center, 
                geompy.MakeVertexWithRef(center, -1, 1, 1))
                    #-math.cos((0 + rot[2]) * math.pi / 180.0), 
                    #math.sin((0 + rot[2]) * math.pi / 180.0), 0)) 

            vstep = math.sqrt(2)
            hstep = 1 
        
        logging.info("boundaryCreate: direction = {}".format(direction))

        geompy.addToStudy(norm, "normalvector")
        geompy.addToStudy(bnorm, "bnorm")
        geompy.addToStudy(vnorm, "vnorm")

        if direction == "111":
            box = self.rombus

        else:
            box = self.geometrybbox
        
        planes = geompy.ExtractShapes(box, geompy.ShapeType["FACE"], True)
        inletplane = []
        outletplane = []
        hplanes = []
        
        fwplanes = []
        bwplanes = []
        lplanes = []
        rplanes = []

        for plane in planes:
            planeNorm = geompy.GetNormal(plane)
            
            angle = round(abs(geompy.GetAngle(planeNorm, norm)), 0)

            if angle == 0:
                outletplane.append(plane)    

            elif angle == 180:
                inletplane.append(plane)

            elif direction == "111" and (angle == 109 or angle == 71):
                #hplanes.append(plane)

                bangle = round(abs(geompy.GetAngle(planeNorm, bnorm)), 0)
                #logging.info("bangle = {}".format(bangle))

                if bangle == 0:
                    fwplanes.append(plane)

                elif bangle == 180:
                    bwplanes.append(plane)

                vangle = round(abs(geompy.GetAngle(planeNorm, vnorm)), 0)
                #logging.info("vangle = {}".format(vangle))

                if vangle == 0:
                    lplanes.append(plane)

                elif vangle == 180:
                    rplanes.append(plane)    

            elif direction == "100" or direction == "001":
                if angle == 90:
                    #hplanes.append(plane)
                    
                    bangle = round(abs(geompy.GetAngle(planeNorm, bnorm)), 0)
                    #logging.info("bangle = {}".format(bangle))

                    if bangle == 0:
                        fwplanes.append(plane)

                    elif bangle == 180:
                        bwplanes.append(plane)

                    vangle = round(abs(geompy.GetAngle(planeNorm, vnorm)), 0)
                    #logging.info("vangle = {}".format(vangle))

                    if vangle == 0:
                        lplanes.append(plane)

                    elif vangle == 180:
                        rplanes.append(plane)


        if salome.sg.hasDesktop():
            salome.sg.updateObjBrowser()

        logging.info("boundaryCreate: inletplanes = {}, outletplanes = {}, hplanes = {}".format(
            len(inletplane), len(outletplane), len(hplanes)))

        logging.info("boundaryCreate: fwplanes = {}, bwplanes = {}, lplanes = {}, rplanes = {}".format(
            len(fwplanes), len(bwplanes), len(lplanes), len(rplanes)))
        
        
        def createGroup(planelist, name):
            gr = geompy.CreateGroup(self.geometry, geompy.ShapeType["FACE"], name)
            
            grcomp = geompy.MakeCompound(planelist)
            grcut = geompy.MakeCutList(grcomp, [self.spheres], True)

            gip = geompy.GetInPlace(self.geometry, grcut, True)
            faces = geompy.SubShapeAll(gip, geompy.ShapeType["FACE"])
            geompy.UnionList(gr, faces)

            return gr

        
        # Main groups
        inlet = createGroup(inletplane, "inlet")

        outlet = createGroup(outletplane, "outlet")

        #symetryPlane = createGroup(hplanes, "symetryPlane")
        symetryPlaneFW = createGroup(fwplanes, "symetryPlaneFW")
        symetryPlaneBW = createGroup(bwplanes, "symetryPlaneBW")
        symetryPlaneL = createGroup(lplanes, "symetryPlaneL")
        symetryPlaneR = createGroup(rplanes, "symetryPlaneR")

        # wall
        allgroup = geompy.CreateGroup(self.geometry, geompy.ShapeType["FACE"])
        faces = geompy.SubShapeAllIDs(self.geometry, geompy.ShapeType["FACE"]) 
        geompy.UnionIDs(allgroup, faces)
        wall = geompy.CutListOfGroups([allgroup], 
            [inlet, outlet, symetryPlaneFW, symetryPlaneBW, symetryPlaneL, symetryPlaneR], "wall")
        
        self.boundary = {
            "inlet": inlet,
            "outlet": outlet,
            "symetryPlaneFW": symetryPlaneFW,
            "symetryPlaneBW": symetryPlaneBW,
            "symetryPlaneL": symetryPlaneL,
            "symetryPlaneR": symetryPlaneR,
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
        Fineness = { 
            0: "Very coarse",
            1: "Coarse",
            2: "Moderate",
            3: "Fine",
            4: "Very fine"
        }[fineness]

        logging.info("meshCreate: mesh fineness - {}".format(Fineness))

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
            logging.info("meshCreate: viscous layers params - thickness = {}, number = {}, stretch factor = {}".format(
                viscousLayers["thickness"], viscousLayers["number"], viscousLayers["stretch"]))

            vlayer = netgen.ViscousLayers(viscousLayers["thickness"], 
                                          viscousLayers["number"], 
                                          viscousLayers["stretch"], 
                                          [self.boundary["inlet"], self.boundary["outlet"]],
                                          1, smeshBuilder.NODE_OFFSET)
        
        else:
            logging.info("meshCreate: viscous layers are disabled")

        for name, boundary in self.boundary.items():
            mesh.GroupOnGeom(boundary, "{}_".format(name), SMESH.FACE)

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
    sc.geometryCreate(alpha, [0, 0])
    
    logging.info("Extracting boundaries ...")
    sc.boundaryCreate(direction)
    
    logging.info("Creating the mesh ...")
    sc.meshCreate(2) #, {
    #    "thickness": 0.001,
    #    "number": 1,
    #    "stretch": 1.1
    #})
    sc.meshCompute()
    
    logging.info("Exporting the mesh ...")
    sc.meshExport(buildpath)
    
    end_time = time.monotonic()
    logging.info("Elapsed time: {}".format(timedelta(seconds=end_time - start_time)))
    logging.info("Done.")
    
    if salome.sg.hasDesktop():
        salome.sg.updateObjBrowser()
