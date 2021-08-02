#import salome
import subprocess
import logging
import sys, os

def hasDesktop() -> bool:
    return salome.sg.hasDesktop()


class SalomeNotFound(Exception):
    pass


def version() -> str:
    if os.environ.get("SALOME_PATH"):
        cmd = os.path.join(os.environ["SALOME_PATH"], "salome")

    else:
        raise(SalomeNotFound("Can't find salome executable."))

    proc = subprocess.Popen(
        [ cmd, "--version" ], 
        stdout = subprocess.PIPE, 
        stderr = subprocess.PIPE
    )

    out, err = proc.communicate()

    return str(out, "utf-8").strip().split(" ")[-1]


def runSalome(port: int, scriptpath: str, root: str, logpath: str = None, *args) -> int:

    if os.environ.get("SALOME_PATH"):
        cmd = [ os.path.join(os.environ["SALOME_PATH"], "salome") ]

    else:
        raise(SalomeNotFound("Can't find salome executable."))

    if not logpath:
        logpath = "/tmp/salome.log"

    fullargs = list(args)
    fullargs.extend([ root, logpath ])
    fmtargs = "args:{}".format(", ".join([ str(arg) for arg in args ]))
    cmdargs = [
        "start", "-t",
        "--shutdown-servers=1",
        "--port", str(port),
        scriptpath,
        fmtargs
    ]

    cmd.extend(cmdargs)

    with subprocess.Popen(
        cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE
    ) as proc, open(logpath, "wb") as logfile:

        logfile = open(logpath, "wb")
        for line in proc.stdout:
            logfile.write(line)

        out, err = proc.communicate()

        if err:
            logfile.write(err)

    return out, err, proc.returncode

