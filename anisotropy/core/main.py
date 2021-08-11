import os, sys
import time
from datetime import timedelta, datetime
import shutil
import logging

import toml
from copy import deepcopy

from anisotropy.core.models import db, Structure, Mesh, SubMesh, MeshResult
from anisotropy.core.utils import struct, deepupdate


###
#   Environment variables and config
##
env = { "ROOT": os.path.abspath(".") }
env.update(
    BUILD = os.path.join(env["ROOT"], "build"),
    LOG = os.path.join(env["ROOT"], "logs"),
    DEFAULT_CONFIG = os.path.join(env["ROOT"], "anisotropy/config/default.toml"),
    CONFIG = os.path.join(env["ROOT"], "conf/config.toml")
)
env["db_path"] = env["BUILD"]
env["salome_port"] = 2810

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
from anisotropy.core.utils import setupLogger
logger_env = env.get("logger", {})

logger = logging.getLogger(logger_env.get("name", "anisotropy"))
setupLogger(logger, logging.INFO)

peeweeLogger = logging.getLogger("peewee")
peeweeLogger.setLevel(logging.INFO)

from anisotropy.core.utils import timer
from anisotropy import __version__
from anisotropy import salomepl
from anisotropy import openfoam
from anisotropy.samples import Simple, FaceCentered, BodyCentered
from math import sqrt
from peewee import JOIN

