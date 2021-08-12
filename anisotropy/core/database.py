# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import os
import logging
from copy import deepcopy

from anisotropy import env
from anisotropy.core.utils import setupLogger
from anisotropy.core.models import db, JOIN, Structure, Mesh, SubMesh, MeshResult, Flow, FlowResult

logger = logging.getLogger(env["logger_name"])
setupLogger(logger, logging.INFO, env["LOG"])


class Database(object):
    def __init__(self, name: str, filepath: str):
        self.name = name
        self.filepath = filepath
        self.__db = db


    def setup(self):
        os.makedirs(self.filepath, exist_ok = True)

        fullpath = os.path.join(self.filepath, "{}.db".format(self.name))
        self.__db.init(fullpath)

        if not os.path.exists(fullpath):
            self.__db.create_tables([
                Structure, 
                Mesh,
                SubMesh,
                MeshResult,
                Flow,
                FlowResult
            ])


    def isempty(self) -> bool:
        query = Structure.select()

        return not query.exists()


    def load(self, structure_type: str, structure_direction: list, structure_theta: float) -> dict:
        structureQuery = (
            Structure
            .select()
            .where(
                Structure.type == structure_type,
                Structure.direction == str(structure_direction),
                Structure.theta == structure_theta
            )
        )
        
        params = {}

        with self.__db.atomic():
            if structureQuery.exists():
                params["structure"] = structureQuery.dicts().get()

                meshQuery = structureQuery.get().meshes

                if meshQuery.exists():
                    params["mesh"] = meshQuery.dicts().get()

                    submeshQuery = meshQuery.get().submeshes
                    
                    if submeshQuery.exists():
                        params["submesh"] = [ entry for entry in submeshQuery.dicts() ]

                    meshresultQuery = meshQuery.get().meshresults

                    if meshresultQuery.exists():
                        params["meshresult"] = meshresultQuery.dicts().get()

        return params


    def loadGeneral(self) -> list:
        query = (
            Structure
            .select()
            .order_by(Structure.type, Structure.direction, Structure.theta)
        )
        response = []

        for entry in query.dicts():
            response.append({ "structure": entry })

        return response


    def update(self, params: dict):
        if not params:
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

        self._updateMeshResult(params.get("meshresult", {}), query, meshID)

        # TODO: update method flow flow / flowresult

    def _updateStructure(self, src: dict, queryMain) -> int:
        raw = deepcopy(src)

        with self.__db.atomic():
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

        with self.__db.atomic():
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
                        Mesh.structure_id == structureID
                    )
                )
                query.execute()

        return tabID

    def _updateSubMesh(self, src: dict, queryMain, meshID):
        if not src:
            return

        raw = deepcopy(src)
        
        with self.__db.atomic():
            if not SubMesh.select().where(SubMesh.mesh_id == meshID).exists():
                tabID = SubMesh.create(
                    mesh_id = meshID,
                    **raw
                )
                logger.debug(f"[ DB ] Created SubMesh entry { tabID }")

            else:
                query = (
                    SubMesh.update(**raw)
                    .where(
                        SubMesh.mesh_id == meshID,
                        SubMesh.name == src["name"]
                    )
                )
                query.execute()

    def _updateMeshResult(self, src: dict, queryMain, meshID):
        if not src:
            return

        raw = deepcopy(src)

        with self.__db.atomic():
            if not MeshResult.select().where(MeshResult.mesh_id == meshID).exists():
                tabID = MeshResult.create(
                    mesh_id = meshID,
                    **raw
                )
                logger.debug(f"[ DB ] Created MeshResult entry { tabID }")

            else:
                query = (
                    MeshResult.update(**raw)
                    .where(
                        MeshResult.mesh_id == meshID 
                    )
                )
                query.execute()
