import os, sys
import time
from datetime import timedelta, datetime
import shutil

#ROOT = "/".join(__file__.split("/")[:-2])
#sys.path.append(os.path.abspath(ROOT))

#from anisotropy.utils import struct
import toml
import logging

__version__ = "1.1"
###
#   Shell args
##
#configPath = "conf/config.toml"
#mode = "safe"

#for n, arg in enumerate(sys.argv):
#    if arg == "-c" or arg == "--config":
#        configPath = sys.args[n + 1]

#    if arg == "-s" or arg == "--safe":
#        mode = "safe"

#    elif arg == "-a" or arg == "--all":
#        mode = "all"

###
#   Load configuration and tools
##
#CONFIG = os.path.join(ROOT, configPath)
#config = struct(toml.load(CONFIG))

#LOG = os.path.join(ROOT, "logs")
#if not os.path.exists(LOG):
#    os.makedirs(LOG)

#BUILD = os.path.join(ROOT, "build")
#if not os.path.exists(BUILD):
#    os.makedirs(BUILD)

##################################################################################
import os
import toml
from copy import deepcopy
from anisotropy.models import db, Structure, Mesh
from anisotropy.utils import struct, deepupdate
import salomepl

###
#   Environment variables and config
##
env = { "ROOT": os.path.abspath(".") }
env.update({
    "BUILD": os.path.join(env["ROOT"], "build"),
    "LOG": os.path.join(env["ROOT"], "logs"),
    "CONFIG": os.path.join(env["ROOT"], "conf/config.toml")
})
env["db_path"] = os.path.join(env["BUILD"], "anisotropy.db")

_defaultConfig = os.path.join(env["ROOT"], "anisotropy/default.toml")

if os.path.exists(_defaultConfig):
    env.update(toml.load(_defaultConfig))

if os.path.exists(env["CONFIG"]):
    config = toml.load(env["CONFIG"])

    for restricted in ["ROOT", "BUILD", "LOG", "CONFIG"]:
        if config.get(restricted):
            config.pop(restricted)
    
    for m, structure in enumerate(config["structures"]):
        for n, estructure in enumerate(env["structures"]):
            if estructure["name"] == structure["name"]:
                deepupdate(env["structures"][n], config["structures"][m])

    config.pop("structures")
    deepupdate(env, config)

###
#   Logger
##
logger_env = env.get("logger", {})
logging.basicConfig(
    level = logging.INFO,
    format = logger_env.get("format", "%(levelname)s: %(message)s"),
    handlers = [
        logging.StreamHandler(),
        logging.FileHandler(
            os.path.join(env["LOG"], logger_env.get("name", "anisotropy"))
        )
    ]
)
logger = logging.getLogger(logger_env.get("name", "anisotropy"))


def timer(func):
    def inner(*args, **kwargs):
        start = time.monotonic()
        ret = func(*args, **kwargs)
        elapsed = time.monotonic() - start

        return ret, elapsed

    return inner