class Anisotropy(object):
    """Ultimate class that organize whole working process"""

    def __init__(self):
        """Constructor method"""

        self.env = env
        self.db = None
        self.params = []


    @staticmethod
    def version():
        """Returns versions of all used main programs

        :return: Versions joined by next line symbol
        :rtype: str
        """
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

    
    def loadFromScratch(self) -> list:
        """Loads parameters from configuration file and expands special values

        :return: List of dicts with parameters
        :rtype: list
        """

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
                    mesh = deepcopy(entry["mesh"])
                    mesh["thickness"] = thicknessList[n]

                    entryNew = {
                        "structure": dict(
                            type = entry["structure"]["type"],
                            theta = theta,
                            direction = [ float(num) for num in direction ],
                            filletsEnabled = entry["structure"]["filletsEnabled"]
                        ),
                        "mesh": mesh,
                        "submesh": deepcopy(entry["submesh"])
                    }
                    
                    paramsAll.append(entryNew)

        return paramsAll

    
    def evalParams(self):
        """Evals specific geometry(structure) parameters"""

        structure = self.params.get("structure")

        if not structure:
            logger.error("Trying to eval empty parameters")
            return
        
        if structure["type"] == "simple":
            thetaMin = 0.01
            thetaMax = 0.28

            r0 = 1
            L = 2 * r0
            radius = r0 / (1 - structure["theta"])

            C1, C2 = 0.8, 0.5
            Cf = C1 + (C2 - C1) / (thetaMax - thetaMin) * (structure["theta"] - thetaMin)
            delta = 0.2
            fillets = delta - Cf * (radius - r0)

        elif structure["type"] == "faceCentered":
            thetaMin = 0.01
            thetaMax = 0.13

            L = 1.0
            r0 = L * sqrt(2) / 4
            radius = r0 / (1 - structure["theta"])

            C1, C2 = 0.3, 0.2
            Cf = C1 + (C2 - C1) / (thetaMax - thetaMin) * (structure["theta"] - thetaMin)
            delta = 0.012
            fillets = delta - Cf * (radius - r0)

        elif structure["type"] == "bodyCentered":
            thetaMin = 0.01
            thetaMax = 0.18
    
            L = 1.0
            r0 = L * sqrt(3) / 4
            radius = r0 / (1 - structure["theta"])

            C1, C2 = 0.3, 0.2
            Cf = C1 + (C2 - C1) / (thetaMax - thetaMin) * (structure["theta"] - thetaMin)
            delta = 0.02
            fillets = delta - Cf * (radius - r0)

        self.params["structure"].update(
            #**structure,
            L = L,
            r0 = r0,
            radius = radius,
            fillets = fillets 
        )

    def getCasePath(self) -> str:
        """Constructs case path from main control parameters
        
        :return: Absolute path to case
        :rtype: str
        """
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

        dbname = os.path.join(self.env["db_path"], "anisotropy.db")
        self.db = db
        self.db.init(dbname)

        if not os.path.exists(dbname):
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
                        Mesh.structure_id == structureID #req["structure_id"]
                    )
                )
                query.execute()

        return tabID

    def _updateSubMesh(self, src: dict, queryMain, meshID) -> None:
        if not src:
            return

        raw = deepcopy(src)
        
        with self.db.atomic():
            if not SubMesh.select().where(SubMesh.mesh_id == meshID).exists():
                tabID = SubMesh.create(
                    mesh_id = meshID,
                    **raw
                )
                logger.debug(f"[ DB ] Created SubMesh entry { tabID }")

            else:
                #req = queryMain.dicts().get()
                #tabID = req["mesh_id"]

                query = (
                    SubMesh.update(**raw)
                    .where(
                        SubMesh.mesh_id == meshID, #req["mesh_id"],
                        SubMesh.name == src["name"]
                    )
                )
                query.execute()

    def _updateMeshResult(self, src: dict, queryMain, meshID) -> None:
        if not src:
            return

        raw = deepcopy(src)

        with self.db.atomic():
            if not MeshResult.select().where(MeshResult.mesh_id == meshID).exists():
                tabID = MeshResult.create(
                    mesh_id = meshID,
                    **raw
                )
                logger.debug(f"[ DB ] Created MeshResult entry { tabID }")

            else:
                #req = queryMain.dicts().get()
                #tabID = req["mesh_id"]

                query = (
                    MeshResult.update(**raw)
                    .where(
                        MeshResult.mesh_id == meshID #req["mesh_id"]
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
        
        structureID = self._updateStructure(params["structure"], query)
        
        meshID = self._updateMesh(params["mesh"], query, structureID)

        for submeshParams in params.get("submesh", []):
            self._updateSubMesh(submeshParams, query, meshID)

        self._updateMeshResult(params.get("meshresults", {}), query, meshID)


    def loadDB(self, structure_type: str, structure_direction: list, structure_theta: float):
        structureQuery = (
            Structure
            .select()
            .where(
                Structure.type == structure_type,
                Structure.direction == str(structure_direction),
                Structure.theta == structure_theta
            )
        )
        
        self.params = {}

        with self.db.atomic():
            if structureQuery.exists():
                self.params["structure"] = structureQuery.dicts().get()

                meshQuery = structureQuery.get().meshes

                if meshQuery.exists():
                    self.params["mesh"] = meshQuery.dicts().get()

                    submeshQuery = meshQuery.get().submeshes
                    
                    if submeshQuery.exists():
                        self.params["submesh"] = [ entry for entry in submeshQuery.dicts() ]

                    meshresultQuery = meshQuery.get().meshresults

                    if meshresultQuery.exists():
                        self.params["meshresult"] = meshresultQuery.dicts().get()

    

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
    def computeMesh(self, type, direction, theta):
        scriptpath = os.path.join(self.env["ROOT"], "anisotropy/__main__.py")
        port = 2900

        return salomepl.utils.runSalome(port, scriptpath, self.env["ROOT"], "_compute_mesh", type, direction, theta)

    def genmesh(self):
        import salome 

        p = self.params

        logger.info("\n".join([
            "genmesh:",
            f"structure type:\t{ p['structure']['type'] }",
            f"coefficient:\t{ p['structure']['theta'] }",
            f"fillet:\t{ p['structure']['fillets'] }",
            f"flow direction:\t{ p['structure']['direction'] }"
        ]))

        salome.salome_init()


        ###
        #   Shape
        ##
        geompy = salomepl.geometry.getGeom()
        structure = dict(
            simple = Simple,
            bodyCentered = BodyCentered,
            faceCentered = FaceCentered
        )[p["structure"]["type"]]
        shape, groups = structure(**p["structure"]).build()

        [length, surfaceArea, volume] = geompy.BasicProperties(shape, theTolerance = 1e-06)

        logger.info("\n".join([
            "shape:",
            f"edges length:\t{ length }",
            f"surface area:\t{ surfaceArea }",
            f"volume:\t{ volume }"
        ]))


        ###
        #   Mesh
        ##
        mp = p["mesh"]

        lengths = [
            geompy.BasicProperties(edge)[0] for edge in geompy.SubShapeAll(shape, geompy.ShapeType["EDGE"]) 
        ]
        meanSize = sum(lengths) / len(lengths)
        mp["maxSize"] = meanSize
        mp["minSize"] = meanSize * 1e-1
        mp["chordalError"] = mp["maxSize"] / 2

        faces = []
        for group in groups:
            if group.GetName() in mp["facesToIgnore"]:
                faces.append(group)


        mesh = salomepl.mesh.Mesh(shape)
        mesh.Tetrahedron(**mp)

        if mp["viscousLayers"]:
            mesh.ViscousLayers(**mp, faces = faces)

        smp = p["submesh"]

        for submesh in smp:
            for group in groups:
                if submesh["name"] == group.GetName():
                    subshape = group

                    submesh["maxSize"] = meanSize * 1e-1
                    submesh["minSize"] = meanSize * 1e-3
                    submesh["chordalError"] = submesh["minSize"] * 1e+1

                    mesh.Triangle(subshape, **submesh)


        model.updateDB()
        returncode, errors = mesh.compute()

        if not returncode:
            mesh.removePyramids()
            mesh.assignGroups()

            casePath = model.getCasePath()
            os.makedirs(casePath, exist_ok = True)
            mesh.exportUNV(os.path.join(casePath, "mesh.unv"))

            meshStats = mesh.stats()
            p["meshresults"] = dict(
                surfaceArea = surfaceArea,
                volume = volume,
                **meshStats
            )
            model.updateDB()

            logger.info("mesh stats:\n{}".format(
                "\n".join(map(lambda v: f"{ v[0] }:\t{ v[1] }", meshStats.items()))
            ))

        else:
            logger.error(errors)

            p["meshresults"] = dict(
                surfaceArea = surfaceArea,
                volume = volume
            )
            model.updateDB()

        salome.salome_close()

    @timer
    def computeFlow(self, type, direction, theta):
        ###
        #   Case preparation
        ##
        foamCase = [ "0", "constant", "system" ]

        # ISSUE: ideasUnvToFoam cannot import mesh with '-case' flag so 'os.chdir' for that
        os.chdir(self.getCasePath())
        openfoam.foamClean()

        for d in foamCase:
            shutil.copytree(
                os.path.join(ROOT, "anisotropy/openfoam/template", d), 
                os.path.join(case, d)
            )
        
        ###
        #   Mesh manipulations
        ##
        if not os.path.exists("mesh.unv"):
            logger.error(f"missed 'mesh.unv'")
            os.chdir(self.env["ROOT"])
            return 1

        _, returncode = openfoam.ideasUnvToFoam("mesh.unv")

        if returncode:
            os.chdir(self.env["ROOT"])
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
        # TODO: replace all task variables
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

