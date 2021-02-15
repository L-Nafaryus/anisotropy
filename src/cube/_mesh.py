import SMESH, SALOMEDS
from salome.smesh import smeshBuilder
smesh = smeshBuilder.New()


def create(geomObj):
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
    param.SetMaxSize( 0.05 )
    param.SetFineness( 3 )
    param.SetGrowthRate( 0.1 )
    param.SetNbSegPerEdge( 5 )
    param.SetNbSegPerRadius( 10 )
    param.SetQuadAllowed( 0 )

    vlayer = netgen.ViscousLayers(0.01, 3, 1.5, [], 
        1, smeshBuilder.SURF_OFFSET_SMOOTH)
    
    return mesh

