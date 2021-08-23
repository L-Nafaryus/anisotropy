# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from math import pi, sqrt
from anisotropy.salomepl import geometry

class Simple(object):
    def __init__(self, **kwargs):

        self.direction = kwargs.get("direction", [1, 0, 0])
        self.theta = kwargs.get("theta", 0.01)
        self.r0 = kwargs.get("r0", 1)
        self.L = kwargs.get("L", 2 * self.r0)
        self.radius = kwargs.get("radius", self.r0 / (1 - self.theta)) 
        self.filletsEnabled = kwargs.get("filletsEnabled", False)
        self.fillets = kwargs.get("fillets", 0)


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
            
            length = self.L * sqrt(2)
            width = self.L * sqrt(2)
            height = self.L

            xl = sqrt(length ** 2 * 0.5)
            yw = xl
            zh = height

            scale = 100
            oo = geompy.MakeVertex(0, 0, 0)

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
                poreCell = geompy.MakePrismVecH(inletface, vecflow, width)

            elif self.direction == [0, 0, 1]:
                sk = geompy.Sketcher3D()
                sk.addPointsAbsolute(0, yw, 0)
                sk.addPointsAbsolute(xl, 0, 0)
                sk.addPointsAbsolute(2 * xl, yw, 0)
                sk.addPointsAbsolute(xl, 2 * yw, 0)
                sk.addPointsAbsolute(0, yw, 0)

                inletface = geompy.MakeFaceWires([sk.wire()], True)
                vecflow = geompy.GetNormal(inletface)
                poreCell = geompy.MakePrismVecH(inletface, vecflow, height)

                
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
            
            length = self.L * sqrt(2)
            width = self.L * sqrt(2)
            height = self.L

            point = []
            xl, yw, zh = -self.L - self.L / 6, -self.L - self.L / 6, -self.L / 6
            point.append((L + xl, self.L + yw, self.L + zh))
            point.append((5 * self.L / 3 + xl, 2 * self.L / 3 + yw, 2 * self.L / 3 + zh))
            point.append((2 * self.L + xl, self.L + yw, 0 + zh))
            point.append((5 * self.L / 3 + xl, 5 * self.L / 3 + yw, -self.L / 3 + zh))
            point.append((L + xl, 2 * self.L + yw, 0 + zh))
            point.append((2 * self.L / 3 + xl, 5 * self.L / 3 + yw, 2 * self.L / 3 + zh))
            point.append((L + xl, self.L + yw, self.L + zh))

            scale = 100
            oo = geompy.MakeVertex(0, 0, 0)

            ###
            #   Bounding box
            ## 
            sk = geompy.Sketcher3D()

            for p in point:
                sk.addPointsAbsolute(*p)
            
            inletface = geompy.MakeFaceWires([sk.wire()], False)
            vecflow = geompy.GetNormal(inletface)
            poreCell = geompy.MakePrismVecH(inletface, vecflow, self.L * sqrt(3))

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

        grain = geompy.MakeSphereR(self.radius)
        lattice = geompy.MakeMultiTranslation2D(grain, ox, self.L, xn, oy, self.L, yn)
        lattice = geompy.MakeMultiTranslation1D(lattice, oz, self.L, zn)
        
        grains = geompy.ExtractShapes(lattice, geompy.ShapeType["SOLID"], True)
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
        shape = geompy.MakeScaleTransform(shape, oo, 1 / scale, theName = "simple")

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

