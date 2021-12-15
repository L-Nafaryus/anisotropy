# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import os
import subprocess
import sys
from typing import List
import logging

logger = logging.getLogger(__name__)

class FoamRunner(object):
    def __init__(self, command: str, args: List[str] = None, mpi: bool = False, cwd: str = None, logpath: str = None, exit: bool = False):
        self.command = command
        self.args = args
        self.mpi = mpi
        self.cwd = cwd or os.getcwd()
        self.logpath = logpath
        self.exit = exit
        self.output = ""
        self.error = ""
        self.returncode = 0

    def fullcommand(self) -> List[str]:
        command = []

        if self.mpi:
            nprocs = os.cpu_count()
            command.extend(["mpirun", "-np", str(nprocs), "--oversubscribe"])

        command.append(self.command)

        if self.args:
            command.extend([ str(arg) for arg in self.args ])

        return command

    def run(self) -> tuple[str, str, int]:
        try:
            proc = subprocess.Popen(
                self.fullcommand(),
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                encoding = "utf-8",
                cwd = self.cwd
            )

            logger.debug(f"Starting subprocess: { proc.args }")

            self.output, self.error = proc.communicate()
            self.returncode = proc.returncode

        except FileNotFoundError as err:
            self.error = err
            self.returncode = 2

            logger.error(self.error, exc_info = True)

        if self.logpath:
            with open(self.logpath, "w") as io:
                if self.output:
                    io.write(self.output)

                if self.error:
                    io.write(self.error)

                io.write(f"Exit code { self.returncode }")

        if not self.returncode == 0 and self.exit:
            raise Exception(f"Subprocess failed: { proc.args }")

        return self.output, self.error, self.returncode