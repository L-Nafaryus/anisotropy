import os
import subprocess
import multiprocessing
import logging
import time
from datetime import timedelta

def salome(port, src_path, build_path, coefficient, direction):
    """
    Run salome and terminate after.

    Parameters:
        port (int): Port for the process.
        src_path (str): Path to the execution script.
        build_path (str): Output path.
    """
    logging.info("Starting SALOME on port {}.".format(port))
    salomelog = open("{}/salome.log".format(build_path), "a")

    subprocess.run([
        "salome", "start", 
        "--port", str(port), 
        "-t", src_path, 
        "args:{},{},{}".format(build_path, coefficient, direction)
        ], 
        stdout=salomelog, 
        stderr=salomelog)
        
    logging.info("Terminating SALOME on port {}.".format(port))
    
    subprocess.run([
        "salome", "kill", 
        str(port)
        ],
        stdout=salomelog,
        stderr=salomelog)

    salomelog.close()


if __name__ == "__main__":
    # Get main paths
    project = os.getcwd()
    src = os.path.join(project, "src")
    build = os.path.join(project, "build")
    
    if not os.path.exists(build):
        os.makedirs(build) 

    # Logger
    logging.basicConfig(
        level=logging.INFO, 
        format="%(levelname)s: %(message)s",
        handlers = [
            logging.StreamHandler(),
            logging.FileHandler("{}/genmesh.log".format(build))
        ])
    start_time = time.monotonic()
    
    # Start in parallel
    processes = []
    structures = ["simpleCubic"] #, "bc-cubic", "fc-cubic"]
    directions = ["001"] #, "100", "111"]
    coefficients = [0.1] #[ alpha * 0.01 for alpha in range(1, 13 + 1) ]
    port = 2810

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

                p = multiprocessing.Process(target = salome, 
                    args = (port, src_path, build_path, coefficient, direction))
                processes.append(p)
                p.start()
                logging.info("{} on port {}.".format(p, port))
                port += 1

    for process in processes:
        process.join()

    end_time = time.monotonic()
    logging.info("Elapsed time: {}".format(timedelta(seconds=end_time - start_time)))

