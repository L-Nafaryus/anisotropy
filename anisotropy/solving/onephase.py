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
    def __init__(
        self,
        direction: list[float] = None,
        pressureInlet: float = None,
        pressureOutlet: float = None,
        pressureInternal: float = None,
        velocityInlet: float = None,
        velocityOutlet: float = None,
        velocityInternal: float = None,
        density: float = None,
        viscosityKinematic: float = None,
        path: str = None,
        **kwargs
    ):
        FoamCase.__init__(self, path = path)

        self.direction = direction 
        self.pressureInlet = pressureInlet 
        self.pressureOutlet = pressureOutlet 
        self.pressureInternal = pressureInternal 
        self.velocityInlet = velocityInlet 
        self.velocityOutlet = velocityOutlet 
        self.velocityInternal = velocityInternal 
        self.density = density 
        self.viscosityKinematic = viscosityKinematic

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
            tolerance = 1e-08,
            smoother = "GaussSeidel"
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
            nNonOrthogonalCorrectors = 13,
            PhiRefCell = 0,
            PhiRefPoint = 0,
            PhiRefValue = 0,
            Phi = 0
        )
        fvSolution["cache"] = { "grad(U)": None }
        fvSolution["SIMPLE"].update(
            nNonOrthogonalCorrectors = 6,
            residualControl = dict(
                p = 1e-05,
                U = 1e-05
            )
        )
        fvSolution["relaxationFactors"]["equations"]["U"] = 0.5

        transportProperties = F.TransportProperties()
        transportProperties.update(
            nu = self.viscosityKinematic
        )
        
        turbulenceProperties = F.TurbulenceProperties()
        turbulenceProperties.content = dict(
            simulationType = "laminar"
        )

        boundaries = ["inlet", "outlet", "symetry", "wall"]
        p = F.P()
        p["boundaryField"] = {}
        u = F.U()
        u["boundaryField"] = {}

        for boundary in boundaries:
            if boundary == "inlet":
                p["boundaryField"][boundary] = dict(
                    type = "fixedValue",
                    value = uniform(self.pressureInlet / self.density)
                )
                u["boundaryField"][boundary] = dict(
                    type = "fixedValue",
                    value = uniform(array(self.direction) * -6e-5)
                )

            elif boundary == "outlet":
                p["boundaryField"][boundary] = dict(
                    type = "fixedValue",
                    value = uniform(self.pressureOutlet / self.density)
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

    
    def createPatches(self, patches: dict):
        # initial 43 unnamed patches ->
        # 6 named patches (inlet, outlet, wall, symetry0 - 3/5) ->
        # 4 inGroups (inlet, outlet, wall, symetry)

        createPatchDict = F.CreatePatchDict()
        createPatchDict["patches"] = []

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

        self.append(createPatchDict)

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
            #R.potentialFoam()

            self.read()

            self.U["boundaryField"]["inlet"] = dict(
                type = "pressureInletVelocity",
                value = uniform(self.velocityInlet)
            )
            self.write()

            R.simpleFoam()

        return "", "", 0
