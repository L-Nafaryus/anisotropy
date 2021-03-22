import os, sys
from collections import namedtuple

ROOT = os.getcwd()
sys.path.append(ROOT)

import src.utils
import src.salome_utils

if __name__ == "__main__":
     
    nprocs = os.cpu_count()
    port = 2810
    salomeServers = []
    salomeServer = namedtuple("salomeServer", ["process", "port"])

    for n in range(nprocs):
        while not utils.portIsFree:
            port += 1

        s = salomeServer(salome_utils.startServer(port), port)
        salomeServers.append(s)

    var = []
    cmd = "python "
    
    # TODO: pass it to samples in namedtuples
    # get sample.directions and etc ..
    structures = [
        "simpleCubic", 
        "bodyCenteredCubic", 
        "faceCenteredCubic"
    ]
    directions = [
        [1, 0, 0],
        [0, 0, 1],
        [1, 1, 1]
    ]

    cmd += "-m "
    var.append((salomeServer[n].port, cmd))

    utils.parallel(nprocs, var, salome_utils.execute)



















if __name__ == "__main__":
    ###
    #   SALOME
    #
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
    structures = ["simpleCubic", "faceCenteredCubic", "bodyCenteredCubic"]
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

    
    ###
    #   FOAM
    #
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
            logging.FileHandler("{}/foam.log".format(build))
        ])
    start_time = time.monotonic()
    
    # Main entry
    structures = ["simpleCubic"] #, "bc-cubic", "fc-cubic"]
    directions = ["001"] #, "100", "111"]
    coefficients = [0.1] #[ alpha * 0.01 for alpha in range(1, 13 + 1) ]

    for structure in structures:
        for direction in directions:
            for coefficient in coefficients:
                foamCase = [ "0", "constant", "system" ]
                src_path = os.path.join(src, "{}Foam".format(structure))
                build_path = os.path.join(build, 
                    structure, 
                    "direction-{}".format(direction), 
                    "alpha-{}".format(coefficient))
                
                
                logging.info("Entry with parameters: {}, direction = {}, alpha = {}".format(structure, direction, coefficient))

                logging.info("Copying baseFOAM case ...")
                for d in foamCase:
                    if not os.path.exists(os.path.join(build_path, d)):
                        shutil.copytree(os.path.join(src_path, d), 
                            os.path.join(build_path, d))
                
                os.chdir(build_path)
                case_path = "."

                logging.info("Importing mesh to foam ...")
                ideasUnvToFoam(case_path, "{}-{}-{}.unv".format(structure, direction, coefficient))
                
                logging.info("Creating patches ...")
                createPatch(case_path)

                logging.info("Scaling mesh ...")
                transformPoints(case_path, "(1e-5 1e-5 1e-5)")
                
                logging.info("Checking mesh ...")
                checkMesh(case_path)
                
                #logging.info("Changing mesh boundaries types ...")
                #foamDictionarySet(case_path, "constant/polyMesh/boundary", "entry0.wall.type", "wall")
                #foamDictionarySet(case_path, "constant/polyMesh/boundary", "entry0.symetryPlane.type", "symetryPlane")

                logging.info("Decomposing case ...")
                decomposePar(case_path)
                
                logging.info("Evaluating initial approximation via potentialFoam ...")
                potentialFoam(case_path)
                
                logging.info("Preparing boundaryFields for simpleFoam ...")
                for n in range(4):
                    foamDictionarySet(case_path, "processor{}/0/U".format(n), 
                        "boundaryField.inlet.type", "pressureInletVelocity")
                    foamDictionarySet(case_path, "processor{}/0/U", 
                        "boundaryField.inlet.value", "uniform (0 0 0)")
                
                logging.info("Calculating ...")
                simpleFoam(case_path)

                os.chdir(project)

    end_time = time.monotonic()
    logging.info("Elapsed time: {}".format(timedelta(seconds=end_time - start_time)))

