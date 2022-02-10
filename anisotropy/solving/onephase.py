# -*- coding: utf-8 -*-

import numpy as np

import anisotropy.openfoam as of
from anisotropy.openfoam import presets
from anisotropy.openfoam import commands


class FlowOnePhase:
    def __init__(
        self,
        path: str = None,
        direction: list[float] = None,
        patches: dict = None,
        pressureInlet: float = None,
        pressureOutlet: float = None,
        pressureInternal: float = None,
        velocityInlet: float = None,
        velocityOutlet: float = None,
        velocityInternal: float = None,
        density: float = None,
        viscosityKinematic: float = None,
        **kwargs
    ):
        
        self.direction = direction 
        self.patches = patches
        self.path = path
        self.case = None
        self.boundaryNames = ["inlet", "outlet", "symetry", "wall"]

        self.pressureInlet = pressureInlet 
        self.pressureOutlet = pressureOutlet 
        self.pressureInternal = pressureInternal 
        self.velocityInlet = velocityInlet 
        self.velocityOutlet = velocityOutlet 
        self.velocityInternal = velocityInternal 
        self.density = density 
        self.viscosityKinematic = viscosityKinematic

    def controlDict(self) -> of.FoamFile:
        ff = presets.controlDict()
        ff.update(
            startFrom = "latestTime",
            endTime = 5000,
            writeInterval = 100,
            runTimeModifiable = "true"
        )

        return ff

    def fvSchemes(self) -> of.FoamFile:
        ff = presets.fvSchemes()

        return ff
    
    def fvSolution(self) -> of.FoamFile:    
        ff = presets.fvSolution()
        ff["solvers"]["U"].update(
            nSweeps = 2,
            tolerance = 1e-08,
            smoother = "GaussSeidel"
        )
        ff["solvers"]["Phi"] = dict(
            solver = "GAMG",
            smoother = "DIC",
            cacheAgglomeration = "yes",
            agglomerator = "faceAreaPair",
            nCellsInCoarsestLevel = 10,
            mergeLevels = 1,
            tolerance = 1e-06,
            relTol = 0.01
        )
        ff["potentialFlow"] = dict(
            nNonOrthogonalCorrectors = 13,
            PhiRefCell = 0,
            PhiRefPoint = 0,
            PhiRefValue = 0,
            Phi = 0
        )
        ff["cache"] = { "grad(U)": None }
        ff["SIMPLE"].update(
            nNonOrthogonalCorrectors = 6,
            residualControl = dict(
                p = 1e-05,
                U = 1e-05
            )
        )
        ff["relaxationFactors"]["equations"]["U"] = 0.5

        return ff

    def transportProperties(self) -> of.FoamFile:
        ff = presets.transportProperties()
        ff.update(
            nu = self.viscosityKinematic
        )

        return ff
        
    def turbulenceProperties(self) -> of.FoamFile:
        ff = presets.turbulenceProperties()
        ff.content = dict(
            simulationType = "laminar"
        )

        return ff

    def p(self) -> of.FoamFile:
        ff = presets.p()
        ff["boundaryField"] = {}

        for boundary in self.boundaryNames:
            if boundary == "inlet":
                ff["boundaryField"][boundary] = dict(
                    type = "fixedValue",
                    value = of.utils.uniform(self.pressureInlet / self.density)
                )

            elif boundary == "outlet":
                ff["boundaryField"][boundary] = dict(
                    type = "fixedValue",
                    value = of.utils.uniform(self.pressureOutlet / self.density)
                )

            else:
                ff["boundaryField"][boundary] = dict(
                    type = "zeroGradient"
                )
 
        return ff

    def U_approx(self) -> of.FoamFile:
        ff = presets.U()
        ff["boundaryField"] = {}

        for boundary in self.boundaryNames:
            if boundary == "inlet":
                ff["boundaryField"][boundary] = dict(
                    type = "fixedValue",
                    value = of.utils.uniform(np.array(self.direction) * -6e-5)
                )

            elif boundary == "outlet":
                ff["boundaryField"][boundary] = dict(
                    type = "zeroGradient",
                )

            else:
                ff["boundaryField"][boundary] = dict(
                    type = "fixedValue",
                    value = of.utils.uniform([0., 0., 0.])
                ) 

        return ff

    def U(self) -> of.FoamFile:
        ff = presets.U()
        ff["boundaryField"] = {}

        for boundary in self.boundaryNames:
            if boundary == "inlet":
                ff["boundaryField"][boundary] = dict(
                    type = "pressureInletVelocity",
                    value = of.utils.uniform(self.velocityInlet)
                )

            elif boundary == "outlet":
                ff["boundaryField"][boundary] = dict(
                    type = "zeroGradient",
                )

            else:
                ff["boundaryField"][boundary] = dict(
                    type = "fixedValue",
                    value = of.utils.uniform([0., 0., 0.])
                ) 

        return ff

    def createPatchDict(self) -> of.FoamFile:
        # initial 43 unnamed patches ->
        # 6 named patches (inlet, outlet, wall, symetry 0 to 3 or 5) ->
        # 4 inGroups (inlet, outlet, wall, symetry)

        ff = presets.createPatchDict()
        ff["patches"] = []

        for name in self.patches.keys():
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

            ff["patches"].append({
                "name": name,
                "patchInfo": {
                    "type": patchType,
                    "inGroups": [patchGroup]
                },
                "constructFrom": "patches",
                "patches": self.patches[name]
            })

        return ff

    def generate(self, approximation: bool = False, meshfile: str = "mesh.mesh"):

        self.case = of.FoamCase(
            path = self.path,
            files = [
                self.controlDict(),
                self.fvSchemes(),
                self.fvSolution(),
                self.transportProperties(), 
                self.turbulenceProperties(),
                self.p()
            ]
        )

        if self.patches is not None:
            self.case += self.createPatchDict()
        
        self.case += self.U_approx() if approximation else self.U()
        
        self.case.write(self.path)

        self.case.chdir()

        commands.netgenNeutralToFoam(meshfile)

        # TODO: contain
        if self.case.contains("createPatchDict"):
            commands.createPatch()

        commands.checkMesh()
        commands.transformPoints({
            "scale": [1e-5, 1e-5, 1e-5]
        })
        commands.renumberMesh()

        if approximation:
            commands.potentialFoam()

            #   replace velocity for the main simulation
            self.case += self.U()
            self.case.write(self.path)
        
        commands.simpleFoam()

        self.case.chback()
