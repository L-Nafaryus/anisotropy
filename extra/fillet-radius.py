import matplotlib.pyplot as plt
from math import sqrt
import sys

if __name__ == "__main__":
    
    try:
        stype = sys.argv[1]

    except IndexError:
        print("python fillet-radius.py [simple|bodyCentered|faceCentered]")

        exit(1)


    if stype == "simple":
        r0 = 1.0
        
        C1, C2 = 0.8, 0.5
        theta1, theta2 = 0.01, 0.28
        
        delta = 0.2

    elif stype == "bodyCentered":
        L = 1.0
        r0 = L * sqrt(3) / 4

        C1, C2 = 0.3, 0.2
        theta1, theta2 = 0.01, 0.18
        
        delta = 0.02

    elif stype == "faceCentered":
        L = 1.0
        r0 = L * sqrt(2) / 4

        C1, C2 = 0.3, 0.2
        theta1, theta2 = 0.01, 0.13

        delta = 0.012

    else:
        print("python fillet-radius.py [simple|bodyCentered|faceCentered]")

        exit(1)


    Cf = lambda theta: C1 + (C2 - C1) / (theta2 - theta1) * (theta - theta1)
    fillet = lambda theta: delta - Cf(theta) * (r0 / (1 - theta) - r0) 
    
    tocount = lambda num: int(num * 100)

    theta = [ 0.01 * n for n in range(tocount(theta1), tocount(theta2) + 1) ]
    coeffs = [ Cf(n) for n in theta ]
    radiuses = [ fillet(n) for n in theta ]

    plt.figure(1)
    
    plt.subplot(211)
    plt.plot(theta, coeffs, "o")
    plt.grid(True)
    plt.ylabel("Cf")

    plt.subplot(212)
    plt.plot(theta, radiuses, "o")
    plt.grid(True)
    plt.ylabel("Radius")
    plt.xlabel("Theta")
    
    plt.show()
