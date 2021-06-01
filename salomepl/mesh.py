import SMESH
from salome.smesh import smeshBuilder
smesh = smeshBuilder.New()

import logging
logger = logging.getLogger("anisotropy")

def getSmesh():
    return smesh


def meshCreate(shape, groups, parameters): #fineness, parameters, viscousLayers = None):
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
    }[parameters.fineness]

    # Mesh
    mesh = smesh.Mesh(shape)
    netgen = mesh.Tetrahedron(algo=smeshBuilder.NETGEN_1D2D3D)

    # Parameters
    param = netgen.Parameters()
    param.SetMinSize(parameters.minSize)
    param.SetMaxSize(parameters.maxSize)
    param.SetFineness(parameters.fineness)
    
    if parameters.fineness == 5:
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
    #if not viscousLayers is None:
    vlayer = netgen.ViscousLayers(
        parameters.thickness,
        parameters.numberOfLayers,
        parameters.stretchFactor,
        parameters.facesToIgnore,
        parameters.isFacesToIgnore, 
        parameters.extrusionMethod
    )

    logger.info("""meshCreate:
viscous layers: 
    thickness:\t{}
    number:\t{}
    stretch factor:\t{}""".format(
        parameters.thickness, 
        parameters.numberOfLayers, 
        parameters.stretchFactor))

        

    #else:
    #    logger.info("""meshCreate: 
    #viscous layers: disabled""")


    return mesh


def meshCompute(mobj):
    """Compute the mesh."""
    status = mobj.Compute()
    
    if status:
        logger.info("meshCompute: computed")
        
        ###
        #   Post computing
        ##
        if mobj.NbPyramids() > 0:
            logger.info(f"meshCompute: detected {mobj.NbPyramids()} pyramids: splitting volumes into tetrahedrons")
            
            pyramidCriterion = smesh.GetCriterion(
                SMESH.VOLUME,
                SMESH.FT_ElemGeomType,
                SMESH.FT_Undefined,
                SMESH.Geom_PYRAMID
            )
            pyramidGroup = mobj.MakeGroupByCriterion("pyramids", pyramidCriterion)
            pyramidVolumes = mobj.GetIDSource(pyramidGroup.GetIDs(), SMESH.VOLUME)

            mobj.SplitVolumesIntoTetra(pyramidVolumes, smesh.Hex_5Tet)
            
            mobj.RemoveGroup(pyramidGroup)
            mobj.RenumberElements()
        
    else:
        logger.warning("meshCompute: not computed")


def meshStats(mobj):
    """
    Print mesh information.
    """
    stats = {
        "Elements": mobj.NbElements(),
        "Edges": mobj.NbEdges(),
        "Faces": mobj.NbFaces(),
        "Volumes": mobj.NbVolumes(),
        "Tetrahedrons": mobj.NbTetras(),
        "Prisms": mobj.NbPrisms(),
        "Pyramids": mobj.NbPyramids()
    }
    info = "meshStats:\n"

    for key in stats:
        info += f"\t{key}:\t{stats[key]}\n"

    logger.info(info)


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

