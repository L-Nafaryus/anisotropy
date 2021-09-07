# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from math import pi, sqrt
from anisotropy.salomepl import geometry

class BodyCentered(object):
    def __init__(self, **kwargs):

        self.direction = kwargs.get("direction", [1, 0, 0])
        self.theta = kwargs.get("theta", 0.01)
        self.L = kwargs.get("L", 1)
        self.r0 = kwargs.get("r0", self.L * sqrt(3) / 4)
        self.radius = kwargs.get("radius", self.r0 / (1 - self.theta)) 
        self.filletsEnabled = kwargs.get("filletsEnabled", False)
        self.fillets = kwargs.get("fillets", 0)
        self.volumeCell = None


    def build(self):

        geompy = geometry.getGeom()

        ###
        #   Pore Cell
        ##
        if self.direction in [[1, 0, 0], [0, 0, 1]]:
            ###
            #   Parameters
            ##
            xn, yn, zn = 3, 3, 3 
            
            length = 2 * self.r0
            width = self.L / 2
            diag = self.L * sqrt(2)
            height = self.L

            point = []
            xl = sqrt(diag ** 2 + diag ** 2) * 0.5
            yw = xl
            zh = height

            scale = 100
            oo = geompy.MakeVertex(0, 0, 0)
            spos1 = (0, 0, 0)
            spos2 = (0, 0, 0)

            ###
            #   Bounding box
            ##
            if self.direction == [1, 0, 0]:
                sk = geompy.Sketcher3D()
                sk.addPointsAbsolute(xl, 0, 0)
                sk.addPointsAbsolute(0, yw, 0)
                sk.addPointsAbsolute(0, yw, zh)
                sk.addPointsAbsolute(xl, 0, zh)
                sk.addPointsAbsolute(xl, 0, 0)

                inletface = geompy.MakeFaceWires([sk.wire()], True)
                vecflow = geompy.GetNormal(inletface)
                poreCell = geompy.MakePrismVecH(inletface, vecflow, diag)

            elif self.direction == [0, 0, 1]:
                sk = geompy.Sketcher3D()
                sk.addPointsAbsolute(0, yw, 0)
                sk.addPointsAbsolute(xl, 0, 0)
                sk.addPointsAbsolute(2 * xl, yw, 0)
                sk.addPointsAbsolute(xl, 2 * yw, 0)
                sk.addPointsAbsolute(0, yw, 0)

                inletface = geompy.MakeFaceWires([sk.wire()], True)
                vecflow = geompy.GetNormal(inletface)
                poreCell = geompy.MakePrismVecH(inletface, vecflow, zh)

            [_, _, self.volumeCell] = geompy.BasicProperties(poreCell, theTolerance = 1e-06)
            
            inletface = geompy.MakeScaleTransform(inletface, oo, scale)
            poreCell = geompy.MakeScaleTransform(poreCell, oo, scale)

            faces = geompy.ExtractShapes(poreCell, geompy.ShapeType["FACE"], False)
            symetryface = []

            for face in faces:
                norm = geompy.GetNormal(face)
                angle = round(geompy.GetAngle(norm, vecflow), 0)

                if (angle == 0 or angle == 180) and not face == inletface:
                    outletface = face
        
                else:
                    symetryface.append(face)
    
        elif self.direction == [1, 1, 1]:
            ###
            #   Parameters
            ##
            xn, yn, zn = 3, 3, 3 
            
            length = 2 * self.r0
            width = self.L / 2
            diag = self.L * sqrt(2)
            height = diag / 3

            point = []
            xl, yw, zh = -self.L / 4, -self.L / 4, -self.L / 4
            point.append((self.L / 3 + xl, self.L / 3 + yw, 4 * self.L / 3 + zh))
            point.append((self.L + xl, 0 + yw, self.L + zh))
            point.append((4 * self.L / 3 + xl, self.L / 3 + yw, self.L / 3 + zh))
            point.append((self.L + xl, self.L + yw, 0 + zh))
            point.append((self.L / 3 + xl, 4 * self.L / 3 + yw, self.L / 3 + zh))
            point.append((0 + xl, self.L + yw, self.L + zh))
            point.append((self.L / 3 + xl, self.L / 3 + yw, 4 * self.L / 3 + zh))

            scale = 100
            oo = geompy.MakeVertex(0, 0, 0)
            spos1 = (0, 0, 0)
            spos2 = (0, 0, 0)

            ###
            #   Bounding box
            ## 
            sk = geompy.Sketcher3D()

            for p in point:
                sk.addPointsAbsolute(*p)
            
            inletface = geompy.MakeFaceWires([sk.wire()], False)
            vecflow = geompy.GetNormal(inletface)
            poreCell = geompy.MakePrismVecH(inletface, vecflow, self.L * sqrt(3))

            [_, _, self.volumeCell] = geompy.BasicProperties(poreCell, theTolerance = 1e-06)

            inletface = geompy.MakeScaleTransform(inletface, oo, scale)
            poreCell = geompy.MakeScaleTransform(poreCell, oo, scale)

            faces = geompy.ExtractShapes(poreCell, geompy.ShapeType["FACE"], False)
            symetryface = []

            for face in faces:
                norm = geompy.GetNormal(face)
                angle = round(geompy.GetAngle(norm, vecflow), 0)

                if (angle == 0 or angle == 180) and not face == inletface:
                    outletface = face
                
                else:
                    symetryface.append(face)

        else:
            raise Exception(f"Direction { self.direction } is not implemented")
        
        ###
        #   Grains
        ##
        ox = geompy.MakeVectorDXDYDZ(1, 0, 0)
        oy = geompy.MakeVectorDXDYDZ(0, 1, 0)
        oz = geompy.MakeVectorDXDYDZ(0, 0, 1)
        xy = geompy.MakeVectorDXDYDZ(1, 1, 0)
        xmy = geompy.MakeVectorDXDYDZ(1, -1, 0)

        grain = geompy.MakeSpherePntR(geompy.MakeVertex(*spos1), self.radius)
        lattice1 = geompy.MakeMultiTranslation2D(grain, ox, self.L, xn, oy, self.L, yn)
        lattice1 = geompy.MakeMultiTranslation1D(lattice1, oz, self.L, zn)

        #grain = geompy.MakeSpherePntR(geompy.MakeVertex(*spos2), radius)
        #lattice2 = geompy.MakeMultiTranslation2D(grain, xy, length, xn + 1, xmy, length, yn + 1)
        #lattice2 = geompy.MakeMultiTranslation1D(lattice2, oz, L, zn)
        lattice2 = geompy.MakeTranslation(lattice1, 0.5 * self.L, 0.5 * self.L, 0.5 * self.L)
        
        grains = geompy.ExtractShapes(lattice1, geompy.ShapeType["SOLID"], True)
        grains += geompy.ExtractShapes(lattice2, geompy.ShapeType["SOLID"], True)
        grains = geompy.MakeFuseList(grains, False, False)

        grains = geompy.MakeScaleTransform(grains, oo, scale)
        grainsOrigin = None

        if self.filletsEnabled:
            grainsOrigin =  geompy.MakeScaleTransform(grains, oo, 1 / scale)
            grains = geompy.MakeFilletAll(grains, self.fillets * scale)

        ###
        #   Groups
        ##
        shape = geompy.MakeCutList(poreCell, [grains])
        shape = geompy.MakeScaleTransform(shape, oo, 1 / scale, theName = "bodyCentered")

        sall = geompy.CreateGroup(shape, geompy.ShapeType["FACE"])
        geompy.UnionIDs(sall,
            geompy.SubShapeAllIDs(shape, geompy.ShapeType["FACE"]))

        inlet = geompy.CreateGroup(shape, geompy.ShapeType["FACE"], theName = "inlet")
        inletshape = geompy.MakeCutList(inletface, [grains])
        inletshape = geompy.MakeScaleTransform(inletshape, oo, 1 / scale)
        geompy.UnionList(inlet, geompy.SubShapeAll(
            geompy.GetInPlace(shape, inletshape, True), geompy.ShapeType["FACE"]))

        outlet = geompy.CreateGroup(shape, geompy.ShapeType["FACE"], theName = "outlet")
        outletshape = geompy.MakeCutList(outletface, [grains])
        outletshape = geompy.MakeScaleTransform(outletshape, oo, 1 / scale)
        geompy.UnionList(outlet, geompy.SubShapeAll(
            geompy.GetInPlace(shape, outletshape, True), geompy.ShapeType["FACE"]))
        
        symetry = []
        for (n, face) in enumerate(symetryface):
            name = "symetry" + str(n)
            symetry.append(geompy.CreateGroup(shape, geompy.ShapeType["FACE"], theName = name))
            symetryshape = geompy.MakeCutList(face, [grains])
            symetryshape = geompy.MakeScaleTransform(symetryshape, oo, 1 / scale)
            geompy.UnionList(symetry[n], geompy.SubShapeAll(
                geompy.GetInPlace(shape, symetryshape, True), geompy.ShapeType["FACE"]))

        groups = []
        groups.append(inlet)
        groups.append(outlet)
        groups.extend(symetry)

        if self.filletsEnabled:
            strips = geompy.CreateGroup(shape, geompy.ShapeType["FACE"], theName = "strips")
            shapeShell = geompy.ExtractShapes(shape, geompy.ShapeType["SHELL"], True)
            stripsShape = geompy.MakeCutList(shapeShell[0], groups + [grainsOrigin])
            geompy.UnionList(strips, geompy.SubShapeAll(
                geompy.GetInPlace(shape, stripsShape, True), geompy.ShapeType["FACE"]))
            groups.append(strips)
        
        wall = geompy.CutListOfGroups([sall], groups, theName = "wall")
        groups.append(wall)

        return shape, groups

