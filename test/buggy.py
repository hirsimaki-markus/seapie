def compute_total(items):
    import seapie; seapie.breakpoint()  # seapie starts here >>>
    if "bad input value" in items:
        raise ValueError("oops")
    return sum(items)

print(compute_total([10, 20, 30, "bad input value"]))