class Anisotropy(object):
    def __init__(self):
        self.db = self._setupDB()
        self.params = []

        self.evalParameters(env)

    @staticmethod
    def version():
        versions = {
            "anisotropy": __version__,
            "Python": sys.version.split(" ")[0],
            "Salome": "[missed]",
            "OpenFOAM": "[missed]"
        }

        try:
            salomeplVersion = salomepl.version()
            openfoamVersion = openfoam.foamVersion()

        except Exception:
            pass

        return "\n".join([ f"{ k }: { v }" for k, v in versions.items() ])

    @staticmethod
    def _setupDB():
        db.init(env["db_path"])

        if not os.path.exists(env["db_path"]):
            db.create_tables([Structure, Mesh])

        return db

    def evalParameters(self, _env: dict):
        from math import sqrt

        structures = deepcopy(_env["structures"])

        for structure in structures:
            _theta = structure["geometry"]["theta"]
            thetaMin = int(_theta[0] / _theta[2]) 
            thetaMax = int(_theta[1] / _theta[2]) + 1
            thetaList = list(
                map(lambda n: n * _theta[2], range(thetaMin, thetaMax))
            )

            _thickness = structure["mesh"]["thickness"]
            count = len(thetaList)
            thicknessList = list(
                map(lambda n: _thickness[0] + n * (_thickness[1] - _thickness[0]) / (count - 1), range(0, count))
            )

            for direction in structure["geometry"]["directions"]:
                for n, theta in enumerate(thetaList):
                    if structure["name"] == "simple":
                        r0 = 1
                        L = 2 * r0
                        radius = r0 / (1 - theta)

                        C1, C2 = 0.8, 0.5 
                        Cf = C1 + (C2 - C1) / (thetaMax - thetaMin) * (theta - thetaMin)
                        delta = 0.2
                        fillets = delta - Cf * (radius - r0)

                    elif structure["name"] == "faceCentered":
                        L = 1.0
                        r0 = L * sqrt(2) / 4
                        radius = r0 / (1 - theta)

                        C1, C2 = 0.3, 0.2
                        Cf = C1 + (C2 - C1) / (thetaMax - thetaMin) * (theta - thetaMin)
                        delta = 0.012
                        fillets = delta - Cf * (radius - r0)

                    elif structure["name"] == "bodyCentered":
                        L = 1.0
                        r0 = L * sqrt(3) / 4
                        radius = r0 / (1 - theta)

                        C1, C2 = 0.3, 0.2 
                        Cf = C1 + (C2 - C1) / (thetaMax - thetaMin) * (theta - thetaMin)
                        delta = 0.02
                        fillets = delta - Cf * (radius - r0)

                    
                    path = os.path.join(
                        _env["BUILD"],
                        structure["name"],
                        f"direction-{ direction }",
                        f"theta-{ theta }"
                    )
                    geometry = dict(
                        theta = theta,
                        direction = direction,
                        r0 = r0,
                        L = L,
                        radius = radius,
                        filletsEnabled = structure["geometry"]["filletsEnabled"],
                        fillets = fillets

                    )
                    mesh = deepcopy(structure["mesh"])
                    mesh.update(
                        thickness = thicknessList[n]
                    )
                    self.params.append({
                        "name": structure["name"],
                        "path": path,
                        "geometry": geometry,
                        "mesh": mesh,
                        "submesh": deepcopy(structure["submesh"])
                    })


    # SELECT * FROM structure LEFT OUTER JOIN mesh ON mesh.structure_id = structure.id WHERE name = "faceCentered" AND direction = "[1, 1, 1]" AND theta = 0.12;
    def updateDB(self):
        for entry in self.params:
            query = (Structure
                .select()
                .where(
                    Structure.name == entry["name"],
                    Structure.direction == str(entry["geometry"]["direction"]),
                    Structure.theta == entry["geometry"]["theta"]
                )
            )

            s = deepcopy(entry["geometry"])
            s.update(
                name = entry["name"],
                path = entry["path"]
            )

            m = deepcopy(entry["mesh"])
            
            if not query.exists():
                with self.db.atomic():
                    stab = Structure.create(**s)

                    m.update(structure_id = stab)
                    mtab = Mesh.create(**m)

            else:
                # TODO: not working update; incorrect update (all entries)
                with self.db.atomic():
                    stab = Structure.update(**s)

                    m.update(structure_id = stab)
                    mtab = Mesh.update(**m)

    @timer
    def computeMesh(self):
        scriptpath = os.path.join(env["ROOT"], "salomepl/genmesh.py")
        port = 2900

        out, err, returncode = salomepl.runSalome(port, scriptpath, env["ROOT"], case)

    def computeFlow(self):
        pass
    
    def _queue(self):
        pass

    def computeAll(self):
        pass


###################################################################################


