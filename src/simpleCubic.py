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
import .gutils, .mutils

class simpleCubic:
    def __init__(self, alpha, fillet, name = None):
        self.name = name if type(name) != None else "simpleCubic"
        
        self.scale = None
        self.angle = None
        self.pos = None

        self.geometry = None
        self.geometrybbox = None
        self.mesh = None
        self.boundary = None
        
        self.geometry2 = None
        self.geometry2bbox = None

        self.grains = None

        salome.salome_init()

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

        self.scale = [2 * math.sqrt(2), 2 * math.sqrt(2), 2]
        self.angle = [0, 0, 0.25 * math.pi]
        self.pos = [2, 0, 0]
        
        # Box
        box = geompy.MakeBoxDXDYDZ(scale[0], scale[1], scale[2])
        box = rotate(box, angle)
        box = geompy.MakeTranslation(box, pos[0], pos[1], pos[2])
        
        self.geometrybbox = box
        
        # Grains
        layer1 = geompy.MakeSpherePntR(geompy.MakeVertex(pos[0], pos[1], pos[2]), R)
        layer1 = geompy.MakeMultiTranslation2D(layer1, None, 2 * R0, 3, None, 2 * R0, 3)
        layer1 = geompy.MakeTranslation(layer1, -2 * R0, 0, 0)
        layer2 = geompy.MakeTranslation(layer1, 0, 0, 2 * R0)
        layer3 = geompy.MakeTranslation(layer2, 0, 0, 2 * R0)
        
        layer1 = geompy.ExtractShapes(layer1, geompy.ShapeType["SOLID"], True)
        layer2 = geompy.ExtractShapes(layer2, geompy.ShapeType["SOLID"], True)
        layer3 = geompy.ExtractShapes(layer3, geompy.ShapeType["SOLID"], True)
        
        self.grains = layer1 + layer2 + layer3

        self.grains = geompy.MakeFuseList(self.grains, False, False)

                
        if not R_fillet == 0:
            self.grains = geompy.MakeFilletAll(self.grains, R_fillet)
        
        # Geometry 1
        self.geometry = geompy.MakeCutList(box, [self.grains], True)
        
        # Rhombohedron
        h = 2
        
        sk = geompy.Sketcher3D()
        sk.addPointsAbsolute(0, 0, h * 2)
        sk.addPointsAbsolute(h, 0, h)
        sk.addPointsAbsolute(h, h, 0) 
        sk.addPointsAbsolute(0, h, h)
        sk.addPointsAbsolute(0, 0, h * 2)

        rhombus = sk.wire()
        rhombus = geompy.MakeFaceWires([rombus], 1)
        vec = geompy.MakeVectorDXDYDZ(1, 1, 0)
        rhombohedron = geompy.MakePrismVecH(rombus, vec, self.scale[0])
        
        self.geometry2bbox = rhombohedron
        
        # Geometry 2
        self.geometry2 = geompy.MakeCutList(rhombohedron, [self.grains], True)
        
        # Debug study
        geompy.addToStudy(self.grains, "grains")
        geompy.addToStudy(self.geometry, self.name)
        geompy.addToStudy(self.geometrybbox, "bbox 1")
        geompy.addToStudy(self.geometry2, "geometry 2")
        geompy.addToStudy(self.geometry2bbox, "bbox 2")


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
    logging.info("Creating the geometry ...")
    sc = simpleCubic(alpha, [0, 0], name)
    
    logging.info("Extracting boundaries ...")
    boundary = sc.boundaryCreate(sc.geometry, direction, sc.grains)
    
    logging.info("Creating the mesh ...")
    mesh = sc.meshCreate(sc.geometry, boundary, 2) #, {
    #    "thickness": 0.001,
    #    "number": 1,
    #    "stretch": 1.1
    #})
    meshCompute(mesh)
    
    logging.info("Exporting the mesh ...")
    meshExport(mesh, buildpath)
    
    end_time = time.monotonic()
    logging.info("Elapsed time: {}".format(timedelta(seconds=end_time - start_time)))
    logging.info("Done.")
    
    if salome.sg.hasDesktop():
        salome.sg.updateObjBrowser()
