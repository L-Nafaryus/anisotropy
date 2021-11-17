# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import anisotropy.openfoam as openfoam
from openfoam.presets import (
    ControlDict, FvSchemes, FvSolution, 
    TransportProperties, TurbulenceProperties, CreatePatchDict,
    P, U
)
from openfoam.foamcase import FoamCase

class OnePhaseFlow(FoamCase):
    def __init__(self):
        FoamCase.__init__(self)

        controlDict = ControlDict()
        controlDict.update(
            startFrom = "latestTime",
            endTime = 5000,
            writeInterval = 100,
            runTimeModifiable = "true"
        )

        fvSchemes = FvSchemes()
        
        fvSolution = FvSolution()
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

        transportProperties = TransportProperties()
        transportProperties.update(
            nu = 1e-06
        )
        
        turbulenceProperties = TurbulenceProperties()
        turbulenceProperties.content = dict(
            simulationType = "laminar"
        )

        createPatchDict = CreatePatchDict()
        createPatchDict["patches"] = []
        
        for patch in ["inlet", "outlet", "wall", "strips", *[ f"symetry{ n }" for n in range(6) ]]:
            newPatch = dict(
                name = patch,
                patchInfo = dict(
                    type = "patch",
                    inGroups = [patch]
                ),
                constructFrom = "patches",
                patches = [ f"smesh_{ patch }" ]
            )

            match patch:
                case "wall" | "strips":
                    newPatch["patchInfo"].update(
                        type = "wall",
                        inGroups = [ "wall" ]
                    )

                case patch if patch.find("symetry") == 0:
                    newPatch["patchInfo"]["inGroups"] = [ "symetryPlane" ]

            createPatchDict["patches"].append(newPatch)


        boundaries = [ "inlet", "outlet", "symetryPlane", "wall", "strips" ]
        p = P()
        p["boundaryField"] = {}
        u = U()
        u["boundaryField"] = {}

        # ISSUE: add proxy from geometry direction to outlet boundaryField.
        for boundary in boundaries:
            match boundary:
                case "inlet":
                    p["boundaryField"][boundary] = dict(
                        type = "fixedValue",
                        value = "uniform 1e-3"
                    )
                    u["boundaryField"][boundary] = dict(
                        type = "fixedValue",
                        value = "uniform (0 0 -6e-5)" # * direction
                    )

                case "outlet":
                    p["boundaryField"][boundary] = dict(
                        type = "fixedValue",
                        value = "uniform 0"
                    )
                    u["boundaryField"][boundary] = dict(
                        type = "zeroGradient",
                    )

                case _:
                    p["boundaryField"][boundary] = dict(
                        type = "zeroGradient"
                    )
                    u["boundaryField"][boundary] = dict(
                        type = "fixedValue",
                        value = "uniform (0 0 0)"
                    ) 

        self.extend([
            controlDict, fvSchemes, fvSolution, createPatchDict,
            transportProperties, turbulenceProperties,
            p, u
        ])

    def build(self):
        # TODO: configure working directory (FoamCase)
        self.write()

        openfoam.ideasUnvToFoam("mesh.unv")
        openfoam.createPatch()
        openfoam.checkMesh()
        openfoam.transformPoints((1e-5, 1e-5, 1e-5))
        openfoam.renumberMesh()
        openfoam.potentialFoam()
        
        self.read()

        self.solution.U["boundaryField"]["outlet"] = dict(
            type = "pressureInletVelocity",
            value = "uniform (0 0 0)" # * direction
        )
        self.write()
        
        openfoam.simpleFoam()
