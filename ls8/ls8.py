#!/usr/bin/env python3

"""Main."""

import os
import sys

from cpu import *

os.system("clear")

cpu = CPU()
cpu.load()
cpu.run()
