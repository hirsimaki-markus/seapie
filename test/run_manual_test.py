#!/usr/bin/env python3

import importmonkey


def main():
    importmonkey.add_path("../src")
    import seapie
    from seapie import prompt

    # while True:
    #    print("got:", repr(tools.read_one_interpreter_input()))

    def lol():
        kissa = "kissa"
        x = "x"
        print(x)

    seapie.prompt()

    asd = 1
    lol()

    try:
        importmonkey.add_path()
    except:
        pass

    seapie.prompt()

    importmonkey.add_path()


if __name__ == "__main__":
    main()
