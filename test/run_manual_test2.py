#!/usr/bin/env python3
import time
import random

def compute(value):
    result = value * 2
    if result % 3 == 0:
        raise ValueError("Bad multiple of 3")
    return result

def worker(limit):
    total = 0
    i = 0

    while i < limit:
        total += i
        i += 1
        time.sleep(0.1)   # slow enough to step, fast enough to continue

    return total

def controller():
    retries = 3
    value = random.randint(1, 10)

    while retries > 0:
        try:
            out = compute(value)
            print("compute:", out)
            break
        except ValueError as e:
            print("error:", e)
            value += 1
            retries -= 1

    result = worker(value)
    print("worker result:", result)
    return result

def main():
    import seapie; seapie.breakpoint()   # 🔴 primary breakpoint

    final = controller()
    print("final:", final)

if __name__ == "__main__":
    main()