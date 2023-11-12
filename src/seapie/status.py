#!/usr/bin/env python3

import os
import linecache
from .settings import CURRENT_SETTINGS


def status_bar(current_frame, event, arg):
    """Uses vt100 coes to print a status bar at the top of the
    terminal. this has the side effect of overwriting history. If getting terminal
    size fails due to file descriptor not being connected to terminal, nothing
    is printed.

    if status is longer than terminal width, it gets cut.

    only prints the bar if current settings allow it.
    """
    if not CURRENT_SETTINGS["show_bar"]:
        return

    status_lines = get_status(current_frame, event, arg)

    try:
        width = os.get_terminal_size().columns
    except OSError:
        return

    # VT100 control codes required.
    save_cursor_pos = "\x1b[s"
    restore_cursor_pos = "\x1b[u"

    move_to_zero = "\x1b[0;0H"
    invert_color = "\x1b[7m"
    reset_color = "\x1b[0m"

    print(f"{save_cursor_pos}{move_to_zero}{invert_color}", end="", flush=True)
    for line in status_lines:
        # Slice end of message if it wont fit in one line. -1 keeps trailing space
        # also force leading space
        line = " " + line
        line = line[: width - 1]
        line = line.ljust(width)
        print(line)
    print(f"{reset_color}{restore_cursor_pos}", end="", flush=True)

    # formatted_status = f"{invert_color}{status.ljust(width)}{reset_color}"
    # out = f"{save_cursor_pos}{move_to_zero}{formatted_status}{restore_cursor_pos}"
    # print(out, flush=True, end="")


def get_status(frame, event, arg):
    """Creates a status string based on a given frame and event(str)

    returns list of lines to use as status

    """
    lines = []

    # get variables to use in lines
    # sep = " │ "  # This is not the same symbol as |
    filename = frame.f_code.co_filename or "None"
    scope = repr(frame.f_code.co_name) or "None"

    # 0 callstack
    accum = []
    callstack_frame = frame
    while callstack_frame:
        accum.append(callstack_frame.f_code.co_name)
        callstack_frame = callstack_frame.f_back
    lines.append(" → ".join(reversed(accum)))

    # get lines 1-3
    lines.append(f"file: {repr(filename)}")  # 1

    try:  # 2
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno
        current_line = linecache.getline(filename, lineno)
        lines.append(f"source: {repr(current_line.strip())}")
    except Exception as e:
        lines.append("None")

    lines.append(  # 3
        f"lineno: {frame.f_lineno}      scope: {scope}      event: {repr(event)}"
    )

    # additional stuff for sometimes.
    # if event == "return":  # 4
    #    # A given object's repr() might fail for some objects so we default
    #    # back to object.__repr__ if neded
    #    try:
    #        retval = f"{repr(arg)}"
    #    except Exception:
    #        retval = f"{object.__repr__(arg)}"
    #    lines.append(retval)
    # if event == "exception":  # 4
    #    lines.append(repr(arg[1]))

    return lines


def print_pickles():
    pickles_dir = os.path.join(os.path.expanduser("~"), ".seapie", "pickles")
    width = os.get_terminal_size().columns  # get term size

    # Load all file names into a list and sort by length
    filenames = sorted(os.listdir(pickles_dir), key=len, reverse=True)

    pad_size = len(max(filenames, key=len)) + 1

    filenames = [i.ljust(pad_size) for i in filenames]

    # No need for fancy logic; stuff wont fit anyways.
    if len(filenames[0]) >= width:
        filenames.reverse()
        for file in filenames:
            print(file)
        return
    else:  # attempt to fit more names per line
        line_accum = []
        while filenames:
            filename = filenames.pop()
            line_accum.append(filename)

            if len("".join(line_accum)) < width:
                if filenames == []:  # reached last item, just print it
                    print("".join(line_accum))
                else:
                    continue  # Keep adding more until line wont fit
            else:
                filenames.append(line_accum.pop())  # Undo the newest adding
                print("".join(line_accum))
                line_accum = []
