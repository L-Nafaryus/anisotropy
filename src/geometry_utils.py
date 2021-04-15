import GEOM
from salome.geom import geomBuilder
geompy = geomBuilder.New()

import math
import logging
from pyquaternion import Quaternion
import numpy as np


def getGeom():
    return geompy


def createGroup(gobj, planelist, grains, name):
    gr = geompy.CreateGroup(gobj, geompy.ShapeType["FACE"], name)

    grcomp = geompy.MakeCompound(planelist)
    #grcut = geompy.MakeCutList(grcomp, [grains], False)

    gip = geompy.GetInPlace(gobj, grcomp, True)
    faces = geompy.SubShapeAll(gip, geompy.ShapeType["FACE"])
    geompy.UnionList(gr, faces)

    return gr


def createBoundary(gobj, bcount, dvec, norm, grains):
    ang = lambda n, count: 2 * np.pi * n / count
    limit = bcount if np.mod(bcount, 2) else int(bcount / 2)

    vecs = [ Quaternion(axis = dvec, angle = ang(n, bcount)).rotate(norm) for n in range(limit) ]
    
    logging.info("""createBoundary: 
    flow direction:\t{}
    side boundaries:\t{}
    normal direction:\t{}
    angles:\t{}
    side directions:\t{}""".format(dvec, bcount, norm, 
        [ ang(n, bcount) / (2 * np.pi) * 360 for n in range(limit) ], 
        len(vecs))) #[ v for v in vecs ]))

    #
    flowvec = geompy.MakeVector(
        geompy.MakeVertex(0, 0, 0),
        geompy.MakeVertex(dvec[0], dvec[1], dvec[2]))
    symvec = []

    for vec in vecs:
        #vec = qvec.vector
        symvec.append(geompy.MakeVector(
            geompy.MakeVertex(0, 0, 0),
            geompy.MakeVertex(vec[0], vec[1], vec[2])))


    #
    planes = geompy.ExtractShapes(gobj, geompy.ShapeType["FACE"], False)
    #planes = geompy.MakeCompound(planes)
    planes = geompy.MakeShell(planes)
    #planes = geompy.ProcessShape(planes, 
    #    [ "FixShape", "FixFaceSize", "DropSmallEdges", "SameParameter" ], 
    #    [ "FixShape.Tolerance3d", "FixShape.MaxTolerance3d", "FixFaceSize.Tolerance", "DropSmallEdges.Tolerance3d", "SameParameter.Tolerance3d" ], 
    #    [ "1e-7", "1", "0.05", "0.05", "1e-7" ])
    planes = geompy.MakeCutList(planes, [grains], False)
    planes = geompy.ExtractShapes(planes, geompy.ShapeType["FACE"], False)
    #print("planes: ", len(planes))

    inletplanes = []
    outletplanes = []
    symetryplanes = [[None, None] for n in range(limit)]

    for plane in planes:
        nvec = geompy.GetNormal(plane)
        
        fwang = round(geompy.GetAngle(nvec, flowvec), 0)
        #print("fwang = ", fwang)

        if fwang == 0:
            inletplanes.append(plane)

        elif fwang == 180:
            outletplanes.append(plane)

        for n in range(len(symvec)):
            sang = round(geompy.GetAngle(nvec, symvec[n]), 0)
            #print("sang = ", sang)

            if sang == 0:
                if symetryplanes[n][0] == None:
                    symetryplanes[n][0] = []

                symetryplanes[n][0].append(plane)

            elif sang == 180:
                if symetryplanes[n][1] == None:
                    symetryplanes[n][1] = []

                symetryplanes[n][1].append(plane)
        #print("\n")

    symetryplanesinfo = []
    for n in range(len(symetryplanes)):
        symetryplanesinfo.append([])
        for pair in range(len(symetryplanes[n])):
            symetryplanesinfo[n].append(len(symetryplanes[n][pair]))

    logging.info("""createBoundary: 
    planes:\t{}
    inlet planes:\t{}
    outlet planes:\t{}
    side planes:\t{}""".format(len(planes), len(inletplanes), len(outletplanes), symetryplanesinfo))

    #
    boundary = {}

    boundary["inlet"] = createGroup(gobj, inletplanes, grains, "inlet")
    boundary["outlet"] = createGroup(gobj, outletplanes, grains, "outlet")
    
    for n in range(len(symetryplanes)):
        name = "symetryPlane{}".format(n + 1)
        
        boundary[name + "_1"] = createGroup(gobj, symetryplanes[n][0], grains, name + "_1")

        if not symetryplanes[n][1] == None:
            boundary[name + "_2"] = createGroup(gobj, symetryplanes[n][1], grains, name + "_2")

    # wall
    allgroup = geompy.CreateGroup(gobj, geompy.ShapeType["FACE"])
    faces = geompy.SubShapeAllIDs(gobj, geompy.ShapeType["FACE"])
    geompy.UnionIDs(allgroup, faces)
    boundary["wall"] = geompy.CutListOfGroups([allgroup], list(boundary.values()), "wall")
    
    return boundary


