# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import click
import ast
import os

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
    "-D", "--database", "database",
    help = "Database path"
)
@click.option(
    "-f", "--force", "force",
    type = click.BOOL,
    default = False,
    help = "Overwrite existing entries"
)
@click.option(
    "-p", "--param", "params", 
    metavar = "key=value", 
    multiple = True, 
    cls = KeyValueOption,
    help = "Overwrite existing parameter (except control variables)"
)
def compute(stage, nprocs, database, force, params):
    from anisotropy.core.main import Anisotropy, Database, logger
    from anisotropy.core.utils import timer, parallel

    args = dict()

    for param in params:
        args.update(param)

    ###
    model = Anisotropy()

    if database:
        if database[-3: ] == ".db":
            splitted = database.split("/")
            db_path = "/".join(splitted[ :-1])
            db_name = splitted[-1: ][0][ :-3]

        else:
            raise Exception("Invalid database extension")

        model.db = Database(db_name, db_path)
        
    logger.info("Constructing database, tables ...")
    model.db.setup()

    def fill_db():
        if model.db.isempty():
            paramsAll = model.loadFromScratch()

            for entry in paramsAll:
                model.db.update(entry)

    _, fill_elapsed = timer(fill_db)()
    logger.info(f"Elapsed time = { fill_elapsed }")

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
                (out, err, returncode), elapsed = timer(case.computeMesh)()

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
                (out, err, returncode), elapsed = timer(case.computeFlow)()

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
def computemesh(root, type, direction, theta):
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

    from anisotropy.core.main import Anisotropy

    ###
    model = Anisotropy()
    model.load(type, direction, theta)

    model.genmesh()

###
#   CLI entry
##
if __name__ == "__main__":
    anisotropy()
