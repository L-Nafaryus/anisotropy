import os, sys
import time
from datetime import timedelta, datetime
import shutil
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
from anisotropy.models import db, JOIN, Structure, Mesh, SubMesh, MeshResult
from anisotropy.utils import struct, deepupdate
import salomepl
import openfoam
from math import sqrt

###
#   Environment variables and config
##
env = { "ROOT": os.path.abspath(".") }
env.update(dict(
    BUILD = os.path.join(env["ROOT"], "build"),
    LOG = os.path.join(env["ROOT"], "logs"),
    DEFAULT_CONFIG = os.path.join(env["ROOT"], "anisotropy/default.toml"),
    CONFIG = os.path.join(env["ROOT"], "conf/config.toml")
))
env["db_path"] = env["BUILD"]


#if os.path.exists(env["CONFIG"]):
#    config = toml.load(env["CONFIG"])

#    for restricted in ["ROOT", "BUILD", "LOG", "CONFIG"]:
#        if config.get(restricted):
#            config.pop(restricted)

    # TODO: not working if custom config empty and etc
#    for m, structure in enumerate(config["structures"]):
#        for n, estructure in enumerate(env["structures"]):
#            if estructure["name"] == structure["name"]:
#                deepupdate(env["structures"][n], config["structures"][m])

