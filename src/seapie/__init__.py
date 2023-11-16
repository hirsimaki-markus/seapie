#!/usr/bin/env python3

"""cpython depdency warning minne kaikkialle

mostly everything here is monolithic and the function are not reusable so you
should not try importing them except for the prompt. a lot of stuff depends on
a state stored in state.py

seapie is intended to be used in scripts, not in the interactive interpreter
"""

import sys

from .repl import prompt
from .version import ver

__version__ = ver
__author__ = "Markus Hirsimäki"
__copyright__ = "This work is dedicated to public domain under The Unlicense."
__license__ = "The Unlicense (https://choosealicense.com/licenses/unlicense/)"
__all__ = ["prompt", "seapie", "Seapie", "brk", "bp"]

seapie = prompt  # Alias for name used in seapie versions 1 and 2.
Seapie = prompt  # Alias for name used in seapie versions 1 and 2.
brk = prompt  # A better new alias.
bp = prompt  # A better new alias.

if hasattr(sys, "ps1"):
    msg = (
        "\nUsing seapie in the interactive interpreter is not supported."
        " See help(seapie) for more details on the limitation."
        " If you are just trying things out, the easies way is to make a script and import seapie there\n"
    )
    print(msg)
