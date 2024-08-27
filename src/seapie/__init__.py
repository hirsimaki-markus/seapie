#!/usr/bin/env python3

"""cpython depdency warning minne kaikkialle

mostly everything here is monolithic and the function are not reusable so you
should not try importing them except for the prompt. a lot of stuff depends on
a state stored in state.py

seapie is intended to be used in scripts, not in the interactive interpreter
"""


from seapie.repl import set_trace

# __version__ is single source of truth for packaging; <major>.<minor>.<patch> is used.
# Trailing/leading zeroes are not allowed. Lone zeroes (such as in 0.1.0) are allowed.
# When incrementing any of major, minor, patch, reset other numbers after it to zero.
# A number with trailing zero is skipped (eg. 0.10.0) and incremented more (eg. 0.11.0).
__version__ = "3.0.2"
__author__ = "Markus Hirsimäki"
__copyright__ = "This work is dedicated to public domain under The Unlicense."
__license__ = "The Unlicense"
__all__ = ["set_trace"]
