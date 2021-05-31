import os, sys
import subprocess

sys.path.append(os.path.abspath("../"))

import logging
logger = logging.getLogger()

from openfoam.miscellaneous import *
from openfoam.meshConversion import *
from openfoam.meshManipulation import *
from openfoam.parallelProcessing import *
from openfoam.solvers import *

def application(name: str, *args: str, case: str = None, stderr: bool = True, useMPI: bool = False) -> int:
    
    cmd = []

    if useMPI:
        nprocs = os.cpu_count()
        cmd.extend(["mpirun", "-np", str(nprocs), "--oversubscribe"])
    
    cmd.append(name)

    if case:
        cmd.extend(["-case", case])

    if args:
        cmd.extend([*args])
        
    logger.info("{}: {}".format(name, [*args]))
    logpath = os.path.join(case if case else "", "{}.log".format(name))
   
    with subprocess.Popen(cmd, 
        stdout = subprocess.PIPE, 
        stderr = subprocess.PIPE) as p, \
        open(logpath, "wb") as logfile:
        
        for line in p.stdout:
            #sys.stdout.buffer.write(line) 
            logfile.write(line)

        #for line in p.stderr:
        #    logfile.write(line)

        out, err = p.communicate()
        logfile.write(err)

        if err and stderr:
            logger.error("""{}:
            {}""".format(name, str(err, "utf-8")))

    return out, p.returncode