###
#   Main
##
def main():
    if checkEnv():
        return

    logger.info(f"args:\n\tconfig:\t{ configPath }\n\tmode:\t{ mode }")

    queue = createQueue()

    for n, case in enumerate(queue):
        date = datetime.now()
        logger.info("-" * 80)
        logger.info(f"""main:
        task:\t{ n + 1 } / { len(queue) }
        cpu count:\t{ os.cpu_count() }
        case:\t{ case }
        date:\t{ date.date() }
        time:\t{ date.time() }""")
        
        ###
        #   Compute mesh
        ##
        taskPath = os.path.join(case, "task.toml")

        task = struct(toml.load(taskPath))
            
        if not task.status.mesh or mode == "all":
            computeMesh(case)

        else:
            logger.info("computeMesh: mesh already computed")
        
        task = struct(toml.load(taskPath))
        
        if not task.status.mesh:
            logger.critical("mesh not computed: skip flow computation")
            continue

        ###
        #   Compute flow
        ##

        if not task.status.flow or mode == "all":
            computeFlow(case)

        else:
            logger.info("computeFlow: flow already computed")
    

def createQueue():
    queue = []

    ###
    #   Special values
    ##
    parameters_theta = {}
    mesh_thickness = {}

    for structure in config.base.__dict__.keys():
        
        theta = getattr(config, structure).geometry.theta
        parameters_theta[structure] = [ n * theta[2] for n in range(int(theta[0] / theta[2]), int(theta[1] / theta[2]) + 1) ]

        thickness = getattr(config, structure).mesh.thickness
        count = len(parameters_theta[structure])
        mesh_thickness[structure] = [ thickness[0] + n * (thickness[1] - thickness[0]) / (count - 1) for n in range(0, count) ]


    ###
    #   structure type > flow direction > coefficient theta
    ##
    for structure in config.base.__dict__.keys():
        if getattr(config.base, structure):
            for direction in getattr(config, structure).geometry.directions:
                for n, theta in enumerate(parameters_theta[structure]):
                    # create dirs for case path
                    case = os.path.join(
                        f"{ BUILD }",
                        f"{ structure }",
                        "direction-{}{}{}".format(*direction), 
                        f"theta-{ theta }"
                    )

                    taskPath = os.path.join(case, "task.toml")
                    
                    if os.path.exists(taskPath) and mode == "safe":
                        queue.append(case)
                        continue
                    
                    if not os.path.exists(case):
                        os.makedirs(case)

                    # prepare configuration for task
                    task = {
                        "logger": dict(config.logger),
                        "structure": structure,
                        "status": {
                            "mesh": False,
                            "flow": False
                        },
                        "statistics": {
                            "meshTime": 0,
                            "flowTime": 0
                        },
                        "geometry": {
                            "theta": theta,
                            "direction": direction,
                            "fillet": getattr(config, structure).geometry.fillet
                        },
                        "mesh": dict(getattr(config, structure).mesh),
                        "flow": dict(config.flow)
                    }
                    
                    # reassign special values
                    task["mesh"]["thickness"] = mesh_thickness[structure][n]
       
                    ##
                    with open(os.path.join(case, "task.toml"), "w") as io:
                        toml.dump(task, io)

                    ##
                    queue.append(case)

    return queue


#from salomepl.utils import runExecute, salomeVersion

def computeMesh(case):
    scriptpath = os.path.join(ROOT, "salomepl/genmesh.py")
    port = 2810
    stime = time.monotonic()

    returncode = runExecute(port, scriptpath, ROOT, case)
    
    task = struct(toml.load(os.path.join(case, "task.toml")))
    elapsed = time.monotonic() - stime
    logger.info("computeMesh: elapsed time: {}".format(timedelta(seconds = elapsed)))

    if returncode == 0:
        task.statistics.meshTime = elapsed

        with open(os.path.join(case, "task.toml"), "w") as io:
            toml.dump(dict(task), io)



import openfoam

