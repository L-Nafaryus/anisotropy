import os
import subprocess
import multiprocessing

src = os.getcwd()
build = os.path.join(src, "../build")

if not os.path.exists(build):
    os.makedirs(build)

###

alpha = []

for n in range(0.01, 0.13 + 0.01, 0.01):
    alpha.append(n)

# Structures
simpleCubic = os.path.join(src, "simple-cubic/main.py")
# Body-centered cubic
#bcCubic = os.path.join(path, "bc-cubic/main.py")
# Face-centered cubic
#fcCubic = os.path.join(path, "fc-cubic/main.py")

###

processes = []
structure = ["simple-cubic"] #, "bc-cubic", "fc-cubic"]
direction = ["1"]

def salome(src_path, build_path, arg):
    subprocess.run(["salome", "start", "-t", src_path, "args:{},{}".format(build_path, arg)])

for s in structure:
    s_path = os.path.join(build, s)
    
    for d in direction:
        d_path = os.path.join(s_path, d)

        for c in alpha:
            src_path = os.path.join(src, "%s/main.py" % s)
            build_path = os.path.join(d_path, str(c))
            
            if not os.path.exists(build_path):
                os.makedirs(build_path)

            print("starting process")
            p = multiprocessing.Process(target = salome, args = (src_path, build_path, c))
            processes.append(p)
            p.start()

        for process in processes:
            process.join()