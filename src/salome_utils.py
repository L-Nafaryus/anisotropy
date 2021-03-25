#import salome
import subprocess
import logging

def hasDesktop() -> bool:
    return salome.sg.hasDesktop()

def startServer(port):

    logging.info("Starting SALOME on port {} ...".format(port))

    p = subprocess.Popen(["salome", "start", "--port", str(port), "-t"],
        #shell = False,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)

    return p

def runExecute(port, scriptpath, *args):

    logging.info("Starting SALOME on port {}".format(port))

    p = subprocess.Popen(["salome", "start", "--shutdown-servers=1", "--port", str(port), "-t", scriptpath, "args:{}".format(", ".join([str(arg) for arg in args]))],
        stderr = subprocess.STDOUT)
    _, err = p.communicate()

    if err:
        if p.returncode == 1:
            logging.error(err)

        else:
            logging.warning(err)

    return p.returncode

def killServer(port):

    logging.info("Terminating SALOME on port {} ...".format(port))

    p = subprocess.Popen(["salome", "kill", str(port)],
        #shell = True,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)

    return p

def remote(port, cmd):

    logging.info("Executing command in the SALOME on port {} ...".format(port))
    
    # cmd = "python -m"; = "python -c"
    p = subprocess.Popen(["salome", "remote", "-p", str(port), "--", str(cmd)],
        #shell = True,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)

    return p


