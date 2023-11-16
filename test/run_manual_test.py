#!/usr/bin/env python3

import importmonkey

importmonkey.add_path("../src")
import seapie  # noqa: E402, F401  # Silence linting.
from seapie import prompt


def main():
    # while True:
    #    print("got:", repr(tools.read_one_interpreter_input()))

    def lol():
        for i in range(2):
            kissa = "kissa"
            x = "x"
            print(x, kissa)
        return "nice"

    # [seapie.prompt() for i in "asd"]
    seapie.prompt()
    seapie.prompt()
    0 / 0

    x = 1
    # lol()

    y = 2
    z = 3
    # print(locals()["z"])
    print(x)
    print(y)
    print(z)


if __name__ == "__main__":
    main()
    exit()
