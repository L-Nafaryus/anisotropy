# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import click
import ast
import os, shutil
import logging

class LiteralOption(click.Option):
    def type_cast_value(self, ctx, value):
        try:
            return ast.literal_eval(value)

        except:
            raise click.BadParameter(f"{ value } (Type error)")

class KeyValueOption(click.Option):
    def _convert(self, ctx, value):
        if not value:
            return {}

        if value.find("=") == -1:
            raise click.BadParameter(f"{ value } (Missed '=')")

        params = value.split("=")

        if not len(params) == 2:
            raise click.BadParameter(f"{ value } (Syntax error)")

        key, val = params[0].strip(), params[1].strip()

        if val[0].isalpha():
            val = f"'{ val }'"

        try:
            return { key: ast.literal_eval(val) }

        except:
            raise click.BadParameter(f"{ value } (Type error)")

    def type_cast_value(self, ctx, value):
        if isinstance(value, list):
            return [ self._convert(ctx, val) for val in value ]

        else:
            return self._convert(ctx, value)

        
def version():
    msg = "Missed package anisotropy"

    try:
        from anisotropy.core.main import Anisotropy
        msg = Anisotropy.version()

    except ImportError:
        pass

    return msg

@click.group()
@click.version_option(version = "", message = version())
def anisotropy():
    pass

@anisotropy.command(
    help = "Initialize project in cwd"
)
def init():
    from anisotropy import env
    from anisotropy.core.utils import setupLogger
    from anisotropy.core.main import logger, Database

    setupLogger(logger, logging.INFO)
    
    cwd = os.getcwd()
    wds = [ "build", "logs" ]

    for wd in wds:
        os.makedirs(os.path.join(cwd, wd), exist_ok = True)

    shutil.copy(env["CONFIG"], os.path.join(cwd, "anisotropy.toml"), follow_symlinks = True)
    
    db = Database(env["db_name"], cwd)
    db.setup()

    logger.info(f"Initialized anisotropy project in { cwd }")

@anisotropy.command(
    help = """Computes cases by chain (mesh -> flow)
    
    Control parameters: type, direction, theta (each parameter affects on a queue)
    """
)
@click.option(
    "-s", "--stage", "stage", 
    type = click.Choice(["all", "mesh", "flow"]), 
    default = "all",
    help = "Current computation stage"
)
@click.option(
    "-N", "--nprocs", "nprocs",
    type = click.INT,
    default = 1,
    help = "Count of parallel processes"
)
@click.option(
    "-f", "--force", "force",
    is_flag = True,
    default = False,
    help = "Overwrite existing entries"
)
@click.option(
    "-u", "--update", "update",
    is_flag = True,
    default = False,
    help = "Update db parameters from config"
)
@click.option(
    "-p", "--param", "params", 
    metavar = "key=value", 
    multiple = True, 
    cls = KeyValueOption,
    help = "Overwrite existing parameter (except control variables)"
)
@click.option(
    "-P", "--path", "path",
    default = os.getcwd(),
    help = "Specify directory to use (instead of cwd)"
)
def compute(stage, nprocs, force, update, params, path):
    from anisotropy import env
    from anisotropy.core.main import Anisotropy, Database, logger
    from anisotropy.core.utils import setupLogger, timer, parallel

    env.update(
        LOG = os.path.join(path, "logs"),
        BUILD = os.path.join(path, "build"),
        CONFIG = os.path.join(path, "anisotropy.toml"),
        db_path = path
    )

    setupLogger(logger, logging.INFO, env["LOG"])
    args = dict()

    for param in params:
        args.update(param)

    ###
    model = Anisotropy()
    model.db = Database(env["db_name"], env["db_path"]) 
        
    logger.info("Configuring database ...")
    model.db.setup()

    if model.db.isempty() or update:
        paramsAll = model.loadFromScratch(env["CONFIG"])

        if args.get("type"):
            paramsAll = [ entry for entry in paramsAll if args["type"] == entry["structure"]["type"] ]

        if args.get("direction"):
            paramsAll = [ entry for entry in paramsAll if args["direction"] == entry["structure"]["direction"] ]

        if args.get("theta"):
            paramsAll = [ entry for entry in paramsAll if args["theta"] == entry["structure"]["theta"] ]

        for entry in paramsAll:
            model.db.update(entry)

        logger.info("{} entries was updated.".format(len(paramsAll)))

    else:
        logger.info("Database was not modified.")


    ###
    def computeCase(stage, type, direction, theta):
        case = Anisotropy()
        case.load(type, direction, theta)
        case.evalParams()
        case.update()

        logger.info(f"Case: type = { type }, direction = { direction }, theta = { theta }")
        logger.info(f"Stage: { stage }")

        if stage == "all" or stage == "mesh":
            if not case.params.get("meshresult", {}).get("status") == "Done" or force:
                (out, err, returncode), elapsed = timer(case.computeMesh)(path)

                if out: logger.info(out)
                if err: logger.error(err)

                case.load(type, direction, theta)

                if case.params.get("meshresult"):
                    case.params["meshresult"]["calculationTime"] = elapsed
                    case.update()

                if returncode:
                    logger.error("Mesh computation failed. Skipping flow computation ...")
                    return

            else:
                logger.info("Mesh exists. Skipping ...")

        if stage == "all" or stage == "flow":
            if not case.params.get("flowresult", {}).get("status") == "Done" or force:
                (out, err, returncode), elapsed = timer(case.computeFlow)(path)

                if out: logger.info(out)
                if err: logger.error(err)

                case.load(type, direction, theta)

                if case.params.get("flowresult"):
                    case.params["flowresult"]["calculationTime"] = elapsed
                    case.update()
            
                if returncode:
                    logger.error("Flow computation failed.")
                    return

            else:
                logger.info("Flow exists. Skipping ...")


    ###
    params = model.db.loadGeneral(
        args.get("type"), 
        args.get("direction"), 
        args.get("theta")
    )
    queueargs = []
    
    for p in params:
        s = p["structure"]

        queueargs.append((stage, s["type"], s["direction"], s["theta"]))

    if nprocs == 1:
        for pos, qarg in enumerate(queueargs):
            computeCase(*qarg)

    else:
        parallel(nprocs, queueargs, computeCase)


