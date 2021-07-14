import click
from anisotropy.anisotropy import Anisotropy

pass_anisotropy = click.make_pass_decorator(Anisotropy)

@click.group()
@click.version_option(version = "", message = Anisotropy.version())
@click.pass_context
def anisotropy(ctx):
    ctx.obj = Anisotropy()


@anisotropy.command()
@click.option("-s", "--stage", "stage", type = click.Choice(["all", "mesh", "flow"]), default = "all")
@click.option("-p", "--param", "params", metavar = "key=value", multiple = True)
@pass_anisotropy
def compute(anisotropy, stage, params):
    pass

anisotropy()
