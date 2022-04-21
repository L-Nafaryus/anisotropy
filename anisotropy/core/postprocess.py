# -*- coding: utf-8 -*-

import pathlib
import numpy as np

import anisotropy.openfoam as of


def flowRate(patch: str, path: str = None):
    func = f"patchFlowRate(patch={ patch })"

    path = pathlib.Path(path or "").resolve()
    outfile = path / "postProcessing" / func / "0/surfaceFieldValue.dat"

    of.commands.postProcess(func, cwd = path, logpath = path / "patchFlowRate.log")
    surfaceFieldValue = of.conversion.read_dat(outfile)["sum(phi)"][-1]

    return surfaceFieldValue


def permeability(viscosity = None, flowRate = None, length = None, areaCross = None, pressureInlet = None, pressureOutlet = None, **kwargs):
    viscosity = kwargs.get("viscosity", viscosity)
    flowRate = kwargs.get("flowRate", flowRate)
    length = kwargs.get("length", length)
    areaCross = kwargs.get("areaCross", areaCross)
    pressureInlet = kwargs.get("pressureInlet", pressureInlet)
    pressureOutlet = kwargs.get("pressureOutlet", pressureOutlet)

    return viscosity * length * flowRate / (areaCross * (pressureInlet - pressureOutlet))


def mean_nan(arr):
    temp = arr.copy()

    if np.isnan(temp[0]):
        temp[0] = temp[1]

    for n, item in enumerate(temp):
        if np.all(np.isnan(item)):
            
            vals = temp[n - 1 : n + 2]

            if np.sum(~np.isnan(vals)) <= 1:
                vals = temp[n - 2 : n + 3]

            temp[n] = vals[~np.isnan(vals)].mean()

    return temp


def filter_group(arr, nan = True, qhigh = True, quantile = 0.97):
    temp = arr.copy()
    check = True
    quan = np.quantile(temp[~np.isnan(temp)], quantile)
    limit = 1000

    while check:
        if nan and np.any(np.isnan(temp)):
            temp = mean_nan(temp)
            check = True
        
        elif qhigh and np.any(quan < temp):
            temp[quan < temp] = np.nan
            check = True

        else:
            check = False 
        
        if limit <= 0:
            break

        else:
            limit -= 1

    return temp


def pad_nan(x, y):
    return np.pad(y, (0, x.size - y.size), 'constant', constant_values = np.nan)


"""
def multiplot_y(
    x, 
    y,
    labels = [],
    lines = [],
    axes_labels = ["", ""],
    legend = True,
    grid = True,
    figsize = (12, 6)
    ):
    fig, ax = plt.subplots(nrows = 1, ncols = 1, figsize = figsize)

    for n, y_arr in enumerate(y):
        ax.plot(x, y_arr, )
"""
