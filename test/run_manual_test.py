#!/usr/bin/env python3



from seapie import set_trace  # noqa: E402, F401  # Silence linting.


def say_goodbye():
    print("Goodbye, World!")

# Register the function to be called on exit
#atexit.register(say_goodbye)


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
    set_trace()
    #prompt()
    #self = exit

    "asd"
    "asd"
    #os._exit(1)
    exit()
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
