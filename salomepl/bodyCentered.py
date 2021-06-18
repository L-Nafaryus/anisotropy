#import salome
#salome.salome_init()

import GEOM
from salome.geom import geomBuilder
geompy = geomBuilder.New()

from math import pi, sqrt

def bodyCenteredCubic(theta = 0.01, fillet = False, direction = [1, 0, 0]):
    
    ###
    #   Parameters
    ##
    L = 1.0
    r0 = L * sqrt(3) / 4

    radius = r0 / (1 - theta)
    xn, yn, zn = 3, 3, 3 
    
    length = 2 * r0
    width = L / 2
    diag = L * sqrt(2)
    height = L

    point = []
    xl = sqrt(diag ** 2 + diag ** 2) * 0.5
    yw = xl
    zh = height

    C1, C2 = 0.3, 0.2 
    theta1, theta2 = 0.01, 0.18
    Cf = C1 + (C2 - C1) / (theta2 - theta1) * (theta - theta1)
    delta = 0.02
    filletradius = delta - Cf * (radius - r0)
    
    scale = 100
    oo = geompy.MakeVertex(0, 0, 0)
    spos1 = (0, 0, 0)
    spos2 = (0, 0, 0)

    ###
    #   Bounding box
    ##
    if direction == [1, 0, 0]:
        sk = geompy.Sketcher3D()
        sk.addPointsAbsolute(xl, 0, 0)
        sk.addPointsAbsolute(0, yw, 0)
        sk.addPointsAbsolute(0, yw, zh)
        sk.addPointsAbsolute(xl, 0, zh)
        sk.addPointsAbsolute(xl, 0, 0)

        inletface = geompy.MakeFaceWires([sk.wire()], True)
        vecflow = geompy.GetNormal(inletface)
        cubic = geompy.MakePrismVecH(inletface, vecflow, diag)

    elif direction == [0, 0, 1]:
        sk = geompy.Sketcher3D()
        sk.addPointsAbsolute(0, yw, 0)
        sk.addPointsAbsolute(xl, 0, 0)
        sk.addPointsAbsolute(2 * xl, yw, 0)
        sk.addPointsAbsolute(xl, 2 * yw, 0)
        sk.addPointsAbsolute(0, yw, 0)

        inletface = geompy.MakeFaceWires([sk.wire()], True)
        vecflow = geompy.GetNormal(inletface)
        cubic = geompy.MakePrismVecH(inletface, vecflow, zh)

    
    inletface = geompy.MakeScaleTransform(inletface, oo, scale)
    cubic = geompy.MakeScaleTransform(cubic, oo, scale)

    faces = geompy.ExtractShapes(cubic, geompy.ShapeType["FACE"], False)
    symetryface = []

    for face in faces:
        norm = geompy.GetNormal(face)
        angle = round(geompy.GetAngle(norm, vecflow), 0)

        if (angle == 0 or angle == 180) and not face == inletface:
            outletface = face
        
        else:
            symetryface.append(face)
    
    ###
    #   Grains
    ##
    ox = geompy.MakeVectorDXDYDZ(1, 0, 0)
    oy = geompy.MakeVectorDXDYDZ(0, 1, 0)
    oz = geompy.MakeVectorDXDYDZ(0, 0, 1)
    xy = geompy.MakeVectorDXDYDZ(1, 1, 0)
    xmy = geompy.MakeVectorDXDYDZ(1, -1, 0)

    grain = geompy.MakeSpherePntR(geompy.MakeVertex(*spos1), radius)
    lattice1 = geompy.MakeMultiTranslation2D(grain, ox, L, xn, oy, L, yn)
    lattice1 = geompy.MakeMultiTranslation1D(lattice1, oz, L, zn)

    #grain = geompy.MakeSpherePntR(geompy.MakeVertex(*spos2), radius)
    #lattice2 = geompy.MakeMultiTranslation2D(grain, xy, length, xn + 1, xmy, length, yn + 1)
    #lattice2 = geompy.MakeMultiTranslation1D(lattice2, oz, L, zn)
    lattice2 = geompy.MakeTranslation(lattice1, 0.5 * L, 0.5 * L, 0.5 * L)
    
    grains = geompy.ExtractShapes(lattice1, geompy.ShapeType["SOLID"], True)
    grains += geompy.ExtractShapes(lattice2, geompy.ShapeType["SOLID"], True)
    grains = geompy.MakeFuseList(grains, False, False)

    grains = geompy.MakeScaleTransform(grains, oo, scale)
    grainsOrigin = None

    if fillet:
        grainsOrigin = grains
        grains = geompy.MakeFilletAll(grains, filletradius * scale)

    ###
    #   Groups
    ##
    shape = geompy.MakeCutList(cubic, [grains])
    shape = geompy.MakeScaleTransform(shape, oo, 1 / scale, theName = "bodyCenteredCubic")
    stripsShape = None

    if fillet:
        shapeOrigin = geompy.MakeCutList(cubic, [grainsOrigin])
        shapeOrigin = geompy.MakeScaleTransform(shapeOrigin, oo, 1 / scale)

        shapeShell = geompy.ExtractShapes(shape, geompy.ShapeType["SHELL"], True)
        shapeOriginShell = geompy.ExtractShapes(shapeOrigin, geompy.ShapeType["SHELL"], True)

        stripsShape = geompy.MakeCutList(shapeShell[0], shapeOriginShell)
        

    sall = geompy.CreateGroup(shape, geompy.ShapeType["FACE"])
    geompy.UnionIDs(sall,
        geompy.SubShapeAllIDs(shape, geompy.ShapeType["FACE"]))

    strips = None
    if fillet:
        strips = geompy.CreateGroup(shape, geompy.ShapeType["FACE"], theName = "strips")
        geompy.UnionList(strips, geompy.SubShapeAll(
            geompy.GetInPlace(shape, stripsShape, True), geompy.ShapeType["FACE"]))

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

    if fillet:
        groups.append(strips)

    wall = geompy.CutListOfGroups([sall], groups, theName = "wall")
    groups.append(wall)

    return shape, groups


