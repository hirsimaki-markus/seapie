#!/usr/bin/env python3

import importmonkey  # type: ignore

importmonkey.add_path("../src")  # type: ignore
import seapie  # noqa: E402


def main():
    # while True:
    #    print("got:", repr(tools.read_one_interpreter_input()))

    def lol():
        for i in range(2):
            kissa = "kissa"
            x = "x"
            print(x, kissa)
        return "nice"

    seapie.prompt()

    # 0 / 0

    x = 1
    lol()

    y = 2
    z = 3
    # print(locals()["z"])
    print(x)
    print(y)
    print(z)


if __name__ == "__main__":
    main()
    exit()
