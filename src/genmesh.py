import os
import subprocess
import multiprocessing

path = os.getcwd()
cube = os.path.join(path, "cube/main.py")
print(cube)
alpha = [0.1, 0.15]
processes = []

def genmesh(coef):
    subprocess.run(["salome", "-t", "{} {}".format(cube, str(coef))])

for c in alpha:
    print("starting process")
    p = multiprocessing.Process(target=genmesh, args=(c,))
    processes.append(p)
    p.start()

for process in processes:
    process.join()
