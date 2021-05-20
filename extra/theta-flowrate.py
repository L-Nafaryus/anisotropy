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

    
    plt.figure(1)
    
    #plt.subplot(211)
    line, = plt.plot(theta, flowrate[0], "o")
    line.set_label("[1, 0, 0]")
    #plt.grid(True)
    #plt.legend()
    #plt.xlabel("theta")
    #plt.ylabel("flowRate")

    #plt.subplot(212)
    line, = plt.plot(theta, flowrate[1], "o")
    line.set_label("[0, 0, 1]")
    #plt.grid(True)
    #plt.xlabel("theta")
    #plt.ylabel("flowRate")

    #plt.subplot(213)
    line, = plt.plot(theta, flowrate[2], "o")
    line.set_label("[1, 1, 1]")
    plt.legend()
    plt.grid(True)
    plt.xlabel("theta")
    plt.ylabel("flowRate")
    plt.show()
