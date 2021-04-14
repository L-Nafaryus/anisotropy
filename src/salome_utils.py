#import salome
import subprocess
import logging
import sys

def hasDesktop() -> bool:
    return salome.sg.hasDesktop()

def startServer(port):

    logging.info("Starting SALOME on port {} ...".format(port))

    p = subprocess.Popen(["salome", "start", "--port", str(port), "-t"],
        #shell = False,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)

    return p

def salomeVersion() -> str:
    return "Salome 9.6.0"

def runExecute(port: int, scriptpath: str, *args) -> int:

    cmd = ["salome", "start", "--shutdown-servers=1", "--port", str(port), "-t",
        scriptpath, "args:{}".format(", ".join([str(arg) for arg in args]))]

    logging.info("salome: {}".format(cmd[1 : 6]))
    #logpath = os.path.join()

    #p = subprocess.Popen(["salome", "start", "--shutdown-servers=1", "--port", str(port), "-t", scriptpath, "args:{}".format(", ".join([str(arg) for arg in args]))],
    #    stderr = subprocess.STDOUT)
    #_, err = p.communicate()

    with subprocess.Popen(cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE) as p:

        #for line in p.stdout:
        #    sys.stdout.buffer.write(line)
        #    logfile.write(line)

        out, err = p.communicate()
        print(str(err, "utf-8"))
        #logfile.write(err)

        if err and p.returncode == 1:
            logging.error("salome:\n\t{}".format(str(err, "utf-8")))
    #if err:
    #    if p.returncode == 1:
    #        logging.error(err)

     #   else:
     #       logging.warning(err)

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