@anisotropy.command(
    help = "! Not a user command"
)
@click.argument("root")
@click.argument("type")
@click.argument("direction")
@click.argument("theta")
@click.argument("path")
def computemesh(root, type, direction, theta, path):
    # ISSUE: can't hide command from help, 'hidden = True' doesn't work
    # [Salome Environment]
    
    ###
    #   Args
    ##
    direction = [ float(num) for num in direction[1:-1].split(" ") if num ]
    theta = float(theta)

    ###
    #   Modules
    ##
    import os, sys

    sys.path.extend([
        root,
        os.path.join(root, "env/lib/python3.9/site-packages")
    ])

    from anisotropy import env
    from anisotropy.core.main import Anisotropy, Database
    import salome 

    ###
    model = Anisotropy()
    model.db = Database(env["db_name"], path)
    model.load(type, direction, theta)

    salome.salome_init()
    model.genmesh(path)
    salome.salome_close()


@anisotropy.command(
    help = "Post processing"
)
@click.option(
    "-P", "--path", "path",
    default = os.getcwd(),
    help = "Specify directory to use (instead of cwd)"
)
@click.argument(
    "plot",
    type = click.Choice(["permeability"])
)
def postprocessing(path, plot):
    from anisotropy import env
    from anisotropy.core.main import Database
    from pandas import Series
    import matplotlib.pyplot as plt

    env.update(
        LOG = os.path.join(path, "logs"),
        BUILD = os.path.join(path, "build"),
        CONFIG = os.path.join(path, "anisotropy.toml"),
        db_path = path
    )

    ###
    db = Database(env["db_name"], env["db_path"]) 
    db.setup()

    params = db.loadGeneral()
    paramsAll = []

    for p in params:
        s = p["structure"]
        paramsAll.append(db.load(s["type"], s["direction"], s["theta"]))

    paramsAll.sort(key = lambda src: f"{ src['structure']['type'] }{ src['structure']['direction'] }{ src['structure']['theta'] }")

    def getTD(src, type, direction):
        return src["structure"]["type"] == type and src["structure"]["direction"] == direction

    if plot == "permeability":
        for structure in ["simple", "faceCentered", "bodyCentered"]:
            d1 = [ entry for entry in paramsAll if getTD(entry, structure, [1.0, 0.0, 0.0]) ]
            d2 = [ entry for entry in paramsAll if getTD(entry, structure, [0.0, 0.0, 1.0]) ]
            d3 = [ entry for entry in paramsAll if getTD(entry, structure, [1.0, 1.0, 1.0]) ]

            theta = [ entry["structure"]["theta"] for entry in d1 ]
            fr1 = Series([ entry.get("flowresult", {}).get("flowRate", None) for entry in d1 ], theta)
            fr2 = Series([ entry.get("flowresult", {}).get("flowRate", None) for entry in d2 ], theta)
            fr3 = Series([ entry.get("flowresult", {}).get("flowRate", None) for entry in d3 ], theta)

            pm2 = 2 * fr2 / fr1
            pm3 = 2 * fr3 / fr1

            plt.figure(1)

            ax1 = pm2.plot(style = "o")
            ax1.set_label("k_2 / k_1")
            ax2 = pm3.plot(style = "o")
            ax2.set_label("k_3 / k_1")

            plt.title(structure)
            plt.xlabel("theta")
            plt.ylabel("permeability")
            plt.legend()
            plt.grid()
            plt.show()



###
#   CLI entry
##
if __name__ == "__main__":
    anisotropy()