def bodyCenteredHexagonalPrism(theta = 0.01, fillet = False, direction = [1, 1, 1]):
    
    ###
    #   Parameters
    ##
    L = 1.0
    r0 = L * sqrt(3) / 4

    radius = r0 / (1 - theta)
    xn, yn, zn = 3, 3, 3 
    
    length = 2 * r0
    width = L / 2
    diag = L * sqrt(2)
    height = diag / 3

    point = []
    xl, yw, zh = -L / 4, -L / 4, -L / 4
    point.append((L / 3 + xl, L / 3 + yw, 4 * L / 3 + zh))
    point.append((L + xl, 0 + yw, L + zh))
    point.append((4 * L / 3 + xl, L / 3 + yw, L / 3 + zh))
    point.append((L + xl, L + yw, 0 + zh))
    point.append((L / 3 + xl, 4 * L / 3 + yw, L / 3 + zh))
    point.append((0 + xl, L + yw, L + zh))
    point.append((L / 3 + xl, L / 3 + yw, 4 * L / 3 + zh))

    C1, C2 = 0.3, 0.2
    theta1, theta2 = 0.01, 0.18
    Cf = C1 + (C2 - C1) / (theta2 - theta1) * (theta - theta1)
    delta = 0.02
    filletradius = delta - Cf * (radius - r0)
    
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
    hexagonPrism = geompy.MakePrismVecH(inletface, vecflow, L * sqrt(3))

    inletface = geompy.MakeScaleTransform(inletface, oo, scale)
    hexagonPrism = geompy.MakeScaleTransform(hexagonPrism, oo, scale)

    faces = geompy.ExtractShapes(hexagonPrism, geompy.ShapeType["FACE"], False)
    symetryface = []

    for face in faces:
        norm = geompy.GetNormal(face)
        angle = round(geompy.GetAngle(norm, vecflow), 0)

        if (angle == 0 or angle == 180) and not face == inletface:
            outletface = face
        
        else:
            symetryface.append(face)
    
    ###
    #   Grains
    ##
    ox = geompy.MakeVectorDXDYDZ(1, 0, 0)
    oy = geompy.MakeVectorDXDYDZ(0, 1, 0)
    oz = geompy.MakeVectorDXDYDZ(0, 0, 1)
    xy = geompy.MakeVectorDXDYDZ(1, 1, 0)
    xmy = geompy.MakeVectorDXDYDZ(1, -1, 0)

    grain = geompy.MakeSpherePntR(geompy.MakeVertex(*spos1), radius)
    lattice1 = geompy.MakeMultiTranslation2D(grain, ox, L, xn, oy, L, yn)
    lattice1 = geompy.MakeMultiTranslation1D(lattice1, oz, L, zn)

    #grain = geompy.MakeSpherePntR(geompy.MakeVertex(*spos2), radius)
    #lattice2 = geompy.MakeMultiTranslation2D(grain, xy, length, xn + 1, xmy, length, yn + 1)
    #lattice2 = geompy.MakeMultiTranslation1D(lattice2, oz, L, zn)
    lattice2 = geompy.MakeTranslation(lattice1, 0.5 * L, 0.5 * L, 0.5 * L)
    
    grains = geompy.ExtractShapes(lattice1, geompy.ShapeType["SOLID"], True)
    grains += geompy.ExtractShapes(lattice2, geompy.ShapeType["SOLID"], True)
    grains = geompy.MakeFuseList(grains, False, False)

    grains = geompy.MakeScaleTransform(grains, oo, scale)
    grainsOrigin = None

    if fillet:
        grainsOrigin = grains
        grains = geompy.MakeFilletAll(grains, filletradius * scale)

    ###
    #   Groups
    ##
    shape = geompy.MakeCutList(hexagonPrism, [grains])
    shape = geompy.MakeScaleTransform(shape, oo, 1 / scale, theName = "bodyCenteredCubic")
    stripsShape = None

    if fillet:
        shapeOrigin = geompy.MakeCutList(hexagonPrism, [grainsOrigin])
        shapeOrigin = geompy.MakeScaleTransform(shapeOrigin, oo, 1 / scale)

        shapeShell = geompy.ExtractShapes(shape, geompy.ShapeType["SHELL"], True)
        shapeOriginShell = geompy.ExtractShapes(shapeOrigin, geompy.ShapeType["SHELL"], True)

        stripsShape = geompy.MakeCutList(shapeShell[0], shapeOriginShell)
        

    sall = geompy.CreateGroup(shape, geompy.ShapeType["FACE"])
    geompy.UnionIDs(sall,
        geompy.SubShapeAllIDs(shape, geompy.ShapeType["FACE"]))

    strips = None
    if fillet:
        strips = geompy.CreateGroup(shape, geompy.ShapeType["FACE"], theName = "strips")
        geompy.UnionList(strips, geompy.SubShapeAll(
            geompy.GetInPlace(shape, stripsShape, True), geompy.ShapeType["FACE"]))


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
    
    if fillet:
        groups.append(strips)


    wall = geompy.CutListOfGroups([sall], groups, theName = "wall")
    groups.append(wall)

    return shape, groups


def bodyCentered(theta, fillet, direction):
    if direction in [[1, 0, 0], [0, 0, 1]]:
        return bodyCenteredCubic(theta, fillet, direction)

    elif direction == [1, 1, 1]:
        return bodyCenteredHexagonalPrism(theta, fillet, direction)

    else:
        raise Exception("This direction is not implemented")

