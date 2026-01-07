#!/usr/bin/env python3
import threading
import time
import random

def noisy(msg):
    print(f"[noisy] {msg}")

class Manager:
    def __enter__(self):
        noisy("enter manager")
        return self

    def __exit__(self, exc_type, exc, tb):
        noisy(f"exit manager exc={exc_type}")
        return False  # do not suppress

def sometimes(x):
    if x % 2 == 0:
        raise RuntimeError(f"boom {x}")
    return x * 10

def gen(n):
    for i in range(n):
        yield i
        time.sleep(0.05)

def recursive(n):
    if n <= 0:
        return "done"
    return recursive(n - 1)

def threaded():
    for i in range(3):
        noisy(f"thread tick {i}")
        time.sleep(0.07)

def controller():
    noisy("controller start")

    with Manager():
        for i in gen(5):
            try:
                noisy(f"loop {i}")
                sometimes(i)
            except RuntimeError as e:
                noisy(f"caught {e}")
            finally:
                noisy("finally block")

    noisy("starting recursion")
    import seapie; seapie.breakpoint()
    recursive(3)

    noisy("spawning thread")
    t = threading.Thread(target=threaded, daemon=True)
    t.start()

    noisy("controller end")
    return "ok"

def main():
    import seapie; seapie.breakpoint()

    result = controller()
    noisy(f"result = {result}")

    time.sleep(0.5)  # let thread finish

if __name__ == "__main__":
    main()