#    config.pop("structures")
#    deepupdate(env, config)


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
        self.env = env
        self.db = None
        self.params = []


    @staticmethod
    def version():
        versions = {
            "anisotropy": __version__,
            "Python": sys.version.split(" ")[0],
            "Salome": "[missed]",
            "OpenFOAM": "[missed]"
        }

        try:
            versions["Salome"] = salomepl.utils.version()
            versions["OpenFOAM"] = openfoam.version()

        except Exception:
            pass

        return "\n".join([ f"{ k }: { v }" for k, v in versions.items() ])

    
    def loadScratch(self):
        if not os.path.exists(self.env["DEFAULT_CONFIG"]):
            logger.error("Missed default configuration file")
            return

        buf = toml.load(self.env["DEFAULT_CONFIG"]).get("structures")
        paramsAll = []

        # TODO: custom config and merge
        
        for entry in buf:
            #   Shortcuts
            _theta = entry["structure"]["theta"]
            thetaMin = int(_theta[0] / _theta[2])
            thetaMax = int(_theta[1] / _theta[2]) + 1
            thetaList = list(
                map(lambda n: n * _theta[2], range(thetaMin, thetaMax))
            )

            _thickness = entry["mesh"]["thickness"]
            count = len(thetaList)
            thicknessList = list(
                map(lambda n: _thickness[0] + n * (_thickness[1] - _thickness[0]) / (count - 1), range(0, count))
            )

            for direction in entry["structure"]["directions"]:
                for n, theta in enumerate(thetaList):
                    entryNew = {
                        "structure": dict(
                            type = entry["structure"]["type"],
                            theta = theta,
                            direction = [ float(num) for num in direction ],
                        ),
                        "mesh": dict(
                            **deepcopy(entry["mesh"]),
                            thickness = thicknessList[n]
                        ),
                        "submesh": dict(
                            **deepcopy(entry["submesh"])
                        )
                    }
                    
                    paramsAll.append(entryNew)

        self.setupDB()
        
        for entry in paramsAll:
            self.updateDB(entry)

    
    def evalParams(self):
        structure = self.params.get("structure")

        if not structure:
            logger.error("Trying to eval empty parameters")
            return
        
        if structure["type"] == "simple":
            thetaMin = 0.01
            thetaMax = 0.28

            r0 = 1
            L = 2 * r0
            radius = r0 / (1 - theta)

            C1, C2 = 0.8, 0.5
            Cf = C1 + (C2 - C1) / (thetaMax - thetaMin) * (theta - thetaMin)
            delta = 0.2
            fillets = delta - Cf * (radius - r0)

        elif structure["type"] == "faceCentered":
            thetaMin = 0.01
            thetaMax = 0.13

            L = 1.0
            r0 = L * sqrt(2) / 4
            radius = r0 / (1 - theta)

            C1, C2 = 0.3, 0.2
            Cf = C1 + (C2 - C1) / (thetaMax - thetaMin) * (theta - thetaMin)
            delta = 0.012
            fillets = delta - Cf * (radius - r0)

        elif structure["type"] == "bodyCentered":
            thetaMin = 0.01
            thetaMax = 0.18
    
            L = 1.0
            r0 = L * sqrt(3) / 4
            radius = r0 / (1 - theta)

            C1, C2 = 0.3, 0.2
            Cf = C1 + (C2 - C1) / (thetaMax - thetaMin) * (theta - thetaMin)
            delta = 0.02
            fillets = delta - Cf * (radius - r0)

        self.params["structure"] = dict(
            **structure,
            L = L,
            r0 = r0,
            radius = radius,
            fillets = fillets 
        )

    def getCasePath(self):
        structure = self.params.get("structure")

        if not structure:
            logger.error("Trying to use empty parameters")
            return

        return os.path.join(
            self.env["BUILD"], 
            structure["type"],
            f"direction-{ structure['direction'] }",
            f"theta-{ structure['theta'] }"
        )






    def getParams(self, structure: str, direction: list, theta: float):
        for entry in self.params:
            if entry["name"] == structure and \
                entry["geometry"]["direction"] == direction and \
                entry["geometry"]["theta"] == theta:
                return entry


    def setupDB(self):
        os.makedirs(self.env["db_path"], exist_ok = True)

        self.db = db
        self.db.init(os.path.join(self.env["db_path"], "anisotropy.db"))

        if not os.path.exists(self.env["db_path"]):
            self.db.create_tables([
                Structure, 
                Mesh,
                SubMesh,
                MeshResult
            ])


    def _updateStructure(self, src: dict, queryMain) -> int:
        raw = deepcopy(src)

        with self.db.atomic():
            if not queryMain.exists():
                tabID = Structure.create(**raw)

            else:
                req = queryMain.dicts().get()
                tabID = req["structure_id"]

                query = (
                    Structure.update(**raw)
                    .where(
                        Structure.type == req["type"],
                        Structure.direction == str(req["direction"]),
                        Structure.theta == req["theta"]
                    )
                )
                query.execute()

        return tabID

    def _updateMesh(self, src: dict, queryMain, structureID) -> int:
        raw = deepcopy(src)

        with self.db.atomic():
            if not queryMain.exists():
                tabID = Mesh.create(
                    structure_id = structureID,
                    **raw
                )

            else:
                req = queryMain.dicts().get()
                tabID = req["mesh_id"]

                query = (
                    Mesh.update(**raw)
                    .where(
                        Mesh.structure_id == req["structure_id"]
                    )
                )
                query.execute()

        return tabID

    def _updateSubMesh(self, srcs: list, queryMain, meshID) -> None:
        if not srcs:
            return

        for src in srcs:
            raw = deepcopy(src)

            with self.db.atomic():
                if not queryMain.exists():
                    tabID = SubMesh.create(
                        mesh_id = meshID,
                        **raw
                    )

                else:
                    req = queryMain.dicts().get()
                    tabID = req["mesh_id"]

                    query = (
                        SubMesh.update(**raw)
                        .where(
                            SubMesh.mesh_id == req["mesh_id"],
                            SubMesh.name == src["name"]
                        )
                    )
                    query.execute()

    def _updateMeshResult(self, src: dict, queryMain, meshID) -> None:
        if not src:
            return

        raw = deepcopy(src)

        with self.db.atomic():
            if not queryMain.exists():
                tabID = MeshResult.create(
                    mesh_id = meshID,
                    **raw
                )

            else:
                req = queryMain.dicts().get()
                tabID = req["mesh_id"]

                query = (
                    Mesh.update(**raw)
                    .where(
                        Mesh.mesh_id == req["mesh_id"]
                    )
                )
                query.execute()

    @timer
    def updateDB(self, src: dict = None):
        if src:
            params = src

        elif self.params:
            params = self.params

        else:
            logger.error("Trying to update db from empty parameters")
            return

        # TODO: query for every table
        query = (
            Structure
            .select(Structure, Mesh)
            .join(
                Mesh, 
                JOIN.INNER, 
                on = (Mesh.structure_id == Structure.structure_id)
            )
            .where(
                Structure.type == params["structure"]["type"],
                Structure.direction == str(params["structure"]["direction"]),
                Structure.theta == params["structure"]["theta"]
            )
        )
        
        structureID = self._updateStructure(entry["structure"], query)
        
        meshID = self._updateMesh(entry["mesh"], query, structureID)
        self._updateSubMesh(entry.get("submesh", []), query, meshID)
        self._updateMeshResult(entry.get("meshresults", {}), query, meshID)


    def loadDB(self, structure_type: str, structure_direction: list, structure_theta: float):
        query = (
            Structure
            .select(Structure, Mesh)
            .join(
                Mesh, 
                JOIN.INNER, 
                on = (Mesh.structure_id == Structure.structure_id)
            )
            .where(
                Structure.type == structure_type,
                Structure.direction == str(structure_direction),
                Structure.theta == structure_theta
            )
        )

        self.params = query.dicts().get()

    

    # TODO: loadDB (one model), loadsDB (all models)
    @timer
    def updateFromDB(self):
        squery = Structure.select().order_by(Structure.structure_id)
        mquery = Mesh.select().order_by(Mesh.structure_id)
        smquery = SubMesh.select()
        mrquery = MeshResult.select().order_dy(MeshResult.mesh_id)
        self.params = []

        for s, m, mr in zip(squery.dicts(), mquery.dicts(), mrquery.dicts()):
            name = s.pop("name")
            path = s.pop("path")

            self.params.append(dict(
                name = name,
                path = path,
                geometry = s,
                mesh = m,
                submesh = [ d for d in smquery.dicts() if d["mesh_id"] == m["mesh_id"] ],
                meshresults = mr 
            ))

        self.params = sorted(self.params, key = lambda entry: f"{ entry['name'] } { entry['geometry']['direction'] } { entry['geometry']['theta'] }")

    @timer
    def computeMesh(self, name, direction, theta):
        scriptpath = os.path.join(self.env["ROOT"], "anisotropy/genmesh.py")
        port = 2900

        return salomepl.utils.runSalome(port, scriptpath, self.env["ROOT"], name, direction, theta)

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

