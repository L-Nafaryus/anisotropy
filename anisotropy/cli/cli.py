# -*- coding: utf-8 -*-

import click
import pathlib
import os
import logging

from . import utils


@click.group()
@click.version_option()
def anisotropy_cli():
    pass


@anisotropy_cli.command(
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
    from anisotropy.core import config as core_config
    from anisotropy.core import utils as core_utils
    
    core_utils.setupLogger(utils.verbose_level(verbose))
    logger = logging.getLogger(__name__)
    
    config = core_config.default_config() 
    filepath = os.path.abspath(os.path.join(path, "anisotropy.toml"))
    
    logger.info(f"Saving file at { filepath }")
    config.dump(filepath)
    
    
@anisotropy_cli.command()
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
    # default = 1,
    help = "Count of parallel processes"
)
@click.option(
    "-s", "--stage", "stage", 
    type = click.Choice(["all", "shape", "mesh", "flow", "postProcess"]),
    # default = "all",
    help = "Current computation stage"
)
@click.option(
    "-f", "--force", "overwrite",
    is_flag = True,
    default = None,
    help = "Overwrite existing entries"
)
@click.option(
    "-p", "--params", "params", 
    metavar = "key=value", 
    multiple = True, 
    cls = utils.KeyValueOption,
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
    import anisotropy
    from anisotropy.core import UltimateRunner
    from anisotropy.core import config as core_config
    from anisotropy.core import utils as core_utils
    
    anisotropy.loadEnv()

    if path:
        path = pathlib.Path(path).resolve()

        os.makedirs(path, exist_ok = True)
        os.chdir(path)
        os.environ["AP_CWD"] = str(path)

    core_utils.setupLogger(utils.verbose_level(verbose), logfile)
    logger = logging.getLogger(__name__)
    
    config = core_config.default_config() 

    if configFile:
        configFile = pathlib.Path(configFile).resolve()

        logger.info(f"Loading file from { configFile }")

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

    print(config.options)
    if pid:
        pid = pathlib.Path(pid).resolve()

        with open(pid, "w") as io:
            io.write(str(os.getpid()))

    runner = UltimateRunner(config = config, exec_id = execution)
    runner.prepare_queue()
    runner.start()

    if pid:
        os.remove(pid)

    logger.info("Computation done. Exiting ...")


@anisotropy_cli.command()
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
def gui(path, verbose):
    import anisotropy
    from anisotropy.core import utils as core_utils
    from anisotropy import gui

    anisotropy.loadEnv()

    path = pathlib.Path(path).resolve()
    path.mkdir(parents = True, exist_ok = True)
    
    os.chdir(path)
    os.environ["ANISOTROPY_CWD"] = str(path)

    core_utils.setupLogger(utils.verbose_level(verbose))
    # logger = logging.getLogger(__name__)

    gui.run(debug = True)