def computeFlow(case):
    ###
    #   Case preparation
    ##
    foamCase = [ "0", "constant", "system" ]

    os.chdir(case)
    task = struct(toml.load(os.path.join(case, "task.toml")))
    openfoam.foamClean()

    for d in foamCase:
        shutil.copytree(
            os.path.join(ROOT, "openfoam/template", d), 
            os.path.join(case, d)
        )
    
    stime = time.monotonic()

    ###
    #   Mesh manipulations
    ##
    if not os.path.exists("mesh.unv"):
        logger.critical(f"computeFlow: missed 'mesh.unv'")
        return

    _, returncode = openfoam.ideasUnvToFoam("mesh.unv")

    if returncode:
        os.chdir(ROOT)

        return returncode
    
    openfoam.createPatch(dictfile = "system/createPatchDict")

    openfoam.foamDictionary(
        "constant/polyMesh/boundary", 
        "entry0.defaultFaces.type", 
        "wall"
    )
    openfoam.foamDictionary(
        "constant/polyMesh/boundary", 
        "entry0.defaultFaces.inGroups", 
        "1 (wall)"
    )
    
    out = openfoam.checkMesh()
    
    if out:
        logger.info(out)

    openfoam.transformPoints(task.flow.scale)
    
    ###
    #   Decomposition and initial approximation
    ##
    openfoam.foamDictionary(
        "constant/transportProperties",
        "nu",
        str(task.flow.constant.nu)
    )

    openfoam.decomposePar()

    openfoam.renumberMesh()

    pressureBF = task.flow.approx.pressure.boundaryField
    velocityBF = task.flow.approx.velocity.boundaryField
    direction = {
        "[1, 0, 0]": 0,
        "[0, 0, 1]": 1,
        "[1, 1, 1]": 2
    }[str(task.geometry.direction)]

    openfoam.foamDictionary(
        "0/p", 
        "boundaryField.inlet.value", 
        openfoam.uniform(pressureBF.inlet.value)
    )
    openfoam.foamDictionary(
        "0/p", 
        "boundaryField.outlet.value", 
        openfoam.uniform(pressureBF.outlet.value)
    )

    openfoam.foamDictionary(
        "0/U", 
        "boundaryField.inlet.value", 
        openfoam.uniform(velocityBF.inlet.value[direction])
    )
    
    openfoam.potentialFoam()
    
    ###
    #   Main computation
    ##
    pressureBF = task.flow.main.pressure.boundaryField
    velocityBF = task.flow.main.velocity.boundaryField

    for n in range(os.cpu_count()):
        openfoam.foamDictionary(
            f"processor{n}/0/U", 
            "boundaryField.inlet.type", 
            velocityBF.inlet.type
        )
        openfoam.foamDictionary(
            f"processor{n}/0/U", 
            "boundaryField.inlet.value", 
            openfoam.uniform(velocityBF.inlet.value[direction])
        )
    
    returncode, out = openfoam.simpleFoam()
    if out:
        logger.info(out)

    ###
    #   Check results
    ##
    elapsed = time.monotonic() - stime
    logger.info("computeFlow: elapsed time: {}".format(timedelta(seconds = elapsed)))

    if returncode == 0:
        task.status.flow = True
        task.statistics.flowTime = elapsed

        postProcessing = "postProcessing/flowRatePatch(name=outlet)/0/surfaceFieldValue.dat"

        with open(postProcessing, "r") as io:
            lastLine = io.readlines()[-1]
            flowRate = float(lastLine.replace(" ", "").replace("\n", "").split("\t")[1])
            
            task.statistics.flowRate = flowRate

        with open(os.path.join(case, "task.toml"), "w") as io:
            toml.dump(dict(task), io)

    os.chdir(ROOT)
    
    return returncode


def checkEnv():
    missed = False
    
    try:
        pythonVersion = "Python {}".format(sys.version.split(" ")[0])
        salomeplVersion = salomeVersion()
        openfoamVersion = openfoam.foamVersion()

    except Exception as e:
        logger.critical("Missed environment %s", e)
        missed = True

    else:
        logger.info(f"environment:\n\t{pythonVersion}\n\t{salomeplVersion}\n\t{openfoamVersion}")

    finally:
        return missed


def postprocessing(queue):

    pass

###
#   Main entry
##
if __name__ == "__main__":
    main()

