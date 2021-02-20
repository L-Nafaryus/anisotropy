#!/usr/bin/env bash

path=build/simple-cubic/0.1

# python src/genmesh.py
# python src/prefoam.py

ideasUnvFoam -case $path mesh.unv
checkMesh -case $path
foamDictionary -case $path constant/polyMesh/boundary -entry entry0.wall.type -set wall
#potentialFoam -case $path
decomposePar -case $path
mpirun -np 4 --oversubscribe simpleFoam -parallel -case $path > $path/simpleFoam.log

