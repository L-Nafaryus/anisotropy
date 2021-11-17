# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import click
import ast
import os, sys, shutil
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

class CliListOption(click.Option):
    def _convert(self, ctx, value):
        if not value:
            return []

        output = [ val for val in value.split(",") ]
        
        if "" in output:
            raise click.BadParameter(f"{ value } (Trying to pass empty item)")

        return output


    def type_cast_value(self, ctx, value):
        if isinstance(value, list):
            return [ self._convert(ctx, val) for val in value ]

        else:
            return self._convert(ctx, value)


@click.group()
def anisotropy():
    pass

@anisotropy.command()
@click.option(
    "-P", "--path", "path",
    default = os.getcwd(),
    help = "Specify directory to use (instead of cwd)"
)
@click.option(
    "-C", "--conf", "configFile"
)
@click.option(
    "-N", "--nprocs", "nprocs",
    type = click.INT,
    default = 1,
    help = "Count of parallel processes"
)
@click.option(
    "-s", "--stage", "stage", 
    type = click.Choice(["all", "mesh", "flow", "postProcessing"]), 
    default = "all",
    help = "Current computation stage"
)
@click.option(
    "-f", "--force", "overwrite",
    is_flag = True,
    default = False,
    help = "Overwrite existing entries"
)
@click.option(
    "-p", "--params", "params", 
    metavar = "key=value", 
    multiple = True, 
    cls = KeyValueOption,
    help = "Overwrite existing parameter (except control variables)"
)
def compute(path, configFile, nprocs, stage, overwrite):
    from anisotropy.core.runner import UltimateRunner
    from anisotropy.core.config import DefaultConfig
    from copy import deepcopy

    config = DefaultConfig() 

    if configFile:
        config.load(configFile)

    config.update(
        nprocs = nprocs,
        stage = stage,
        overwrite = overwrite 
    )
    config.expand()

    baseRunner = UltimateRunner(config = config, exec_id = True)
    queue = []

    for case in config.cases:
        caseConfig = deepcopy(config)
        caseConfig.cases = [ case ]

        caseRunner = UltimateRunner(config = caseConfig)
        caseRunner._exec_id = baseRunner._exec_id
        queue.append(caseRunner)

    baseRunner.parallel(queue)

##############

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
    help = "Initialize new anisotropy project."
)
@click.option(
    "-P", "--path", "path",
    default = os.getcwd(),
    help = "Specify directory to use (instead of cwd)"
)
def init(path):
    from anisotropy import env
    from anisotropy.core.main import Database

    if not os.path.exists(path) or not os.path.isdir(path):
        click.echo(f"Cannot find directory { path }")

        return

    wds = [ "build", "logs" ]

    for wd in wds:
        os.makedirs(os.path.join(path, wd), exist_ok = True)

    shutil.copy(env["CONFIG"], os.path.join(path, "anisotropy.toml"), follow_symlinks = True)
    
    db = Database(env["db_name"], path)
    db.setup()

    click.echo(f"Initialized anisotropy project in { path }")


@anisotropy.command(
    help = "Load parameters from configuration file and update database."
)
@click.option(
    "-f", "--force", "force",
    is_flag = True,
    default = False,
    help = "Overwrite existing entries"
)
@click.option(
    "-p", "--params", "params", 
    metavar = "key=value", 
    multiple = True, 
    cls = KeyValueOption,
    help = "Specify control parameters to update (type, direction, theta)"
)
@click.option(
    "-P", "--path", "path",
    default = os.getcwd(),
    help = "Specify directory to use (instead of cwd)"
)
def update(force, params, path):
    from anisotropy import env
    from anisotropy.core.main import Anisotropy, Database

    env.update(
        LOG = os.path.join(path, "logs"),
        BUILD = os.path.join(path, "build"),
        CONFIG = os.path.join(path, "anisotropy.toml"),
        db_path = path
    )

    args = dict()

    for param in params:
        args.update(param)


    model = Anisotropy()
    database = Database(env["db_name"], env["db_path"]) 
        
    click.echo("Configuring database ...")
    database.setup()

    if database.isempty() or update:
        paramsAll = model.loadFromScratch(env["CONFIG"])

        if args.get("type"):
            paramsAll = [ entry for entry in paramsAll if args["type"] == entry["structure"]["type"] ]

        if args.get("direction"):
            paramsAll = [ entry for entry in paramsAll if args["direction"] == entry["structure"]["direction"] ]

        if args.get("theta"):
            paramsAll = [ entry for entry in paramsAll if args["theta"] == entry["structure"]["theta"] ]

        from anisotropy.core.models import Structure, Mesh
        #from numpy 
        for entry in paramsAll:
            database.update(entry)


        click.echo("{} entries was updated.".format(len(paramsAll)))

    else:
        click.echo("Database was not modified.")


