# -*- coding: utf-8 -*-
#
#  VULNERS OPENSOURCE
#  __________________
#
#  Vulners Project [https://vulners.com]
#  All Rights Reserved.
#
__author__ = "Kir Ermakov <isox@vulners.com>"

import os
import platform
import subprocess
from time import sleep


def find_linux_executable(prog_filename):
    bdirs = os.path.expandvars("$PATH").split(":")
    paths_tried = []
    for d in bdirs:
        p = os.path.expandvars(os.path.join(d, prog_filename))
        paths_tried.append(p)
        if os.path.exists(p):
            return p


def execute(cmd):

    # Using https://stackoverflow.com/questions/4760215/running-shell-command-and-capturing-the-output
    # Little mods

    def _execute_cmd(command):

        if os.name == "nt" or platform.system() == "Windows":
            # set stdin, out, err all to PIPE to get results (other than None) after run the Popen() instance
            p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        else:
            # Use bash if it exist
            p = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                executable=find_linux_executable("bash"),
            )

        # the Popen() instance starts running once instantiated (??)
        # additionally, communicate(), or poll() and wait process to terminate
        # communicate() accepts optional input as stdin to the pipe (requires setting stdin=subprocess.PIPE above), return out, err as tuple
        # if communicate(), the results are buffered in memory

        # Read stdout from subprocess until the buffer is empty !
        # if error occurs, the stdout is '', which means the below loop is essentially skipped
        # A prefix of 'b' or 'B' is ignored in Python 2;
        # it indicates that the literal should become a bytes literal in Python 3
        # (e.g. when code is automatically converted with 2to3).
        # return iter(p.stdout.readline, b'')

        for line in iter(p.stdout.readline, b""):
            yield line
        while p.poll() is None:
            # Don't waste CPU-cycles
            sleep(0.1)
        # Empty STDERR buffer
        err = p.stderr.read()
        if p.returncode != 0:
            yield err

    out = []
    for line in _execute_cmd(cmd):
        # error did not occur earlier
        if line is not None:
            # trailing comma to avoid a newline (by print itself) being printed
            out.append(line.strip().decode())
    return "\n".join(out)
