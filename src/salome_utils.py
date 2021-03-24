#import salome
import subprocess
import logging

def hasDesktop() -> bool:
    return salome.sg.hasDesktop()

def startServer(port):

    logging.info("Starting SALOME on port {} ...".format(port))

    p = subprocess.run(["salome", "start", "--port", str(port), "-t"],
        #shell = False,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)

    return p


def killServer(port):

    logging.info("Terminating SALOME on port {} ...".format(port))

    p = subprocess.run(["salome", "kill", str(port)],
        #shell = True,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)

    return p

def remote(port, cmd):

    logging.info("Executing command in the SALOME on port {} ...".format(port))
    
    # cmd = "python -m"; = "python -c"
    p = subprocess.run(["salome", "remote", "-p", str(port), "--", str(cmd)],
        #shell = True,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)

    return p


