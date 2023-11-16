#!/usr/bin/env python3

"""Docstring. cpython depdency warning minne kaikkialle

mostly everything here is monolithic and the function are not reusable so you
should not try importing them except for the prompt. a lot of stuff depends on
a state stored in settings.py



"""
from .repl import prompt, repl_exec
from .version import ver

__version__ = ver
__author__ = "Markus Hirsimäki"
__copyright__ = "This work is dedicated to public domain under The Unlicense."
__license__ = "The Unlicense (https://choosealicense.com/licenses/unlicense/)"
__all__ = [
    "repl_exec",  # Part of actual repl.
    "prompt",  # Breakpoint to trigger repl.
    "seapie",  # Backwards compatibility alias.
    "Seapie",  # Backwards compatibility alias.
    "true_exec",  # Backwards compatibility alias.
    "brk",  # New alias.
    "bp",  # New alias.
]

# Old names for compatibility with version 1.x.x and 2.x.x naming schemes.
seapie = prompt
Seapie = prompt
true_exec = repl_exec

# Provide two common aliases for breakpoint.
brk = prompt
bp = prompt
