#!/usr/bin/env python
# -*- coding: utf-8 -*-

import salome

def hasDesktop() -> bool:
    return salome.sg.hasDesktop()

def startServer(port, logPath):

    log = open("{}/salome.log".format(logPath), "a")
    logging.info("Starting SALOME on port {} ...".format(port))

    p = subprocess.Popen(["salome", "start", "--port", str(port), "-t"],
        shell = True,
        stdout = log,
        stderr = log)

    log.close()

    return p

def killServer(port, logPath):

    log = open("{}/salome.log".format(logPath), "a")
    logging.info("Terminating SALOME on port {} ...".format(port))

    p = subprocess.Popen(["salome", "kill", str(port)],
        shell = True,
        stdout = log,
        stderr = log)

    log.close()

    return p

def execute(port, cmd, logPath):

    log = open("{}/salome.log".format(logPath), "a")
    logging.info("Executing command in the SALOME on port {} ...".format(port))

    p = subprocess.Popen(["salome", "connect", "-p", str(port), str(cmd)],
        shell = True,
        stdout = log,
        stderr = log)

    log.close()

    return p


