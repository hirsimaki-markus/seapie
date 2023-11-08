#!/usr/bin/env python3

import importmonkey  # type: ignore  # silence pylance


def main():
    importmonkey.add_path("../src")
    import seapie
    from seapie import prompt

    # while True:
    #    print("got:", repr(tools.read_one_interpreter_input()))

    def lol():
        for i in range(2):
            kissa = "kissa"
            x = "x"
            print(x)
        return "nice"

    seapie.prompt()
    # 0 / 0
    importmonkey.add_path("../")

    x = 1
    y = 2
    z = 3
    # print(locals()["z"])
    print(z)
    lol()


if __name__ == "__main__":
    main()
    exit()
