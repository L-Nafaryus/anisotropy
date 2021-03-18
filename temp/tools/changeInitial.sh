#!/usr/bin/env bash

for n in {0..3}; do

    foamDictionary "processor${n}/0/U" -entry boundaryField.inlet.type -set pressureInletVelocity
    foamDictionary "processor${n}/0/U" -entry boundaryField.inlet.value -set 'uniform (0 0 0)'
done
