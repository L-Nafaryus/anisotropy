import salome
salome.salome_init()

import GEOM
from salome.geom import geomBuilder
geompy = geomBuilder.New()

from math import pi, sqrt

def faceCenteredCubic(theta = 0.01, fillet = False, direction = [1, 0, 0]):
    
    ###
    #   Parameters
    ##
    L = 1.0
    r0 = L * sqrt(2) / 4

    radius = r0 / (1 - theta)
    xn, yn, zn = 3, 3, 3 
    
    length = 2 * r0
    width = L / 2
    diag = L * sqrt(3)
    height = diag / 3

    point = []
    xl = sqrt(length ** 2 + length ** 2) * 0.5
    yw = xl
    zh = width

    C1, C2 = 0.3, 0.2
    theta1, theta2 = 0.01, 0.13
    Cf = C1 + (C2 - C1) / (theta2 - theta1) * (theta - theta1)
    delta = 0.012
    filletradius = delta - Cf * (radius - r0)
    
    scale = 100
    oo = geompy.MakeVertex(0, 0, 0)
    spos1 = (-width * (xn - 1), 0, -width * (zn - 2))
    spos2 = (-width * xn, 0, -width * (zn - 1))

    ###
    #   Bounding box
    ##
    if direction == [1, 0, 0]:
        sk = geompy.Sketcher3D()
        sk.addPointsAbsolute(0, 0, -zh)
        sk.addPointsAbsolute(-xl, yw, -zh)
        sk.addPointsAbsolute(-xl, yw, zh)
        sk.addPointsAbsolute(0, 0, zh)
        sk.addPointsAbsolute(0, 0, -zh)

        inletface = geompy.MakeFaceWires([sk.wire()], True)
        vecflow = geompy.GetNormal(inletface)
        cubic = geompy.MakePrismVecH(inletface, vecflow, length)

    elif direction == [0, 0, 1]:
        sk = geompy.Sketcher3D()
        sk.addPointsAbsolute(0, 0, -zh)
        sk.addPointsAbsolute(xl, yw, -zh)
        sk.addPointsAbsolute(0, 2 * yw, -zh)
        sk.addPointsAbsolute(-xl, yw, -zh)
        sk.addPointsAbsolute(0, 0, -zh)

        inletface = geompy.MakeFaceWires([sk.wire()], True)
        vecflow = geompy.GetNormal(inletface)
        cubic = geompy.MakePrismVecH(inletface, vecflow, 2 * zh)

    else:
        raise Exception("The direction is not implemented")
    
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
    lattice1 = geompy.MakeMultiTranslation2D(grain, xy, length, xn, xmy, length, yn)
    lattice1 = geompy.MakeMultiTranslation1D(lattice1, oz, L, zn - 1)

    grain = geompy.MakeSpherePntR(geompy.MakeVertex(*spos2), radius)
    lattice2 = geompy.MakeMultiTranslation2D(grain, xy, length, xn + 1, xmy, length, yn + 1)
    lattice2 = geompy.MakeMultiTranslation1D(lattice2, oz, L, zn)
    
    grains = geompy.ExtractShapes(lattice1, geompy.ShapeType["SOLID"], True)
    grains += geompy.ExtractShapes(lattice2, geompy.ShapeType["SOLID"], True)
    grains = geompy.MakeFuseList(grains, False, False)

    grains = geompy.MakeScaleTransform(grains, oo, scale)

    if fillet:
        grains = geompy.MakeFilletAll(grains, filletradius * scale)

    ###
    #   Groups
    ##
    shape = geompy.MakeCutList(cubic, [grains])
    shape = geompy.MakeScaleTransform(shape, oo, 1 / scale, theName = "faceCenteredCubic")

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
    wall = geompy.CutListOfGroups([sall], groups, theName = "wall")
    groups.append(wall)

    return shape, groups

def faceCenteredHexagonalPrism(theta = 0.01, fillet = False, direction = [1, 1, 1]):
    
    ###
    #   Parameters
    ##
    L = 1.0
    r0 = L * sqrt(2) / 4

    radius = r0 / (1 - theta)
    xn, yn, zn = 3, 3, 3 
    
    length = 2 * r0
    width = L / 2
    diag = L * sqrt(3)
    height = diag / 3

    point = []
    xl, yw, zh = -(xn - 2) * L / 3, -(yn - 2) * L / 3, -(zn - 2) * L / 3
    point.append((-2 * width / 3 + xl, -2 * width / 3 + yw, width / 3 + zh))
    point.append((0 + xl, -width + yw, 0 + zh))
    point.append((width / 3 + xl, -2 * width / 3 + yw, -2 * width / 3 + zh))
    point.append((0 + xl, 0 + yw, -width + zh))
    point.append((-2 * width / 3 + xl, width / 3 + yw, -2 * width / 3 + zh))
    point.append((-width + xl, 0 + yw, 0 + zh))
    point.append((-2 * width / 3 + xl, -2 * width / 3 + yw, width / 3 + zh))

    C1, C2 = 0.3, 0.2
    theta1, theta2 = 0.01, 0.13
    Cf = C1 + (C2 - C1) / (theta2 - theta1) * (theta - theta1)
    delta = 0.012
    filletradius = delta - Cf * (radius - r0)
    
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
    lattice1 = geompy.MakeMultiTranslation2D(grain, xy, length, xn, xmy, length, yn)
    lattice1 = geompy.MakeMultiTranslation1D(lattice1, oz, L, zn - 1)

    grain = geompy.MakeSpherePntR(geompy.MakeVertex(*spos2), radius)
    lattice2 = geompy.MakeMultiTranslation2D(grain, xy, length, xn + 1, xmy, length, yn + 1)
    lattice2 = geompy.MakeMultiTranslation1D(lattice2, oz, L, zn)
    
    grains = geompy.ExtractShapes(lattice1, geompy.ShapeType["SOLID"], True)
    grains += geompy.ExtractShapes(lattice2, geompy.ShapeType["SOLID"], True)
    grains = geompy.MakeFuseList(grains, False, False)

    grains = geompy.MakeScaleTransform(grains, oo, scale)

    if fillet:
        grains = geompy.MakeFilletAll(grains, filletradius * scale)

    ###
    #   Groups
    ##
    shape = geompy.MakeCutList(hexagonPrism, [grains])
    shape = geompy.MakeScaleTransform(shape, oo, 1 / scale, theName = "faceCenteredCubic")

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
    wall = geompy.CutListOfGroups([sall], groups, theName = "wall")
    groups.append(wall)

    return shape, groups

