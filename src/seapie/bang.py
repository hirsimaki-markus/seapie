"""
bang handler stuff and related tools
"""

import os
import sys
import traceback
from .settings import CURRENT_SETTINGS
from .status import get_status


def bang_handler(user_input, frame, event, arg):
    """Attempts to do complete adnlings of bands. returns values only

    if the enclosing repl must take an action that cant be done here.

    dokumentoi tai poista aliakset

    possible actions and return values:
    * exit() happens
    * step-with-repl; repl should return itself as the new trace func
    * continue-in-repl; repl loop should "continue" in while and read new input
    * step-without-repl

    """
    user_input = user_input.lower()
    if user_input in ("!e", "!exit"):
        exit()  # raises system exit that takes a moment to propagate and cleanup
    elif user_input in ("!q", "!quit"):
        os._exit(1)  # exit ungracefully right now.
    elif user_input in ("!s", "!step"):
        return "step-with-repl"
    elif user_input in ("!r", "!run"):
        frame.f_trace = None
        sys.settrace(None)
        return "step-without-repl"
    elif user_input in ("!h", "!help"):
        print_help()
        return "continue-in-repl"
    elif user_input in ("!t", "!traceback", "!tb"):
        print_tb(frame, 0)  # there are no seapie related frames to hide since
        # there is no exception going on.
        return "continue-in-repl"
    elif user_input in ("!b", "!bar"):
        CURRENT_SETTINGS["show_bar"] = not CURRENT_SETTINGS["show_bar"]
        return "continue-in-repl"
    elif user_input in ("!i", "!info"):
        print(get_status(frame, event, arg))
        return "continue-in-repl"
    elif user_input in ("!w", "!where"):
        print_source_lines(frame)
        return "continue-in-repl"
    elif user_input.startswith("!g") or user_input.startswith("!goto"):
        do_goto(frame, user_input)
        return "continue-in-repl"
    else:
        if user_input.startswith("!"):  # got an invalid bang
            print(f"Invalid bang {user_input}")
            return "continue-in-repl"
        else:  # got code
            return


def print_tb(frame, num_frames_to_hide):
    """
    if exception occurs in seapie, num frames tells how many seapie
    relatd frames to hide from the traceback found in exception.
    this is joined with other frames found with tb.extact_stack to show
    all frames from original source and frames from input but not seape itself
    """
    exc_type, exc_val, exc_tb = sys.exc_info()  # Get the traceback

    # if (exc_type, exc_val, exc_tb) == (None, None, None):
    #    # print_tb was called when there is no exception, use stack instead.
    #    # all frames can be found here when there is not exception going on.
    #    tb_frames = traceback.extract_stack()
    # else:
    #    # Extract the traceback frames from the exception object because
    #    # there is an exception going on and we need all frames available
    #    tb_frames = traceback.extract_tb(exc_tb)

    # need to use extract stack to include all frames in stack
    # tb_frames = traceback.extract_stack()

    traceback_exc = traceback.TracebackException(*sys.exc_info())
    # tämä lupaa piilottaa kaiken tästä moduulista, eli mikään mitä täältä moduulista kutsutaan ei saa nostaa itse herjaa tai se tulee näkyville!

    # seapie would be present here so we hide it from the middle of the stack
    # Exclude the frames occupied by the debugger
    # if num_frames_to_hide == 0:
    #    # manual check needed because [:-0] is empty list instead of full
    #    tb_exc_stack_filtered = traceback_exc.stack
    # else:
    tb_exc_stack_filtered = traceback_exc.stack[num_frames_to_hide:]

    # we have to use both traceback.extract_stack(frame) and traceback_exc.stack
    # because otherwise frames created in seapie repl would not be visible
    # or frames created in original source would not be visible
    tb_frames = traceback.extract_stack(frame) + tb_exc_stack_filtered

    # Format the filtered traceback
    formatted_traceback = "".join(traceback.format_list(tb_frames))

    print("Traceback (most recent call last):")  # Print header.
    print(formatted_traceback, end="")  # Print traceback,

    # Only print the error itself if an exception is being handled
    if exc_type is not None and exc_val is not None:
        print(f"{exc_type.__name__}: {exc_val}")


def print_source_lines(frame):
    """Reponds to term size"""
    try:
        width = os.get_terminal_size().columns
    except OSError:
        width = 80

    current_lineno = frame.f_lineno
    filename = frame.f_globals.get("__file__")  # Null check with .get

    if filename is None:
        print("Unable to retrieve the current filename.")
        return

    try:
        with open(filename, "r") as file:
            lines = file.readlines()
    except OSError as e:
        print(f"Error opening file: {e}")
        return

    invert_color = "\x1b[7m"
    reset_color = "\x1b[0m"

    max_lineno_width = len(str(len(lines)))

    for lineno, line in enumerate(lines, start=1):
        line = line[:-1]  # Remove trailing newline with -1
        line_prefix = "-->" if lineno == current_lineno else "   "
        linenum = str(lineno).rjust(max_lineno_width)  # right aling lineno
        if abs(lineno - current_lineno) <= 10:  # show 10 prev and following lines
            out = f"{invert_color}{linenum}{reset_color} {line_prefix}{line}"
            # invert color and reset color lenghts are added to width since
            # they are invisible and dont actually take up space
            out = out[: width + len(invert_color) + len(reset_color)]

            print(out)


def do_goto(frame, user_input):
    """Wohoo. goto in python."""
    command_parts = user_input.split(" ")
    if command_parts[0] not in ("!g", "!goto"):
        print(f"Invalid bang {user_input}")
        return
    if len(command_parts) == 2:
        line_number_str = command_parts[1]
        if line_number_str.isdigit():
            line_number = int(line_number_str)
        else:
            print("Invalid line number. Use: !g 123 or !goto 123")
            return
    else:
        print("Invalid bang. Use: !g 123 or !goto 123")
        return

    try:
        frame.f_lineno = line_number
    except Exception as e:
        print("Goto failed:", str(e))
        return
    else:
        print("Goto succeeded. Next line to execute is", line_number)
        return


def print_help():
    print("nice")
