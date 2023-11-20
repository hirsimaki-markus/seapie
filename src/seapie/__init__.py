#!/usr/bin/env python3

"""cpython depdency warning minne kaikkialle

mostly everything here is monolithic and the function are not reusable so you
should not try importing them except for the prompt. a lot of stuff depends on
a state stored in state.py

seapie is intended to be used in scripts, not in the interactive interpreter
"""

import sys

from .repl import prompt, true_exec
from .version import __version__  # noqa: F401  # Silence linting.

__author__ = "Markus Hirsimäki"
__copyright__ = "This work is dedicated to public domain under The Unlicense."
__license__ = "The Unlicense (https://choosealicense.com/licenses/unlicense/)"
__all__ = ["prompt", "true_exec"]

if hasattr(sys, "ps1"):
    msg = (
        "\nUsing seapie in interactive interpreter is not supported. See"
        " help(seapie) for more details. If you are just trying things out"
        " it's easiest to make a script and import seapie there.\n"
    )
    print(msg)

if (sys.version_info.major == 3) and (sys.version_info.minor < 12):
    print("\nPython 3.12.0 or later is recommended for seapie (PEP 709).\n")


asd = """
eai
█▀ █▀ █▀█ █▀█ █ █▀
▀█ █▀ █▀█ █▀▀ █ █▀
▀▀ ▀▀ ▀ ▀ ▀   ▀ ▀▀
█▀ █▀ █▀█ █▀█ █ █▀
▀█ █▀ ▌▀█ █▀▀ █ █▀
▀▀ ▀▀ ▌ ▀ ▀   ▀ ▀▀
box drawing heavy
▖▗ ▘▝ ▙ ▛ ▜ ▟ ▞ ▚ ▀ ▄
▄▄
▌▐
aaa
▛   ▛▜
▟   ▛▜ ▙ ▌▐▌▐ ▙▐

╝  ╗  ╔  ╚  ╣  ╩  ╦  ╠  ═  ║  ╬
┘  ┐  ┌  └  ┤  ┴  ┬  ├  ─  │  ┼
┌┐ ┌ ┌┐ ┌┐ ┬
└┐ ├ ┤ ├┘ │
└┘ └ ╹╵
      ╻
      ┗
╴  ╵  ╶  ╷  ╸  ╹  ╺  ╻


┏┓ ┏┓ ┏┓ ┏┓  ╻ ┏┓
┗┓ ┣┛ ┏┫ ┣┛ ╺┓ ┣┛
┗┛ ┗┛ ┗┛ ╹   ╹ ┗┛
╻╺╹╸
╻╺╹╸╋
┃
┫
━╺
╹╸╸╻
 ┏╸┏
╺┛ ┗╸
╻ ┃╸
"""
