import SMESH
from salome.smesh import smeshBuilder
smesh = smeshBuilder.New()

from config import logger

def getSmesh():
    return smesh


def meshCreate(shape, groups, fineness, parameters, viscousLayers = None):
    """
    Creates a mesh from a geometry.

    Parameters:
        fineness (int): Fineness of mesh.

            0 - Very coarse,
            1 - Coarse,
            2 - Moderate,
            3 - Fine,
            4 - Very fine.

    Returns:
        Configured instance of class <SMESH.SMESH_Mesh>, containig the parameters and boundary groups.

    """
    ###
    #   Netgen
    ##
    Fineness = {
        0: "Very coarse",
        1: "Coarse",
        2: "Moderate",
        3: "Fine",
        4: "Very fine",
        5: "Custom"
    }[fineness]

    # Mesh
    mesh = smesh.Mesh(shape)
    netgen = mesh.Tetrahedron(algo=smeshBuilder.NETGEN_1D2D3D)

    # Parameters
    param = netgen.Parameters()
    param.SetMinSize(parameters.minSize)
    param.SetMaxSize(parameters.maxSize)
    param.SetFineness(fineness)
    
    if fineness == 5:
        param.SetGrowthRate(parameters.growthRate)
        param.SetNbSegPerEdge(parameters.nbSegPerEdge)
        param.SetNbSegPerRadius(parameters.nbSegPerRadius)
    
    
    param.SetChordalErrorEnabled(parameters.chordalErrorEnabled)
    param.SetChordalError(parameters.chordalError)

    param.SetSecondOrder(parameters.secondOrder)
    param.SetOptimize(parameters.optimize)
    param.SetQuadAllowed(parameters.quadAllowed)
    
    param.SetUseSurfaceCurvature(parameters.useSurfaceCurvature)
    param.SetFuseEdges(parameters.fuseEdges)
    param.SetCheckChartBoundary(parameters.checkChartBoundary)
    
        
    logger.info("""meshCreate:
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

    
    ###
    #   Groups
    ##
    for group in groups:
        mesh.GroupOnGeom(group, "{}_".format(group.GetName()), SMESH.FACE)

    ###
    #   Viscous layers
    ##
    if not viscousLayers is None:
        vlayer = netgen.ViscousLayers(
            viscousLayers.thickness,
            viscousLayers.numberOfLayers,
            viscousLayers.stretchFactor,
            viscousLayers.facesToIgnore,
            viscousLayers.isFacesToIgnore, 
            viscousLayers.extrusionMethod
        )

        logger.info("""meshCreate:
    viscous layers: 
        thickness:\t{}
        number:\t{}
        stretch factor:\t{}""".format(
            viscousLayers.thickness, 
            viscousLayers.numberOfLayers, 
            viscousLayers.stretchFactor))

        

    else:
        logger.info("""meshCreate: 
    viscous layers: disabled""")


    return mesh


def meshCompute(mobj):
    """Compute the mesh."""
    status = mobj.Compute()
    #msg = ""

    #if status:
    #    msg = "Computed"

    #else:
    #    msg = "Not computed"

    #logger.info("""meshCompute:
    #status:\t{}""".format(msg))

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

        logger.info("""meshCompute:
    Elements:\t{}
        Edges:\t{}
        Faces:\t{}
            Triangles:\t{}
        Volumes:\t{}
            Tetrahedrons:\t{}
            Prisms:\t{}
            Pyramid:\t{}""".format(
            elements, edges, faces, triangles, volumes, tetra, prism, pyramid))

    else:
        logger.warning("meshCompute: not computed")


def meshExport(mobj, path):
    """
    Export the mesh in a file in UNV format.

    Parameters:
        path (string): full path to the expected directory.
    """

    try:
        mobj.ExportUNV(path)

        logger.info("""meshExport:
    format:\t{}""".format("unv"))

    except:
        logger.error("""meshExport: Cannot export.""")


