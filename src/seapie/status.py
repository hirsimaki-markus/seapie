#!/usr/bin/env python3

import os
import pathlib


def print_status_bar(status):
    """Uses vt100 coes to print a status bar at the top of the
    terminal. this has the side effect of overwriting history. If getting terminal
    size fails due to file descriptor not being connected to terminal, nothing
    is printed.

    if status is longer than terminal width, it gets cut.
    """
    try:
        width = os.get_terminal_size().columns
    except OSError:
        return

    # Slice end of message if it wont fit in one line. -1 keeps trailing space
    # also force leading space
    status = " " + status[: (width - 1)]

    # VT100 control codes required.
    move_to_zero = "\x1b[0;0H"
    save_cursor_pos = "\x1b[s"
    restore_cursor_pos = "\x1b[u"
    invert_color = "\x1b[7m"
    reset_color = "\x1b[0m"

    formatted_status = f"{invert_color}{status.ljust(width)}{reset_color}"
    out = f"{save_cursor_pos}{move_to_zero}{formatted_status}{restore_cursor_pos}"
    print(out, flush=True, end="")


def get_status(frame, event, arg):
    """Creates a status string based on a given frame and event(str)"""
    sep = " │ "  # This is not the same symbol as |
    # Null check with 'or ""'
    filename = pathlib.Path(frame.f_code.co_filename or "").name

    status = f"{filename}{sep}no. {frame.f_lineno}{sep}{event.upper()}"

    if event == "call":
        callee_name = frame.f_code.co_name
        caller_name = frame.f_back.f_code.co_name
        status = f"{status}{sep}{caller_name} → {callee_name}"
    elif event == "line":
        pass
    elif event == "return":
        # If returning from main to bash i.e.: about to exit.
        callee_name = frame.f_code.co_name
        if frame.f_back is None:
            caller_name = "None"
        else:
            caller_name = frame.f_back.f_code.co_name
        retval = f"returning {repr(arg)}"
        status = f"{status}{sep}{caller_name} ← {callee_name}" f"{sep}{retval}"
    elif event == "exception":
        status = f"{status}{sep} raising {repr(arg[1])}"
    return status
