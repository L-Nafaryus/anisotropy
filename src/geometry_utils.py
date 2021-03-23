#!/usr/bin/env python
# -*- coding: utf-8 -*-

import GEOM
from salome.geom import geomBuilder
geompy = geomBuilder.New()

import math
import logging

def getGeom():
    return geompy

def rotate(gobj, ang):
    x = geompy.MakeVectorDXDYDZ(1, 0, 0),
    y = geompy.MakeVectorDXDYDZ(0, 1, 0),
    z = geompy.MakeVectorDXDYDZ(0, 0, 1)

    # yaw
    rotated = geompy.MakeRotation(gobj, z, ang[2])
    print(rotated)
    # pitch
    rotated = geompy.MakeRotation(rotated, y, ang[1])
    # roll
    rotated = geompy.MakeRotation(rotated, x, ang[0])

    return rotated

def createGroup(gobj, planelist, grains, name):
    gr = geompy.CreateGroup(gobj, geompy.ShapeType["FACE"], name)

    grcomp = geompy.MakeCompound(planelist)
    grcut = geompy.MakeCutList(grcomp, [grains], True)

    gip = geompy.GetInPlace(gobj, grcut, True)
    faces = geompy.SubShapeAll(gip, geompy.ShapeType["FACE"])
    geompy.UnionList(gr, faces)

    return gr

def boundaryCreate(gobj, dvec, grains):

    xvec = geompy.MakeVector(
        geompy.MakeVertex(0, 0, 0),
        geompy.MakeVertex(dvec[0], dvec[1], dvec[2]))
    #xvec = rotate(dvec, self.angle)

    yvec = rotate(xvec, [0.5 * math.pi, 0, 0])
    zvec = rotate(xvec, [0, 0.5 * math.pi, 0])

    logging.info("boundaryCreate: dvec = {}".format(dvec))

    planes = geompy.ExtractShapes(gobj, geompy.ShapeType["FACE"], True)
    inletplanes = []
    outletplanes = []
    uplanes = []

    fwplanes = []
    bwplanes = []
    lplanes = []
    rplanes = []

    for plane in planes:
        nvec = geompy.GetNormal(plane)
        xang = geompy.GetAngle(nvec, xvec)
        yang = geompy.GetAngle(nvec, yvec)
        zang = geompy.GetAngle(nvec, zvec)

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

    logging.info(
        "boundaryCreate: inletplanes = {}, outletplanes = {}, hplanes = {}".format(
            len(inletplane), len(outletplane), len(hplanes)))

    logging.info(
        "boundaryCreate: fwplanes = {}, bwplanes = {}, lplanes = {}, rplanes = {}".format(
            len(fwplanes), len(bwplanes), len(lplanes), len(rplanes)))

    # Main groups
    inlet = createGroup(gobj, inletplane, grains, "inlet")
    outlet = createGroup(gobj, grains, outletplane, "outlet")

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


