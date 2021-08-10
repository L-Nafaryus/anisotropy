from math import pi, sqrt

class FaceCentered(object):
    def __init__(self, **kwargs):

        self.direction = kwargs.get("direction", [1, 0, 0])
        self.theta = kwargs.get("theta", 0.01)
        self.L = kwargs.get("L", 1)
        self.r0 = kwargs.get("r0", self.L * sqrt(2) / 4)
        self.radius = kwargs.get("radius", self.r0 / (1 - self.theta)) 
        self.filletsEnabled = kwargs.get("filletsEnabled", False)
        self.fillets = kwargs.get("fillets", 0)


    def build(self):
        import salomepl

        geompy = salomepl.geometry.getGeom()

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
            oo = geompy.MakeVertex(0, 0, 0)
            spos1 = (-width * (xn - 1), 0, -width * (zn - 2))
            spos2 = (-width * xn, 0, -width * (zn - 1))

            ###
            #   Bounding box
            ##
            if self.direction == [1, 0, 0]:
                sk = geompy.Sketcher3D()
                sk.addPointsAbsolute(0, 0, -zh)
                sk.addPointsAbsolute(-xl, yw, -zh)
                sk.addPointsAbsolute(-xl, yw, zh)
                sk.addPointsAbsolute(0, 0, zh)
                sk.addPointsAbsolute(0, 0, -zh)

                inletface = geompy.MakeFaceWires([sk.wire()], True)
                vecflow = geompy.GetNormal(inletface)
                poreCell = geompy.MakePrismVecH(inletface, vecflow, length)

            elif self.direction == [0, 0, 1]:
                sk = geompy.Sketcher3D()
                sk.addPointsAbsolute(0, 0, -zh)
                sk.addPointsAbsolute(xl, yw, -zh)
                sk.addPointsAbsolute(0, 2 * yw, -zh)
                sk.addPointsAbsolute(-xl, yw, -zh)
                sk.addPointsAbsolute(0, 0, -zh)

                inletface = geompy.MakeFaceWires([sk.wire()], True)
                vecflow = geompy.GetNormal(inletface)
                poreCell = geompy.MakePrismVecH(inletface, vecflow, 2 * zh)

            
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
            oo = geompy.MakeVertex(0, 0, 0)
            spos1 = (-width * (xn - 1), 0, -width * (zn - 2))
            spos2 = (-width * xn, 0, -width * (zn - 1))

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
        xy = geompy.MakeVectorDXDYDZ(1, 1, 0)
        xmy = geompy.MakeVectorDXDYDZ(1, -1, 0)

        grain = geompy.MakeSpherePntR(geompy.MakeVertex(*spos1), radius)
        lattice1 = geompy.MakeMultiTranslation2D(grain, xy, length, xn, xmy, length, yn)
        lattice1 = geompy.MakeMultiTranslation1D(lattice1, oz, L, zn - 1)

        grain = geompy.MakeSpherePntR(geompy.MakeVertex(*spos2), radius)
        lattice2 = geompy.MakeMultiTranslation2D(grain, xy, length, xn + 1, xmy, length, yn + 1)
        lattice2 = geompy.MakeMultiTranslation1D(lattice2, oz, L, zn)
        
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
        shape = geompy.MakeScaleTransform(shape, oo, 1 / scale, theName = "faceCentered")
        
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


