# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from anisotropy.salomepl.geometry import StructureGeometry
from numpy import pi, sqrt, fix
import logging

class FaceCentered(StructureGeometry):
    @property
    def name(self):
        """Shape name.
        """
        return "faceCentered"
    
    @property
    def L(self):
        return self.r0 * 4 / sqrt(2)
        
    @property
    def thetaMin(self):
        return 0.01
    
    @property
    def thetaMax(self):
        return 0.13
    
    @property
    def fillets(self):
        analytical = self.r0 * (2 * sqrt(3) / 3 - 1 / (1 - self.theta))
        # ISSUE: MakeFilletAll : Fillet can't be computed on the given shape with the given radius.
        # Temporary solution: degrade the precision (minRound <= analytical).
        rTol = 3
        minRound = fix(10 ** rTol * analytical) * 10 ** -rTol

        return minRound
        
    def build(self):
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
            diag = self.L * sqrt(3)
            height = diag / 3

            point = []
            xl = sqrt(length ** 2 + length ** 2) * 0.5
            yw = xl
            zh = width

            scale = 100
            oo = self.geo.MakeVertex(0, 0, 0)
            spos1 = (-width * (xn - 1), 0, -width * (zn - 2))
            spos2 = (-width * xn, 0, -width * (zn - 1))

            ###
            #   Bounding box
            ##
            if self.direction == [1, 0, 0]:
                sk = self.geo.Sketcher3D()
                sk.addPointsAbsolute(0, 0, -zh)
                sk.addPointsAbsolute(-xl, yw, -zh)
                sk.addPointsAbsolute(-xl, yw, zh)
                sk.addPointsAbsolute(0, 0, zh)
                sk.addPointsAbsolute(0, 0, -zh)

                inletface = self.geo.MakeFaceWires([sk.wire()], True)
                vecflow = self.geo.GetNormal(inletface)
                poreCell = self.geo.MakePrismVecH(inletface, vecflow, length)

            elif self.direction == [0, 0, 1]:
                sk = self.geo.Sketcher3D()
                sk.addPointsAbsolute(0, 0, -zh)
                sk.addPointsAbsolute(xl, yw, -zh)
                sk.addPointsAbsolute(0, 2 * yw, -zh)
                sk.addPointsAbsolute(-xl, yw, -zh)
                sk.addPointsAbsolute(0, 0, -zh)

                inletface = self.geo.MakeFaceWires([sk.wire()], True)
                vecflow = self.geo.GetNormal(inletface)
                poreCell = self.geo.MakePrismVecH(inletface, vecflow, 2 * zh)

            self.shapeCell = poreCell
            
            inletface = self.geo.MakeScaleTransform(inletface, oo, scale)
            poreCell = self.geo.MakeScaleTransform(poreCell, oo, scale)

            faces = self.geo.ExtractShapes(poreCell, self.geo.ShapeType["FACE"], False)
            symetryface = []

            for face in faces:
                norm = self.geo.GetNormal(face)
                angle = round(self.geo.GetAngle(norm, vecflow), 0)

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
            diag = self.L * sqrt(3)
            height = diag / 3

            point = []
            xl, yw, zh = -(xn - 2) * self.L / 3, -(yn - 2) * self.L / 3, -(zn - 2) * self.L / 3
            point.append((-2 * width / 3 + xl, -2 * width / 3 + yw, width / 3 + zh))
            point.append((0 + xl, -width + yw, 0 + zh))
            point.append((width / 3 + xl, -2 * width / 3 + yw, -2 * width / 3 + zh))
            point.append((0 + xl, 0 + yw, -width + zh))
            point.append((-2 * width / 3 + xl, width / 3 + yw, -2 * width / 3 + zh))
            point.append((-width + xl, 0 + yw, 0 + zh))
            point.append((-2 * width / 3 + xl, -2 * width / 3 + yw, width / 3 + zh))

            scale = 100
            oo = self.geo.MakeVertex(0, 0, 0)
            spos1 = (-width * (xn - 1), 0, -width * (zn - 2))
            spos2 = (-width * xn, 0, -width * (zn - 1))

            ###
            #   Bounding box
            ## 
            sk = self.geo.Sketcher3D()

            for p in point:
                sk.addPointsAbsolute(*p)
            
            inletface = self.geo.MakeFaceWires([sk.wire()], False)
            vecflow = self.geo.GetNormal(inletface)
            poreCell = self.geo.MakePrismVecH(inletface, vecflow, self.L * sqrt(3))

            self.shapeCell = poreCell

            inletface = self.geo.MakeScaleTransform(inletface, oo, scale)
            poreCell = self.geo.MakeScaleTransform(poreCell, oo, scale)

            faces = self.geo.ExtractShapes(poreCell, self.geo.ShapeType["FACE"], False)
            symetryface = []

            for face in faces:
                norm = self.geo.GetNormal(face)
                angle = round(self.geo.GetAngle(norm, vecflow), 0)

                if (angle == 0 or angle == 180) and not face == inletface:
                    outletface = face
                
                else:
                    symetryface.append(face)

        else:
            raise Exception(f"Direction { self.direction } is not implemented")
        
        ###
        #   Grains
        ##
        ox = self.geo.MakeVectorDXDYDZ(1, 0, 0)
        oy = self.geo.MakeVectorDXDYDZ(0, 1, 0)
        oz = self.geo.MakeVectorDXDYDZ(0, 0, 1)
        xy = self.geo.MakeVectorDXDYDZ(1, 1, 0)
        xmy = self.geo.MakeVectorDXDYDZ(1, -1, 0)

        grain = self.geo.MakeSpherePntR(self.geo.MakeVertex(*spos1), self.radius)
        lattice1 = self.geo.MakeMultiTranslation2D(grain, xy, length, xn, xmy, length, yn)
        lattice1 = self.geo.MakeMultiTranslation1D(lattice1, oz, self.L, zn - 1)

        grain = self.geo.MakeSpherePntR(self.geo.MakeVertex(*spos2), self.radius)
        lattice2 = self.geo.MakeMultiTranslation2D(grain, xy, length, xn + 1, xmy, length, yn + 1)
        lattice2 = self.geo.MakeMultiTranslation1D(lattice2, oz, self.L, zn)
        
        grains = self.geo.ExtractShapes(lattice1, self.geo.ShapeType["SOLID"], True)
        grains += self.geo.ExtractShapes(lattice2, self.geo.ShapeType["SOLID"], True)
        grains = self.geo.MakeFuseList(grains, False, False)

        grains = self.geo.MakeScaleTransform(grains, oo, scale)
        grainsOrigin = None

        if self.filletsEnabled:
            grainsOrigin =  self.geo.MakeScaleTransform(grains, oo, 1 / scale)
            grains = self.geo.MakeFilletAll(grains, self.fillets * scale)

        self.shapeLattice = self.geo.MakeScaleTransform(grains, oo, 1 / scale)
        
        ###
        #   Shape
        ##
        #poreCell = self.geo.LimitTolerance(poreCell, 1e-12)
        #grains = self.geo.LimitTolerance(grains, 1e-12)

        self.shape = self.geo.MakeCutList(poreCell, [grains])
        self.shape = self.geo.MakeScaleTransform(self.shape, oo, 1 / scale, theName = self.name)
        
        isValid, msg = self.isValid()
        
        if not isValid:
            logging.warning(msg)
            self.heal()
            
        ###
        #   Groups
        #
        #   inlet, outlet, simetry(N), strips(optional), wall
        ##
        self.groups = []
        groupAll = self.createGroupAll(self.shape)
        
        self.groups.append(self.createGroup(self.shape, inletface, "inlet", [grains], 1 / scale))
        self.groups.append(self.createGroup(self.shape, outletface, "outlet", [grains], 1 / scale))

        for n, face in enumerate(symetryface):
            self.groups.append(self.createGroup(self.shape, face, f"symetry{ n }", [grains], 1 / scale))
 
        if self.filletsEnabled:
            shapeShell = self.geo.ExtractShapes(self.shape, self.geo.ShapeType["SHELL"], True)[0]
            self.groups.append(self.createGroup(self.shape, shapeShell, "strips", self.groups + [grainsOrigin]))

        self.groups.append(self.geo.CutListOfGroups([groupAll], self.groups, theName = "wall"))
