# -*- coding: utf-8 -*-

from . import FoamFile


def controlDict() -> FoamFile:
    ff = FoamFile(filename = "system/controlDict")

    ff.content = {
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

    return ff


def fvSolution() -> FoamFile:
    ff = FoamFile(filename = "system/fvSolution")

    ff.content = {
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

    return ff


def fvSchemes() -> FoamFile:
    ff = FoamFile(filename = "system/fvSchemes")

    ff.content = {
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

    return ff


def transportProperties() -> FoamFile:
    ff = FoamFile(filename = "constant/transportProperties")

    ff.content = {
        "transportModel": "Newtonian",
        "nu": 1e-05
    }

    return ff


def turbulenceProperties() -> FoamFile:
    ff = FoamFile(filename = "constant/turbulenceProperties")

    ff.content = {
        "simulationType": "RAS", 
        "RAS": {
            "RASModel": "kEpsilon", 
            "turbulence": "on", 
            "printCoeffs": "on"
        }
    }

    return ff


def p() -> FoamFile:
    ff = FoamFile("0/p", _class = "volScalarField")

    ff.content = {
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

    return ff


def U() -> FoamFile:
    ff = FoamFile("0/U", _class = "volVectorField")

    ff.content = {
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

    return ff


def createPatchDict() -> FoamFile:
    ff = FoamFile("system/createPatchDict")

    ff.content = {
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

    return ff


def decomposeParDict() -> FoamFile:
    ff = FoamFile("system/decomposeParDict")

    ff.content = {
        "numberOfSubdomains": 4,
        "method": "simple",
        "coeffs": {
            "n": [2, 2, 2]
        }
    }

    return ff
