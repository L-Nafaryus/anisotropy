# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from anisotropy.salomepl.geometry import StructureGeometry
from numpy import pi, sqrt, cos, arccos, fix 
import logging

class BodyCentered(StructureGeometry):
    @property
    def name(self):
        """Shape name.
        """
        return "bodyCentered"
    
    @property
    def L(self):
        return self.r0 * 4 / sqrt(3)

    @property
    def thetaMin(self):
        return 0.01
    
    @property
    def thetaMax(self):
        return 0.18
    
    @property
    def fillets(self):
        analytical = self.r0 * (sqrt(2) / sqrt(1 - cos(pi - 2 * arccos(sqrt(2 / 3)))) - 
            1 / (1 - self.theta))
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
            diag = self.L * sqrt(2)
            height = self.L

            point = []
            xl = sqrt(diag ** 2 + diag ** 2) * 0.5
            yw = xl
            zh = height

            scale = 100
            oo = self.geo.MakeVertex(0, 0, 0)
            spos1 = (0, 0, 0)
            spos2 = (0, 0, 0)

            ###
            #   Bounding box
            ##
            if self.direction == [1, 0, 0]:
                sk = self.geo.Sketcher3D()
                sk.addPointsAbsolute(xl, 0, 0)
                sk.addPointsAbsolute(0, yw, 0)
                sk.addPointsAbsolute(0, yw, zh)
                sk.addPointsAbsolute(xl, 0, zh)
                sk.addPointsAbsolute(xl, 0, 0)

                inletface = self.geo.MakeFaceWires([sk.wire()], True)
                vecflow = self.geo.GetNormal(inletface)
                poreCell = self.geo.MakePrismVecH(inletface, vecflow, diag)

            elif self.direction == [0, 0, 1]:
                sk = self.geo.Sketcher3D()
                sk.addPointsAbsolute(0, yw, 0)
                sk.addPointsAbsolute(xl, 0, 0)
                sk.addPointsAbsolute(2 * xl, yw, 0)
                sk.addPointsAbsolute(xl, 2 * yw, 0)
                sk.addPointsAbsolute(0, yw, 0)

                inletface = self.geo.MakeFaceWires([sk.wire()], True)
                vecflow = self.geo.GetNormal(inletface)
                poreCell = self.geo.MakePrismVecH(inletface, vecflow, zh)

            
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
            oo = self.geo.MakeVertex(0, 0, 0)
            spos1 = (0, 0, 0)
            spos2 = (0, 0, 0)

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
        #   Lattice
        ##
        ox = self.geo.MakeVectorDXDYDZ(1, 0, 0)
        oy = self.geo.MakeVectorDXDYDZ(0, 1, 0)
        oz = self.geo.MakeVectorDXDYDZ(0, 0, 1)
        xy = self.geo.MakeVectorDXDYDZ(1, 1, 0)
        xmy = self.geo.MakeVectorDXDYDZ(1, -1, 0)

        grain = self.geo.MakeSpherePntR(self.geo.MakeVertex(*spos1), self.radius)
        lattice1 = self.geo.MakeMultiTranslation2D(grain, ox, self.L, xn, oy, self.L, yn)
        lattice1 = self.geo.MakeMultiTranslation1D(lattice1, oz, self.L, zn)

        lattice2 = self.geo.MakeTranslation(lattice1, -0.5 * self.L, -0.5 * self.L, -0.5 * self.L)
        
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
        self.shape = self.geo.MakeCutList(poreCell, [grains])
        self.shape = self.geo.MakeScaleTransform(self.shape, oo, 1 / scale, theName = self.name)
        
        isValid, _ = self.isValid()
        
        if not isValid:
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
 

