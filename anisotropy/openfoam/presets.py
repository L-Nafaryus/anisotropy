# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from anisotropy.openfoam.foamfile import FoamFile

class ControlDict(FoamFile):
    def __init__(self):
        FoamFile.__init__(self,
            "system/controlDict",
            _location = "system"
        )
        self.content = {
            "application": "simpleFoam",
            "startFrom": "startTime",
            "startTime": 0,
            "stopAt": "endTime",
            "endTime": 2000,
            "deltaT": 1,
            "writeControl": "timeStep",
            "writeInterval": 100,
            "purgeWrite": 0,
            "writeFormat": "ascii",
            "writePrecision": 6,
            "writeCompression": "off",
            "timeFormat": "general",
            "timePrecision": 6,
            "runTimeModifiable": "true"
        }

class FvSolution(FoamFile):
    def __init__(self):
        FoamFile.__init__(self,
            "system/fvSolution",
            _location = "system"
        )
        self.content = {
            "solvers": {
                "p": {
                    "solver": "GAMG",
                    "tolerance": 1e-06,
                    "relTol": 0.1,
                    "smoother": "GaussSeidel"
                },
                "U": {
                    "solver": "smoothSolver",
                    "smoother": "symGaussSeidel",
                    "tolerance": 1e-05,
                    "relTol": 0.1
                }
            },
            "SIMPLE": {
                "nNonOrthogonalCorrectors": 0,
                "consistent": "yes",
                "residualControl": {
                    "p": 1e-02,
                    "U": 1e-03
                }
            },
            "relaxationFactors": {
                "fields": {
                    "p": 0.3
                },
                "equations": {
                    "U": 0.7
                }
            }
        }

class FvSchemes(FoamFile):
    def __init__(self):
        FoamFile.__init__(self,
            "system/fvSchemes",
            _location = "system"
        )
        self.content = {
            "ddtSchemes": {
                "default": "steadyState"
            }, 
            "gradSchemes": {
                "default": ("Gauss", "linear")
            }, 
            "divSchemes": {
                "default": "none", 
                "div(phi,U)": ("bounded", "Gauss", "linearUpwind", "grad(U)"), 
                "div((nuEff*dev2(T(grad(U)))))": ("Gauss", "linear"), 
                "div(nonlinearStress)": ("Gauss", "linear")
            }, 
            "laplacianSchemes": {
                "default": ("Gauss", "linear", "corrected")
            }, 
            "interpolationSchemes": {
                "default": "linear"
            }, 
            "snGradSchemes": {
                "default": "corrected"
            } 
        }

class TransportProperties(FoamFile):
    def __init__(self):
        FoamFile.__init__(self,
            "constant/transportProperties",
            _location = "constant"
        )
        self.content = {
            "transportModel": "Newtonian",
            "nu": 1e-05
        }

class TurbulenceProperties(FoamFile):
    def __init__(self):
        FoamFile.__init__(self,
            "constant/turbulenceProperties",
            _location = "constant"
        )
        self.content = {
            "simulationType": "RAS", 
            "RAS": {
                "RASModel": "kEpsilon", 
                "turbulence": "on", 
                "printCoeffs": "on"
            }
        }

class P(FoamFile):
    def __init__(self):
        FoamFile.__init__(self,
            "0/p",
            _location = "0",
            _class = "volScalarField"
        )
        self.content = {
            "dimensions": "[0 2 -2 0 0 0 0]",
            "internalField": "uniform 0",
            "boundaryField": {
                "inlet": {
                    "type": "fixedValue",
                    "value": "uniform 0.001"
                },
                "outlet": {
                    "type": "fixedValue",
                    "value": "uniform 0"
                },
                "wall": {
                    "type": "zeroGradient"
                }
            }
        }

class U(FoamFile):
    def __init__(self):
        FoamFile.__init__(self,
            "0/U",
            _location = "0",
            _class = "volVectorField"
        )
        self.content = {
            "dimensions": "[0 1 -1 0 0 0 0]",
            "internalField": "uniform (0 0 0)",
            "boundaryField": {
                "inlet": {
                    "type": "fixedValue",
                    "value": "uniform (0 0 -6e-5)"
                },
                "outlet": {
                    "type": "zeroGradient",
                },
                "wall": {
                    "type": "fixedValue",
                    "value": "uniform (0 0 0)"
                }
            }
        }

class CreatePatchDict(FoamFile):
    def __init__(self):
        FoamFile.__init__(self,
            "system/createPatchDict",
            _location = "system",
        )
        self.content = {
            "pointSync": False,
            "patches": [
                {
                    "name": "inlet",
                    "patchInfo": {
                        "type": "patch",
                        "inGroups": ["inlet"]
                    },
                    "constructFrom": "patches",
                    "patches": ["some_inlet"]
                },
                {
                    "name": "output",
                    "patchInfo": {
                        "type": "patch",
                        "inGroups": ["outlet"]
                    },
                    "constructFrom": "patches",
                    "patches": ["some_outlet"]
                },
                {
                    "name": "wall",
                    "patchInfo": {
                        "type": "wall",
                        "inGroups": ["wall"]
                    },
                    "constructFrom": "patches",
                    "patches": ["some_wall"]
                }
            ]
        }

class DecomposeParDict(FoamFile):
    def __init__(self):
        FoamFile.__init__(self,
            "system/decomposeParDict",
            _location = "system",
        )
        self.content = {
            "numberOfSubdomains": 4,
            "method": "simple",
            "coeffs": {
                "n": [2, 2, 2]
            }
        }
