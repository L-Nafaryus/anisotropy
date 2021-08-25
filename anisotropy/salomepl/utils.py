# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import subprocess
import logging
import sys, os
import re


class SalomeNotFound(Exception):
    pass


class SalomeManager(object):
    def __init__(self):
        self.__port = None
        self.__lastproc = None


    def runner(self, cmdargs: list, **kwargs):
        timeout = kwargs.pop("timeout") if kwargs.get("timeout") else None

        try:
            with subprocess.Popen(
                cmdargs,
                stdout = kwargs.pop("stdout") if kwargs.get("stdout") else subprocess.PIPE,
                stderr = kwargs.pop("stdout") if kwargs.get("stderr") else subprocess.PIPE,
                **kwargs
            ) as proc:
                self.__lastproc = proc
                out, err = proc.communicate(timeout = timeout)

        except FileNotFoundError:
            raise SalomeNotFound()

        return out, err, proc.returncode


    def port(self) -> int:
        out, err, returncode = self.runner(["salome", "start", "--print-port"], text = True)
        
        if returncode == 0:
            reg = re.search("(?!port:)([0-9]+)", out)

            if reg:
                return int(reg.group())

        return 2810


    def version(self) -> int:
        out, err, returncode = self.runner(["salome", "--version"], text = True)

        return out.strip().split(" ")[-1]


    def kill(self, port: int = None):
        return self.runner(["salome", "kill", str(self.__port or port)])


    def execute(self, scriptpath: str, *args, root: str = None, logpath: str = None, timeout: int = None, **kwargs):

        if not root:
            root = os.environ["HOME"]

        # ISSUE: salome removes commas from string list
        args = list(args)
        args.insert(1, root)

        salomeargs = "args:"
        salomeargs += ",".join([ '"{}"'.format(str(arg)) for arg in args ])

        if kwargs:
            salomeargs += "," + ",".join([ '{}="{}"'.format(k, v) for k, v in kwargs.items() ])

        ###
        self.__port = self.port()
        cmd = [
            "salome",
            "start", 
            "-t",
            "--shutdown-servers=1",
            "--port", str(self.__port),
            scriptpath,
            salomeargs
        ]

        try:
            out, err, returncode = self.runner(cmd, timeout = timeout)

        except subprocess.TimeoutExpired:
            lastproc = self.__lastproc
            self.kill()

            out, err = lastproc.communicate()
            returncode = lastproc.returncode

        if logpath:
            with open(os.path.join(logpath, "salome.log"), "wb") as io:
                io.write(out)
                io.write(err)

        return str(out, "utf-8"), str(err, "utf-8"), returncode


