import matplotlib.pyplot as plt
from math import sqrt
import sys, os

if __name__ == "__main__":
    
    BUILD = "../build"
    postProcessing = "postProcessing/flowRatePatch(name=outlet)/0/surfaceFieldValue.dat"

    #structures = [
    #    "simple",
    #    #"bodyCentered",
    #    #"faceCentered"
    #]

    theta = [c * 0.01 for c in range(1, 28 + 1)]
    directions = [
        [1, 0, 0],
        [0, 0, 1],
        [1, 1, 1]
    ]
    flowrate = [ [] for n in range(3) ]

    #nu = 1e-06
    #p = [1e-03, 0]

    for num, d in enumerate(directions):
        for t in theta:
            path = os.path.join(
                BUILD, 
                "simple", 
                "direction-{}{}{}".format(*d), 
                "theta-{}".format(t), 
                postProcessing
            )

            with open(path, "r") as io:
                lastLine = io.readlines()[-1]

            value = lastLine.replace(" ", "").replace("\n", "").split("\t")[1]
            flowrate[num].append(float(value))

    k2, k3 = [], []

    for n, _ in enumerate(flowrate[0]):
        k2.append(2 * flowrate[1][n] / flowrate[0][n])
        k3.append(2 * flowrate[2][n] / flowrate[0][n])

    
    plt.figure(1)
    
    ax = plt.subplot(211)
    line, = ax.plot(theta, flowrate[0], "o")
    line.set_label("[1, 0, 0]")

    line, = ax.plot(theta, flowrate[1], "o")
    line.set_label("[0, 0, 1]")

    line, = plt.plot(theta, flowrate[2], "o")
    line.set_label("[1, 1, 1]")
    
    ax.set_yscale("log")

    plt.legend()
    plt.grid(True)
    plt.xlabel("theta")
    plt.ylabel("flowRate")
    
    ax = plt.subplot(212)
    line, = ax.plot(theta, k2, "o")
    line.set_label("k2")
    line, = ax.plot(theta, k3, "o")
    line.set_label("k3")
    plt.legend()
    plt.grid(True)
    plt.xlabel("theta")
    plt.ylabel("k")

    plt.show()
