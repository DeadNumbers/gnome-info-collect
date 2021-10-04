#!/usr/bin/env python

import subprocess
from sys import stderr

rc = subprocess.call("./gnome-info-collect.sh")

stderr.write("Program exited with code " + str(rc) + "\n")
