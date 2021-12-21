# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import anisotropy.openfoam.presets as F
import anisotropy.openfoam.runnerPresets as R
from anisotropy.openfoam import FoamCase, uniform
from numpy import array
import logging

logger = logging.getLogger(__name__)

class OnePhaseFlow(FoamCase):
    def __init__(self, direction, path: str = None):
        FoamCase.__init__(self, path = path)

        controlDict = F.ControlDict()
        controlDict.update(
            startFrom = "latestTime",
            endTime = 5000,
            writeInterval = 100,
            runTimeModifiable = "true"
        )

        fvSchemes = F.FvSchemes()
        
        fvSolution = F.FvSolution()
        fvSolution["solvers"]["U"].update(
            nSweeps = 2,
            tolerance = 1e-08
        )
        fvSolution["solvers"]["Phi"] = dict(
            solver = "GAMG",
            smoother = "DIC",
            cacheAgglomeration = "yes",
            agglomerator = "faceAreaPair",
            nCellsInCoarsestLevel = 10,
            mergeLevels = 1,
            tolerance = 1e-06,
            relTol = 0.01
        )
        fvSolution["potentialFlow"] = dict(
            nNonOrthogonalCorrectors = 20,
            PhiRefCell = 0,
            PhiRefPoint = 0,
            PhiRefValue = 0,
            Phi = 0
        )
        fvSolution["cache"] = { "grad(U)": None }
        fvSolution["SIMPLE"].update(
            nNonOrthogonalCorrectors = 10,
            residualControl = dict(
                p = 1e-05,
                U = 1e-05
            )
        )
        fvSolution["relaxationFactors"]["equations"]["U"] = 0.5

        transportProperties = F.TransportProperties()
        transportProperties.update(
            nu = 1e-06
        )
        
        turbulenceProperties = F.TurbulenceProperties()
        turbulenceProperties.content = dict(
            simulationType = "laminar"
        )

        boundaries = [ "inlet", "outlet", "symetry", "wall"]
        p = F.P()
        p["boundaryField"] = {}
        u = F.U()
        u["boundaryField"] = {}

        # ISSUE: add proxy from geometry direction to outlet boundaryField.
        for boundary in boundaries:
            if boundary == "inlet":
                p["boundaryField"][boundary] = dict(
                    type = "fixedValue",
                    value = uniform(1e-3)
                )
                u["boundaryField"][boundary] = dict(
                    type = "fixedValue",
                    value = uniform(array(direction) * -6e-5) # uniform([0, 0, -6e-5])
                )

            elif boundary == "outlet":
                p["boundaryField"][boundary] = dict(
                    type = "fixedValue",
                    value = uniform(0)
                )
                u["boundaryField"][boundary] = dict(
                    type = "zeroGradient",
                )

            else:
                p["boundaryField"][boundary] = dict(
                    type = "zeroGradient"
                )
                u["boundaryField"][boundary] = dict(
                    type = "fixedValue",
                    value = uniform([0, 0, 0])
                ) 

        self.extend([
            controlDict, 
            fvSchemes, 
            fvSolution,
            transportProperties, 
            turbulenceProperties,
            p, 
            u
        ])

    @staticmethod
    def facesToPatches(faces: tuple[int, str]):
        # initial 43 unnamed patches ->
        # 6 named patches (inlet, outlet, wall, symetry0 - 3/5) ->
        # 4 inGroups (inlet, outlet, wall, symetry)

        createPatchDict = F.CreatePatchDict()
        createPatchDict["patches"] = []
        patches = {}

        for n, name in faces:
            #   shifted index
            n += 1

            if patches.get(name):
                patches[name].append(f"patch{n}")

            else:
                patches[name] = [f"patch{n}"]

        for name in patches.keys():
            if name == "inlet":
                patchGroup = "inlet"
                patchType = "patch"

            elif name == "outlet":
                patchGroup = "outlet"
                patchType = "patch"

            elif name == "wall":
                patchGroup = "wall"
                patchType = "wall"

            else:
                patchGroup = "symetry"
                patchType = "symetryPlane"

            createPatchDict["patches"].append({
                "name": name,
                "patchInfo": {
                    "type": patchType,
                    "inGroups": [patchGroup]
                },
                "constructFrom": "patches",
                "patches": patches[name]
            })

        return createPatchDict

    def build(self) -> tuple[str, str, int]:
        # TODO: configure working directory (FoamCase)
        with self:
            self.write()

            R.netgenNeutralToFoam("mesh.mesh")
            R.createPatch()
            R.checkMesh()
            R.transformPoints({
                "scale": [1e-5, 1e-5, 1e-5]
            })
            R.renumberMesh()
            R.potentialFoam()

            self.read()

            self.U["boundaryField"]["outlet"] = dict(
                type = "pressureInletVelocity",
                value = uniform([0, 0, 0])
            )
            self.write()

            R.simpleFoam()

        return "", "", 0
