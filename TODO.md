- fvSolution: cellLimited
- collapseDict: collapseEdges

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
