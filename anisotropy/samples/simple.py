# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from anisotropy.salomepl.geometry import StructureGeometry
from anisotropy.salomepl.mesh import Mesh
from numpy import pi, sqrt, fix
import logging

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
        analytical = self.r0 * (sqrt(2) - 1 / (1 - self.theta))
        # ISSUE: MakeFilletAll : Fillet can't be computed on the given shape with the given radius.
        # Temporary solution: degrade the precision (minRound <= analytical).
        rTol = 3
        minRound = fix(10 ** rTol * analytical) * 10 ** -rTol

        return minRound * self.filletScale

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


class SimpleMesh(Mesh):
    def build(self):
        algo2d = self.mesh.Triangle(algo = self.smeshBuilder.NETGEN_1D2D)
        hypo2d = algo2d.Parameters()
        hypo2d.SetMaxSize(0.1)
        hypo2d.SetMinSize(0.001)
        hypo2d.SetFineness(5)
        hypo2d.SetGrowthRate(0.3)
        hypo2d.SetNbSegPerEdge(2)
        hypo2d.SetNbSegPerRadius(3)
        hypo2d.SetChordalErrorEnabled(True)
        hypo2d.SetChordalError(0.05)
        hypo2d.SetOptimize(True)
        hypo2d.SetUseSurfaceCurvature(True)

        algo3d = self.mesh.Tetrahedron(algo = self.smeshBuilder.NETGEN_3D)
        #hypo3d = algo3d.Parameters()

        #faces = [ group for group in self.geom.groups if group.GetName() in ["inlet", "outlet"] ]
        #hypo3dVL = algo3d.ViscousLayers(...)
    

from anisotropy.openfoam.presets import ControlDict

class SimpleFlow(object): # FoamCase
    def __init__(self):
        controlDict = ControlDict()
        controlDict["startFrom"] = "latestTime"
        controlDict["endTime"] = 5000
        controlDict["writeInterval"] = 100

