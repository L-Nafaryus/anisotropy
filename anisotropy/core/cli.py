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
    model.setupDB()

    if model.isEmptyDB():
        paramsAll = model.loadFromScratch()

        for entry in paramsAll:
            model.updateDB(entry)

    model.loadDB(type, direction, theta)
    # TODO: merge cli params with db params here 
    model.evalParams()
    model.updateDB()

    # TODO: do smth with output
    if stage == "all" or stage == "mesh":
        ((out, err, code), elapsed) = model.computeMesh(type, direction, theta)

    if stage == "all" or stage == "flow":
        ((out, err, code), elapsed) = model.computeFlow(type, direction, theta)


@anisotropy.command()
@click.argument("root")
@click.argument("name")
@click.argument("direction")
@click.argument("theta", type = click.FLOAT)
def _compute_mesh(root, name, direction, theta):
    # [Salome Environment]

    ###
    #   Args
    ##
    direction = list(map(lambda num: float(num), direction[1:-1].split(",")))

    ###
    #   Modules
    ##
    import salome

    sys.path.extend([
        root,
        os.path.join(root, "env/lib/python3.9/site-packages")
    ])

    from anisotropy.core.main import Anisotropy

    ###
    model = Anisotropy()
    model.setupDB()
    model.loadDB(type, direction, theta)

    model.genmesh()


###
#   CLI entry
##
#anisotropy()
