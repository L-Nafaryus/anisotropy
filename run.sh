#!/usr/bin/env bash

path=.
#build/simple-cubic/0.1

# python src/genmesh.py
# python src/prefoam.py

rm -r postProcessing processor* *.log logs constant/polymesh

ideasUnvFoam -case $path mesh.unv
polyDualMesh 70 -overwrite
checkMesh -case $path -allGeometry -allTopology
foamDictionary -case $path constant/polyMesh/boundary -entry entry0.wall.type -set wall


potentialFoam -case $path

decomposePar -case $path

foamDictionary -case $path 0/U -entry boundary.inlet.type -set pressureInletVelocity
foamDictionary -case $path 0/U -entry boundary.inlet.value -set 'uniform (0 0 0)'
mpirun -np 4 --oversubscribe simpleFoam -parallel -case $path > $path/simpleFoam.log

