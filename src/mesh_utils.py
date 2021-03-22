#!/usr/bin/env python
# -*- coding: utf-8 -*-

import SMESH
from salome.smesh import smeshBuilder
smesh = smeshBuilder.New()

import logging

def getSmesh():
    return smesh

def meshCreate(gobj, boundary, fineness, viscousLayers=None):
    """
    Creates a mesh from a geometry.

    Parameters:
        fineness (int): Fineness of mesh.

            0 - Very coarse,
            1 - Coarse,
            2 - Moderate,
            3 - Fine,
            4 - Very fine.

        viscousLayers (dict or None): Defines viscous layers for mesh.
            By default, inlets and outlets specified without layers.

            {
                "thickness": float,
                "number": int,
                "stretch": float
            }

    Returns:
        Configured instance of class <SMESH.SMESH_Mesh>, containig the parameters and boundary groups.

    """
    Fineness = {
        0: "Very coarse",
        1: "Coarse",
        2: "Moderate",
        3: "Fine",
        4: "Very fine"
    }[fineness]

    logging.info("meshCreate: mesh fineness - {}".format(Fineness))

    mesh = smesh.Mesh(gobj)
    netgen = mesh.Tetrahedron(algo=smeshBuilder.NETGEN_1D2D3D)

    param = netgen.Parameters()
    param.SetSecondOrder( 0 )
    param.SetOptimize( 1 )
    param.SetChordalError( -1 )
    param.SetChordalErrorEnabled( 0 )
    param.SetUseSurfaceCurvature( 1 )
    param.SetFuseEdges( 1 )
    param.SetCheckChartBoundary( 0 )
    param.SetMinSize( 0.01 )
    param.SetMaxSize( 0.1 )
    param.SetFineness(fineness)
    #param.SetGrowthRate( 0.1 )
    #param.SetNbSegPerEdge( 5 )
    #param.SetNbSegPerRadius( 10 )
    param.SetQuadAllowed( 0 )

    if not viscousLayers is None:
        logging.info("meshCreate: viscous layers params - thickness = {}, number = {}, stretch factor = {}".format(
            viscousLayers["thickness"], viscousLayers["number"], viscousLayers["stretch"]))

        vlayer = netgen.ViscousLayers(
            viscousLayers["thickness"],
            viscousLayers["number"],
            viscousLayers["stretch"],
            [boundary["inlet"], boundary["outlet"]],
            1, smeshBuilder.NODE_OFFSET)

    else:
        logging.info("meshCreate: viscous layers are disabled")

    for name, b in boundary.items():
        mesh.GroupOnGeom(b, "{}_".format(name), SMESH.FACE)

    return mesh

def meshCompute(mobj):
    """Compute the mesh."""
    status = mobj.Compute()

    if status:
        logging.info("Mesh succesfully computed.")

    else:
        logging.warning("Mesh is not computed.")

def meshExport(mobj, path):
    """
    Export the mesh in a file in UNV format.

    Parameters:
        path (string): full path to the expected directory.
    """
    exportpath = os.path.join(path, "{}.unv".format(mobj.name))

    try:
        mobj.ExportUNV(exportpath)

    except:
        logging.error("Cannot export mesh to '{}'".format(exportpath))

