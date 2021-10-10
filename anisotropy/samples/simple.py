# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from anisotropy.samples.structure import StructureGeometry
from math import pi, sqrt

class Simple(StructureGeometry):
    @property
    def name(self):
        """Shape name.
        """
        return "simple"
    
    @property
    def L(self):
        return 2 * self.r0
    
    @property
    def thetaMin(self):
        return 0.01
    
    @property
    def thetaMax(self):
        return 0.28
    
    @property
    def fillets(self):
        if self.direction == [1.0, 1.0, 1.0]:
            C1, C2 = 0.8, 0.5
            Cf = C1 + (C2 - C1) / (self.thetaMax - self.thetaMin) * (self.theta - self.thetaMin)
            delta = 0.2
            
            return delta - Cf * (self.radius - self.r0)
        
        else:
            C1, C2 = 0.8, 0.5
            Cf = C1 + (C2 - C1) / (self.thetaMax - self.thetaMin) * (self.theta - self.thetaMin)
            delta = 0.2
            
            return delta - Cf * (self.radius - self.r0)
            

    def build(self):
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
            oo = self.geo.MakeVertex(0, 0, 0)

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
                poreCell = self.geo.MakePrismVecH(inletface, vecflow, width)

            elif self.direction == [0, 0, 1]:
                sk = self.geo.Sketcher3D()
                sk.addPointsAbsolute(0, yw, 0)
                sk.addPointsAbsolute(xl, 0, 0)
                sk.addPointsAbsolute(2 * xl, yw, 0)
                sk.addPointsAbsolute(xl, 2 * yw, 0)
                sk.addPointsAbsolute(0, yw, 0)

                inletface = self.geo.MakeFaceWires([sk.wire()], True)
                vecflow = self.geo.GetNormal(inletface)
                poreCell = self.geo.MakePrismVecH(inletface, vecflow, height)

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
            
            length = self.L * sqrt(2)
            width = self.L * sqrt(2)
            height = self.L

            point = []
            xl, yw, zh = -self.L - self.L / 6, -self.L - self.L / 6, -self.L / 6
            point.append((self.L + xl, self.L + yw, self.L + zh))
            point.append((5 * self.L / 3 + xl, 2 * self.L / 3 + yw, 2 * self.L / 3 + zh))
            point.append((2 * self.L + xl, self.L + yw, 0 + zh))
            point.append((5 * self.L / 3 + xl, 5 * self.L / 3 + yw, -self.L / 3 + zh))
            point.append((self.L + xl, 2 * self.L + yw, 0 + zh))
            point.append((2 * self.L / 3 + xl, 5 * self.L / 3 + yw, 2 * self.L / 3 + zh))
            point.append((self.L + xl, self.L + yw, self.L + zh))

            scale = 100
            oo = self.geo.MakeVertex(0, 0, 0)

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

        grain = self.geo.MakeSphereR(self.radius)
        lattice = self.geo.MakeMultiTranslation2D(grain, ox, self.L, xn, oy, self.L, yn)
        lattice = self.geo.MakeMultiTranslation1D(lattice, oz, self.L, zn)
        
        grains = self.geo.ExtractShapes(lattice, self.geo.ShapeType["SOLID"], True)
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
