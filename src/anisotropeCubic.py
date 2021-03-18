#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
from . import geometry_utils

import GEOM
geompy = geometry_utils.getGeom()

class StructuredGrains:
    def __init__(self, radius, stackAngle, theta, layers):
        self.pos = [0, 0, 0]
        self.angle = [0, 0, 0]
        self.radius = radius
        self.theta = theta
        self.layers = layers
        
        # Parameters and dependencies
        R = self.radius / (1 - self.theta)
        
        C1 = 0.8 #fillet[0]
        C2 = 0.4 #fillet[1]
        self.theta1 = 0.01
        self.theta2 = 0.28
        
        Cf = C1 + (C2 - C1) / (self.theta2 - self.theta1) * (self.theta - self.theta1)
        R_fillet = Cf * (self.radius * math.sqrt(2) - R)
        
        ###
        stackang = [
            0.5 * math.pi - stackAngle[0], 
            0.5 * math.pi - stackAngle[1], 
            0.5 * math.pi - stackAngle[2]
        ]
        
        xvec = geompy.MakeVector(
            geompy.MakeVertex(0, 0, 0),
            geompy.MakeVertex(1, 0, 0))
        yvec = geometry_utils.rotate(xvec, [0.5 * math.pi, 0, 0])
        zvec = geometry_utils.rotate(xvec, [0, 0.5 * math.pi, 0])
        
        grain = geompy.MakeSpherePntR(geompy.MakeVertex(pos[0], pos[1], pos[2]), R)
        
        xstack = geompy.MakeMultiTranslation1D(grain, xvec, 2 * self.radius, self.layers[0])
        ystack = geompy.MakeMultiTranslation1D(xgrain, yvec, 2 * self.radius, self.layers[1])
        zstack = geompy.MakeMultiTranslation1D(ygrain, zvec, 2 * self.radius, self.layers[2])
        
        # Correct position to zero
        stack = geompy.MakeTranslation(zstack, -2 * self.radius, 0, 0)
        
        self.geometry = geompy.ExtractShapes(stack, geompy.ShapeType["SOLID"], True)
        self.geometry = geompy.MakeFuseList(self.geometry, False, False)
                
        if not R_fillet == 0:
            self.geometry = geompy.MakeFilletAll(self.geometry, R_fillet)


class AnisotropeCubic:
    def __init__(self, scale, grains, style):
        self.pos = [0, 0, 0]
        self.angle = [0, 0, 0]
        self.scale = scale
        self.grains = grains

        # Bounding box
        if style == 0:
            # Square
            profile = (
                geompy.Sketcher3D()
                .addPointAbsolute(0, 0, 0)
                .addPointAbsolute(0, 0, self.scale[2])
                .addPointAbsolute(0, self.scale[1], self.scale[2])
                .addPointAbsolute(0, self.scale[1], 0)
                .addPointAbsolute(0, 0, 0)
            )
            
            face = geompy.MakeFaceWires([profile.wire()], 1)

        elif style == 1:
            # Rombus
            profile = (
                geompy.Sketcher3D()
                .addPointAbsolute(self.scale[0], 0.5 * self.scale[1], 0)
                .addPointAbsolute(0.5 * self.scale[0], 0, 0.5 * self.scale[2])
                .addPointAbsolute(0, 0.5 * self.scale[1], self.scale[2])
                .addPointAbsolute(0.5 * self.scale[0], self.scale[1], 0.5 * self.scale[2])
                .addPointAbsolute(self.scale[0], 0.5 * self.scale[1], 0)
            )

            face = geompy.MakeFaceWires([profile.wire()], 1)
            face = geompy.MakeTranslation(face, 
                0.5 * self.scale[1], 0, 0)

        self.boundingbox = geompy.MakePrismVecH(face,
            geompy.MakeVectorDXDYDZ(1, 0, 0), 
            self.scale[0])
        
        # Geometry
        self.geometry = geompy.MakeCutList(box, [self.grains], True)




