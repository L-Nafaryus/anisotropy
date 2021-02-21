#!/usr/bin/env bash

cd src
# Generate mesh
python src/genmesh.py
python prefoam.py
cd ../

#
for alpha in $( find build/simple-cubic -maxdepth 1 -type d); do
    path="$alpha/system/controlDict"
    
    if [ -f $path ]; then
        ideasUnvFoam -case $path mesh.unv
        checkMesh -case $path
        foamDictionary -case $path constant/polyMesh/boundary -entry entry0.wall.type -set wall
        decomposePar -case $path
        mpirun -np 4 --oversubscribe simpleFoam -parallel -case $path > $path/simpleFoam.log
    fi
done
