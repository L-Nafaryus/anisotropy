from netgen.meshing import Mesh as netgenMesh
from meshio import Mesh as meshioMesh

meshfile = "mesh.mesh"

mesh = netgenMesh()
mesh.Load(meshfile)

topology3d = {
    4: "tetra"
}

pointsNew = []
cellsNew = {}

for point in mesh.Points():
    pointsNew.append(list(point.p))

for cell in mesh.Elements3D():
    cellTopo = topology3d[len(cell.points)]
    cellNew = []

    for pointId in cell.points:
        cellNew.append(pointId.nr)

    if cellsNew.get(cellTopo):
        cellsNew[cellTopo].append(cellNew)

    else:
        cellsNew[cellTopo] = [ cellNew ]    

cellsMeshio = [ cell for cell in cellsNew.items() ]
meshNew = meshioMesh(pointsNew, cellsMeshio)