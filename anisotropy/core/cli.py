# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import click
import ast
import os
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

        
def verboseLevel(level: int):
    return {
        0: logging.ERROR,
        1: logging.INFO,
        2: logging.DEBUG
    }.get(level, logging.ERROR)


@click.group()
@click.version_option()
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
@click.option(
    "-v", "--verbose", "verbose",
    count = True,
    help = "Increase verbose level"
)
def init(path, verbose):
    from anisotropy.core.config import DefaultConfig
    from anisotropy.core.utils import setupLogger
    
    setupLogger(verboseLevel(verbose))
    logger = logging.getLogger(__name__)
    
    config = DefaultConfig() 
    filepath = os.path.abspath(os.path.join(path, "anisotropy.toml"))
    
    logger.info(f"Saving file at { filepath }")
    config.dump(filepath)
    
    
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
    #default = 1,
    help = "Count of parallel processes"
)
@click.option(
    "-s", "--stage", "stage", 
    type = click.Choice(["all", "shape", "mesh", "flow", "postProcess"]),
    #default = "all",
    help = "Current computation stage"
)
@click.option(
    "-f", "--force", "overwrite",
    is_flag = True,
    #default = False,
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
    "-v", "--verbose", "verbose",
    count = True,
    help = "Increase verbose level"
)
@click.option(
    "--exec-id", "execution"
)
@click.option(
    "--pid", "pid",
    help = "Specify pid file path"
)
@click.option(
    "--logfile", "logfile",
    help = "Specify log file path"
)
def compute(path, configFile, nprocs, stage, overwrite, params, verbose, execution, pid, logfile):
    from anisotropy.core.runner import UltimateRunner
    from anisotropy.core.config import DefaultConfig
    from anisotropy.core.utils import setupLogger
    
    if path:
        os.makedirs(os.path.abspath(path), exist_ok = True)
        os.chdir(os.path.abspath(path))

    setupLogger(verboseLevel(verbose), logfile)
    logger = logging.getLogger(__name__)
    
    config = DefaultConfig() 

    if configFile:
        filepath = os.path.abspath(configFile)
        logger.info(f"Loading file from { filepath }")

        try:
            config.load(configFile)

        except FileNotFoundError:
            config.dump(configFile)

    else:
        logger.info("Using default configuration")

    args = {
        "nprocs": nprocs,
        "stage": stage,
        "overwrite": overwrite 
    }

    for k, v in args.items():
        if v is not None:
            config.update(**{ k: v })
    
    if pid:
        pidpath = os.path.abspath(pid)

        with open(pidpath, "w") as io:
            io.write(str(os.getpid()))

    runner = UltimateRunner(config = config, exec_id = execution)
    runner.fill()
    runner.start()

    os.remove(pidpath)

@anisotropy.command()
@click.option(
    "-P", "--path", "path",
    default = os.getcwd(),
    help = "Specify directory to use (instead of cwd)"
)
@click.option(
    "-v", "--verbose", "verbose",
    count = True,
    help = "Increase verbose level"
)
def gui(verbose):
    import anisotropy
    from anisotropy.core.utils import setupLogger
    from anisotropy.gui import app 

    anisotropy.loadEnv()

    os.makedirs(os.path.abspath(path), exist_ok = True)
    os.chdir(os.path.abspath(path))
    os.environ["ANISOTROPY_CWD"] = path

    setupLogger(verboseLevel(verbose))
    logger = logging.getLogger(__name__)

    app.run_server(debug = True)


##############
"""


@click.group()
@click.version_option(version = "", message = version())
def anisotropy():
    pass


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

"""    
###
#   CLI entry
##
if __name__ == "__main__":
    #try:
        anisotropy()

    #except KeyboardInterrupt:
    #    click.echo("Interrupted!")

    #finally:
    #    sys.exit(0)
