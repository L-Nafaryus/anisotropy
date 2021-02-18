import os
import subprocess
import multiprocessing

path = os.getcwd()
cube = os.path.join(path, "cube/main.py")

alpha = [0.1, 0.15, 0.2]
processes = []

def salome(exePath, arg):
    subprocess.run(["salome", "start", "-t", exePath, "args:%s" % arg])

for c in alpha:
    print("starting process")
    p = multiprocessing.Process(target = salome, args = (cube, c))
    processes.append(p)
    p.start()

for process in processes:
    process.join()
