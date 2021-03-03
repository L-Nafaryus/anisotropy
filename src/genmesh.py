import os
import subprocess
import multiprocessing

def salome(src_path, build_path, coefficient, direction):
    subprocess.run(["salome", "start", "-t", src_path, "args:{},{}".format(build_path, coefficient, direction)])

if __name__ == "__main__":
    # Get main paths
    project = os.getcwd()
    src = os.path.join(project, "src")
    build = os.path.join(project, "build")

    if not os.path.exists(build):
        os.makedirs(build)

    ###
    processes = []
    structures = ["simple-cubic"] #, "bc-cubic", "fc-cubic"]
    directions = ["001", "100"]
    coefficients = [ alpha * 0.01 for alpha in range(1, 13 + 1) ]

    for structure in structures:
        for direction in directions:
            for coefficient in coefficients:
                src_path = os.path.join(src, "{}.py".format(structure))
                build_path = os.path.join(build, 
                    structure, 
                    "direction-{}".format(direction), 
                    "alpha-{}".format(coefficient))
                
                if not os.path.exists(build_path):
                    os.makedirs(build_path)

                print("starting process")
                p = multiprocessing.Process(target = salome, args = (src_path, build_path, coefficient, direction))
                processes.append(p)
                p.start()

    for process in processes:
        process.join()
