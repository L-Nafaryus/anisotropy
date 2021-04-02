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
        4: "Very fine",
        5: "Custom"
    }[fineness]

    mesh = smesh.Mesh(gobj)
    netgen = mesh.Tetrahedron(algo=smeshBuilder.NETGEN_1D2D3D)

    param = netgen.Parameters()
    param.SetMinSize( 0.001 )
    param.SetMaxSize( 0.1 )
    
    param.SetSecondOrder( 0 )
    param.SetOptimize( 1 )
    param.SetQuadAllowed( 0 )
    param.SetChordalError( -1 )
    param.SetChordalErrorEnabled( 0 )
    param.SetUseSurfaceCurvature( 1 )
    param.SetFuseEdges( 1 )
    param.SetCheckChartBoundary( 0 )
    
    param.SetFineness(fineness)
    
    # TODO: add customization
    if fineness == 5:
        param.SetGrowthRate( 0.1 )
        param.SetNbSegPerEdge( 5 )
        param.SetNbSegPerRadius( 10 )
    
    
    logging.info("""meshCreate:
    fineness:\t{}
    min size:\t{}
    max size:\t{}
    growth rate:\t{}
    nb segs per edge:\t{}
    nb segs per radius:\t{}
    limit size by surface curvature:\t{}
    quad-dominated:\t{}
    second order:\t{}
    optimize:\t{}""".format(
        Fineness, param.GetMinSize(), param.GetMaxSize(), 
        param.GetGrowthRate(), param.GetNbSegPerEdge(), param.GetNbSegPerRadius(), 
        True if param.GetUseSurfaceCurvature() else False, 
        True if param.GetQuadAllowed() else False, 
        True if param.GetSecondOrder() else False, 
        True if param.GetOptimize() else False))



    if not viscousLayers is None:
        logging.info("""meshCreate:
    viscous layers: 
        thickness:\t{}
        number:\t{}
        stretch factor:\t{}""".format(
            viscousLayers["thickness"], viscousLayers["number"], viscousLayers["stretch"]))

        vlayer = netgen.ViscousLayers(
            viscousLayers["thickness"],
            viscousLayers["number"],
            viscousLayers["stretch"],
            [boundary["inlet"], boundary["outlet"]],
            1, smeshBuilder.NODE_OFFSET)

    else:
        logging.info("""meshCreate: 
    viscous layers: disabled""")

    for name, b in boundary.items():
        mesh.GroupOnGeom(b, "{}_".format(name), SMESH.FACE)

    return mesh


def meshCompute(mobj):
    """Compute the mesh."""
    status = mobj.Compute()
    msg = ""

    if status:
        msg = "Computed"

    else:
        msg = "Not computed"

    logging.info("""meshCompute:
    status:\t{}""".format(msg))

    if status:
        omniinfo = mobj.GetMeshInfo()
        keys = [ str(k) for k in omniinfo.keys() ]
        vals = [ v for v in omniinfo.values() ]
        info = {}

        for n in range(len(keys)):
            info[keys[n]] = vals[n]

        edges = info["Entity_Edge"]
        
        triangles = info["Entity_Triangle"]
        faces = triangles

        tetra = info["Entity_Tetra"]
        prism = info["Entity_Penta"]
        pyramid = info["Entity_Pyramid"]
        volumes = tetra + prism + pyramid

        elements = edges + faces + volumes

        logging.info("""meshCompute:
    Elements:\t{}
        Edges:\t{}
        Faces:\t{}
            Triangles:\t{}
        Volumes:\t{}
            Tetrahedrons:\t{}
            Prisms:\t{}
            Pyramid:\t{}""".format(
            elements, edges, faces, triangles, volumes, tetra, prism, pyramid))


def meshExport(mobj, path):
    """
    Export the mesh in a file in UNV format.

    Parameters:
        path (string): full path to the expected directory.
    """

    try:
        mobj.ExportUNV(path)

        logging.info("""meshExport:
        format:\t{}""".format("unv"))

    except:
        logging.error("""meshExport: Cannot export.""")