@anisotropy.command(
    help = """Compute cases by chain (mesh -> flow)
    
    Control parameters: type, direction, theta (each parameter affects on a queue)
    """
)
@click.option(
    "-s", "--stage", "stage", 
    type = click.Choice(["all", "mesh", "flow", "postProcessing"]), 
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
    "-p", "--params", "params", 
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
def compute(stage, nprocs, force, params, path):
    from anisotropy import env
    from anisotropy.core.main import Anisotropy, Database, logger
    from anisotropy.core.utils import setupLogger, parallel

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
    logger.info("Writing pid ...")
    pidpath = os.path.join(path, "anisotropy.pid")

    with open(pidpath, "w") as io:
        io.write(str(os.getpid()))

    ###
    #   Preparations
    ##
    database = Database(env["db_name"], env["db_path"]) 
        
    logger.info("Loading database ...")
    database.setup()

    params = database.loadGeneral(
        args.get("type"), 
        args.get("direction"), 
        args.get("theta")
    )
    queueargs = []
    
    for p in params:
        s = p["structure"]

        queueargs.append((s["type"], s["direction"], s["theta"]))
    
    ###
    #   Wrap function
    ##
    def computeCase(type, direction, theta):
        case = Anisotropy()
        case.db = database
        case.load(type, direction, theta)
        case.evalParams()
        case.update()

        logger.info(f"Case: type = { type }, direction = { direction }, theta = { theta }")
        logger.info(f"Stage mode: { stage }")

        if stage in ["mesh", "all"]:
            case.load(type, direction, theta)

            if not case.params["meshresult"]["meshStatus"] == "Done" or force:
                logger.info("Current stage: mesh")
                out, err, returncode = case.computeMesh(path)

                if out: logger.info(out)
                if err: logger.error(err)
                if returncode:
                    logger.error("Mesh computation failed. Skipping flow computation ...")

                    return

            else:
                logger.info("Mesh exists. Skipping ...")

        if stage in ["flow", "all"]:
            case.load(type, direction, theta)

            if not case.params["flowresult"]["flowStatus"] == "Done" or force:
                logger.info("Current stage: flow")
                out, err, returncode = case.computeFlow(path)

                if out: logger.info(out)
                if err: logger.error(err)
                if returncode:
                    logger.error("Flow computation failed.")

                    return

            else:
                logger.info("Flow exists. Skipping ...")

        if stage in ["postProcessing", "all"]:
            case.load(type, direction, theta)

            if case.params["meshresult"]["meshStatus"] == "Done":
                logger.info("Current stage: mesh postProcessing")
                case.porosity()

            else:
                logger.warning("Cannot compute mesh post processing values.")
            
            if case.params["flowresult"]["flowStatus"] == "Done":
                logger.info("Current stage: flow postProcessing")
                case.flowRate()

            else:
                logger.warning("Cannot compute flow post processing values.")


    ###
    #   Run
    ##
    if nprocs == 1:
        for pos, qarg in enumerate(queueargs):
            computeCase(*qarg)

    else:
        parallel(nprocs, queueargs, computeCase)

    if os.path.exists(pidpath):
        logger.info("Removing pid ...")
        os.remove(pidpath)

    logger.info("Computation done.")


@anisotropy.command(
    help = "Kill process by pid file"
)
@click.option(
    "-P", "--path", "path",
    default = os.getcwd(),
    help = "Specify directory to use (instead of cwd)"
)
@click.argument("pidfile")
def kill(path, pidfile):
    from anisotropy.salomepl.utils import SalomeManager

    try:
        with open(os.path.join(path, pidfile), "r") as io:
            pid = io.read()

        os.kill(int(pid), 9)

    except FileNotFoundError:
        click.echo(f"Unknown file { pidfile }")

    except ProcessLookupError:
        click.echo(f"Cannot find process with pid { pid }")

    # TODO: killall method kills all salome instances. Not a good way
    SalomeManager().killall()

@anisotropy.command(
    help = "! Internal command"
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
    
    pyversion = "{}.{}".format(3, 9) #(*sys.version_info[:2])
    sys.path.extend([
        root,
        os.path.join(root, "env/lib/python{}/site-packages".format(pyversion)),
        os.path.abspath(".local/lib/python{}/site-packages".format(pyversion))
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



@anisotropy.command()
@click.option(
    "-p", "--params", "params", 
    metavar = "key=value", 
    multiple = True, 
    cls = KeyValueOption,
    help = "Select by control parameters (type, direction, theta)"
)
@click.option(
    "-P", "--path", "path",
    metavar = "PATH",
    default = os.getcwd(),
    help = "Specify directory to use (instead of cwd)"
)
@click.option(
    "--list", "printlist",
    is_flag = True,
    help = "Print a list of avaliable fields."
)
@click.option(
    "--export",
    metavar = "PATH",
    help = "Export output."
)
@click.option(
    "--fields", "fields",
    metavar = "f1,f2,...",
    multiple = True,
    cls = CliListOption,
    help = "Select fields to use."
)
@click.argument(
    "output",
    required = False,
    type = click.Choice(["cli", "plot"]),
    default = "cli"
)
def show(params, path, printlist, export, fields, output):
    from anisotropy import env
    from anisotropy.core.database import Database, Structure
    from pandas import DataFrame, Series
    import matplotlib.pyplot as plt

    env.update(
        LOG = os.path.join(path, "logs"),
        BUILD = os.path.join(path, "build"),
        CONFIG = os.path.join(path, "anisotropy.toml"),
        db_path = path
    )

    args = dict()

    for param in params:
        args.update(param)


    ###
    db = Database(env["db_name"], env["db_path"]) 
    db.setup()

    searchargs = []

    if args.get("type"):
        searchargs.append(Structure.type == args["type"])

    if args.get("direction"):
        searchargs.append(Structure.direction == str(args["direction"]))

    if args.get("theta"):
        searchargs.append(Structure.theta == args["theta"])

    result = db.search(searchargs)
    result.sort(key = lambda src: f"{ src['type'] }{ src['direction'] }{ src['theta'] }")

    df = DataFrame(result)
    df_keys = [ key for key in df.keys() ]
    
    if printlist:
        click.echo("Avaliable fields for query:")
        click.echo("\t{}".format("\n\t".join(df_keys)))

        return

    if not result:
        click.echo("Empty result.")

        return

    tables = []

    if fields:
        for fieldslist in fields:
            for field in fieldslist:
                if field not in df_keys:
                    click.echo(f"Unknown field '{ field }'. Try to use '--list' flag to see all avaliable fields.")

                    return
        
            tables.append(df[fieldslist])
    else:
        tables.append(df)

    if output == "plot":
        fig, ax = plt.subplots(nrows = 1, ncols = 1)

        for table in tables:
            table.plot(table.keys()[0], table.keys()[1], ax = ax, style = "o")

        plt.legend()
        plt.grid()
    
    if export:
        supported = ["csv", "jpg"]
        filepath, ext = os.path.splitext(export)
        ext = ext.replace(".", "")

        if ext not in supported:
            click.echo(f"Unknown extension '{ ext }'.")

            return

        if ext == "csv":
            if len(tables) == 1:
                tables[0].to_csv(export, sep = ";")
            
            else:
                for n, table in enumerate(tables):
                    table.to_csv("{}.{}.{}".format(filepath, n, ext), sep = ";")

        elif ext == "jpg":
            plt.savefig(export)

    else:

        if output == "cli":
            res = "\n\n".join([ table.to_string() for table in tables ])
            click.echo(res)

        elif output == "plot":
            plt.show()

    
###
#   CLI entry
##
if __name__ == "__main__":
    #try:
        anisotropy()

    #except KeyboardInterrupt:
    #    click.echo("Interrupted!")

    #finally:
    #    from anisotropy.salomepl.utils import SalomeManager
    #    click.echo("Exiting ...")

    #    if os.path.exists("anisotropy.pid"):
    #        os.remove("anisotropy.pid")

    #    SalomeManager().killall()

    #    sys.exit(0)
