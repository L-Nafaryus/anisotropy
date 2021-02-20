import SMESH, SALOMEDS
from salome.smesh import smeshBuilder
smesh = smeshBuilder.New()


def create(geomObj, bc):
    mesh = smesh.Mesh(geomObj)
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
    param.SetFineness( 4 )
    #param.SetGrowthRate( 0.1 )
    #param.SetNbSegPerEdge( 5 )
    #param.SetNbSegPerRadius( 10 )
    param.SetQuadAllowed( 0 )

    vlayer = netgen.ViscousLayers(0.025, 5, 1.1, [],
        1, smeshBuilder.NODE_OFFSET)
    
    mesh.GroupOnGeom(bc[0], 'inlet', SMESH.FACE)
    mesh.GroupOnGeom(bc[1], 'outlet', SMESH.FACE)
    mesh.GroupOnGeom(bc[2], 'wall', SMESH.FACE)

    return mesh

