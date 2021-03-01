#!/usr/bin/env bash

path=.
#build/simple-cubic/0.1

# python src/genmesh.py
# python src/prefoam.py

# Clean case directory
rm -rf postProcessing processor* *.log logs *.obj constant/polyMesh

# Export and transform mesh
ideasUnvToFoam -case $path mesh.unv
transformPoints -scale '(1e-5 1e-5 1e-5)'
#polyDualMesh 70 -overwrite
checkMesh -case $path -allGeometry -allTopology > checkMesh.log

# Change boundary type for mesh
foamDictionary -case $path constant/polyMesh/boundary -entry entry0.wall.type -set wall

# Case decomposition
decomposePar -case $path

# Initial approximation
mpirun -np 4 --oversubscribe potentialFoam -case $path -parallel

# Change boundary type for simpleFoam
for n in {0..3}; do

    foamDictionary "processor${n}/0/U" -entry boundaryField.inlet.type -set pressureInletVelocity
    foamDictionary "processor${n}/0/U" -entry boundaryField.inlet.value -set 'uniform (0 0 0)'
done

sleep 2
# Main calculation
mpirun -np 4 --oversubscribe simpleFoam -parallel -case $path | tee -a $path/simpleFoam.log

