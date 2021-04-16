## Usefull utils
- createPatch
- polyDualMesh
- fvSolution: cellLimited
- collapseDict: collapseEdges
- renumberMesh
- processorField

## Errors
- salome:

th. 139990926538304 - 
Trace /volatile/salome/jenkins/workspace/Salome_master_CO7/SALOME-9.6.0-CO7/SOURCES/SMESH/src/SMESH/SMESH_subMesh.cxx [2005] : 
NETGEN_2D3D failed on sub-shape #1 with error COMPERR_BAD_INPUT_MESH 
"NgException at Volume meshing: Stop meshing since surface mesh not consistent Some edges multiple times in surface mesh"

th. 140588498282048 - 
Trace /volatile/salome/jenkins/workspace/Salome_master_CO7/SALOME-9.6.0-CO7/SOURCES/SMESH/src/SMESH/SMESH_subMesh.cxx [2005] : 
NETGEN_2D3D failed on sub-shape #47 with error COMPERR_WARNING 
"Thickness 0.001 of viscous layers not reached, average reached thickness is 0.000928207"

th. 139986338838080 - 
Trace /volatile/salome/jenkins/workspace/Salome_master_CO7/SALOME-9.6.0-CO7/SOURCES/SMESH/src/SMESH/SMESH_subMesh.cxx [2005] : 
NETGEN_2D3D failed on sub-shape #1 with error COMPERR_BAD_INPUT_MESH 
"NgException at Volume meshing: Stop meshing since boundary mesh is overlapping Intersecting triangles"


## 1.03.21
- [x] boundary type (wall or symetryPlane)
- [x] restruct for ways
- [x] build alpha = 0.01 .. 0.13
- [x] ! symetryPlane -> cyclicAMI

## 3.03.21
- [x] configure salome server, ports, etc.
- [ ] less processes for salome, optimization.

## 4.03.21
- [x] 3rd direction
- [x] createPatch(Dict)
- [ ] views (mesh, ..)
- [x] alpha for simpleCubic [0.01 .. 0.28]
- [x] translation vector (cyclicAMI)
- [ ] BUG: angle between the direction vector and the normal to inlet is ~1.4e-14 
    - [x] Another solution
- [ ] BUG: ideasUnvToFoam not working with param '-case PATH'
    - [x] Temporary sulution via os.chdir(PATH)

## 6.03.21
- [ ] ERROR: MakeFuseList with alpha > 0.2

## 7.03.21
- [x] Split the symetryPlane to 4 faces

## 11.03.21
- [x] Dual test for cyclicAMI
