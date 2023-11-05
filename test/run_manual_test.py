#!/usr/bin/env python3

import importmonkey
import sys


if __name__ == "__main__":
    importmonkey.add_path("../src")
    import seapie
    from seapie import repl

    # while True:
    #    print("got:", repr(tools.read_one_interpreter_input()))

    def lol():
        kissa = "kissa"
        x = "x"
        print(x)

    seapie.breakpoint()

    asd = 1
    lol()

    importmonkey.add_path()
