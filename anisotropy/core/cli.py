import click

#pass_anisotropy = click.make_pass_decorator(Anisotropy)
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

@anisotropy.command()
@click.option("-s", "--stage", "stage", type = click.Choice(["all", "mesh", "flow"]), default = "all")
@click.option("-p", "--param", "params", metavar = "key=value", multiple = True)
def compute(stage, params):
    from anisotropy.core.main import Anisotropy

    model = Anisotropy()
    model.db.setup()

    if model.db.isempty():
        paramsAll = model.loadFromScratch()

        for entry in paramsAll:
            model.db.update(entry)

    (type, direction, theta) = ("simple", [1.0, 0.0, 0.0], 0.01)

    model.load(type, direction, theta)
    # TODO: merge cli params with db params here 
    model.evalParams()
    model.update()

    # TODO: do smth with output
    if stage == "all" or stage == "mesh":
        ((out, err, code), elapsed) = model.computeMesh(type, direction, theta)

        model.load(type, direction, theta)
        model.params["meshresult"]["calculationTime"] = elapsed
        model.update()

    if stage == "all" or stage == "flow":
        ((out, err, code), elapsed) = model.computeFlow(type, direction, theta)


@anisotropy.command()
@click.argument("root")
@click.argument("type")
@click.argument("direction")
@click.argument("theta")
def computemesh(root, type, direction, theta):
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
