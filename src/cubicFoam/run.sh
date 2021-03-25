#!/usr/bin/env bash

ideasUnvToFoam mesh.unv
createPatch -overwrite
#patchSummary
transformPoints -scale '1e-5'

foamDictionary constant/polyMesh/boundary -entry entry0.cyclicPlaneL.separationVector -set '(0 1e-5 0)'
foamDictionary constant/polyMesh/boundary -entry entry0.cyclicPlaneR.separationVector -set '(0 -1e-5 0)'

checkMesh -allGeometry -allTopology | tee -a checkMesh.log

#
decomposePar

mpirun -np 4 --oversubscribe potentialFoam -parallel | tee -a potentialFoam.log

foamDictionary processor0/0/U -entry boundaryField.inlet.type -set pressureInletVelocity
foamDictionary processor1/0/U -entry boundaryField.inlet.type -set pressureInletVelocity
foamDictionary processor2/0/U -entry boundaryField.inlet.type -set pressureInletVelocity
foamDictionary processor3/0/U -entry boundaryField.inlet.type -set pressureInletVelocity
foamDictionary processor0/0/U -entry boundaryField.inlet.value -set 'uniform (0 0 0)'
foamDictionary processor1/0/U -entry boundaryField.inlet.value -set 'uniform (0 0 0)'
foamDictionary processor2/0/U -entry boundaryField.inlet.value -set 'uniform (0 0 0)'
foamDictionary processor3/0/U -entry boundaryField.inlet.value -set 'uniform (0 0 0)'

mpirun -np 4 --oversubscribe simpleFoam -parallel | tee -a simpleFoam.log
