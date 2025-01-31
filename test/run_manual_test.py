#!/usr/bin/env python3
import sys

import seapie
import seapie.prompt  # noqa: E402, F401  # Silence linting.
from seapie import set_trace


def level2():

    ##sys.settrace(seapie.repl.repl)
    #sys._getframe(0).f_trace = seapie.repl.repl

    print("Goodbye, World!")
    return "byeee"

def level1():
    set_trace()
    #breakpoint()
    print("Goodbye, World!")

    level2()
    #breakpoint()

    return "byeee"


def main():


    level1()
    x = 1
    y = 2
    z = 3
    print(x)
    print(y)
    print(sys.gettrace())
    print(z)
    0/0

if __name__ == "__main__":
    main()
    exit()