def boundaryCreate(gobj, dvec, grains):

    xvec = geompy.MakeVector(
        geompy.MakeVertex(0, 0, 0),
        geompy.MakeVertex(dvec.x[0], dvec.x[1], dvec.x[2]))
    #xvec = rotate(xvec, [0, 0, 0.25 * math.pi])

    #yvec = rotate(xvec, [0.5 * math.pi, 0, 0])
    #zvec = rotate(xvec, [0, 0.5 * math.pi, 0])
    
    yvec = geompy.MakeVector(
        geompy.MakeVertex(0, 0, 0),
        geompy.MakeVertex(dvec.y[0], dvec.y[1], dvec.y[2]))
    zvec = geompy.MakeVector(
        geompy.MakeVertex(0, 0, 0),
        geompy.MakeVertex(dvec.z[0], dvec.z[1], dvec.z[2]))

    geompy.addToStudy(xvec, "xvec")
    geompy.addToStudy(yvec, "yvec")
    geompy.addToStudy(zvec, "zvec")

    logging.info("""boundaryCreate: 
    direction vectors:  x = {}
                        y = {}
                        z = {}""".format(dvec.x, dvec.y, dvec.z))

    planes = geompy.ExtractShapes(gobj, geompy.ShapeType["FACE"], False)
    planes = geompy.MakeCompound(planes)
    planes = geompy.MakeCutList(planes, [grains], False)
    planes = geompy.ExtractShapes(planes, geompy.ShapeType["FACE"], False)

    inletplanes = []
    outletplanes = []
    #uplanes = []

    fwplanes = []
    bwplanes = []
    lplanes = []
    rplanes = []

    for plane in planes:
        nvec = geompy.GetNormal(plane)
        xang = round(geompy.GetAngle(nvec, xvec), 0)
        yang = round(geompy.GetAngle(nvec, yvec), 0)
        zang = round(geompy.GetAngle(nvec, zvec), 0)
        #print(xang, yang, zang, sep="\t")

        if xang == 0:
            inletplanes.append(plane)

        elif xang == 180:
            outletplanes.append(plane)

        elif yang == 0:
            fwplanes.append(plane)

        elif yang == 180:
            bwplanes.append(plane)

        elif zang == 0:
            lplanes.append(plane)

        elif zang == 180:
            rplanes.append(plane)
    
    logging.info("""boundaryCreate:
    planes count:\t{}
    inlet planes:\t{}
    outlet planes:\t{}
    forward planes:\t{}
    backward planes:\t{}
    left planes:\t{}
    right planes:\t{}""".format(len(planes), len(inletplanes), len(outletplanes), 
        len(fwplanes), len(bwplanes), len(lplanes), len(rplanes)))

    # Main groups
    inlet = createGroup(gobj, inletplanes, grains, "inlet")
    outlet = createGroup(gobj, outletplanes, grains, "outlet")

    symetryPlaneFW = createGroup(gobj, fwplanes, grains, "symetryPlaneFW")
    symetryPlaneBW = createGroup(gobj, bwplanes, grains, "symetryPlaneBW")
    symetryPlaneL = createGroup(gobj, lplanes, grains, "symetryPlaneL")
    symetryPlaneR = createGroup(gobj, rplanes, grains, "symetryPlaneR")

    # wall
    allgroup = geompy.CreateGroup(gobj, geompy.ShapeType["FACE"])
    faces = geompy.SubShapeAllIDs(gobj, geompy.ShapeType["FACE"])
    geompy.UnionIDs(allgroup, faces)
    wall = geompy.CutListOfGroups([allgroup],
        [inlet, outlet, symetryPlaneFW, symetryPlaneBW, symetryPlaneL, symetryPlaneR], "wall")

    boundary = {
        "inlet": inlet,
        "outlet": outlet,
        "symetryPlaneFW": symetryPlaneFW,
        "symetryPlaneBW": symetryPlaneBW,
        "symetryPlaneL": symetryPlaneL,
        "symetryPlaneR": symetryPlaneR,
        "wall": wall
    }

    return boundary


