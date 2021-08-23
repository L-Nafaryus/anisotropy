# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import click
import ast

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
    "-P", "--parallel", "parallel",
    type = click.INT,
    default = 1,
    help = "Count of parallel processes"
)
@click.option(
    "-p", "--param", "params", 
    metavar = "key=value", 
    multiple = True, 
    cls = KeyValueOption,
    help = "Overwrite existing parameter (except control variables)"
)
def compute(stage, parallel, params):
    from anisotropy.core.main import Anisotropy, logger
    from anisotropy.core.utils import timer

    args = dict()

    for param in params:
        args.update(param)


    model = Anisotropy()
    model.db.setup()

    if model.db.isempty():
        paramsAll = model.loadFromScratch()

        for entry in paramsAll:
            model.db.update(entry)

    type, direction, theta = args["type"], args["direction"], args["theta"]
    
    
    model.load(type, direction, theta)
    # TODO: merge cli params with db params here 
    model.evalParams()
    model.update()

    # TODO: single compute / queue
    
    if stage == "all" or stage == "mesh":
        ((out, err, code), elapsed) = timer(model.computeMesh)()

        if out: click.echo(out)
        if err: click.echo(err)

        if model.params.get("meshresult"):
            model.load(type, direction, theta)
            model.params["meshresult"]["calculationTime"] = elapsed
            model.update()

    if stage == "all" or stage == "flow":
        ((out, err, code), elapsed) = timer(model.computeFlow)()

        if out: click.echo(out)
        if err: click.echo(err)

        if model.params.get("flowresult"):
            model.load(type, direction, theta)
            model.params["flowresult"]["calculationTime"] = elapsed
            model.update()


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