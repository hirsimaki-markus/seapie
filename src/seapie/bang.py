"""
bang handler stuff
"""

import sys
import traceback
from .repl import CURRENT_SETTINGS


def bang_handler(bang, frame):
    """Attempts to do complete adnlings of bands. returns values only

    if the enclosing repl must take an action that cant be done here.

    dokumentoi tai poista aliakset

    possible actions and return values:
    * exit() happens
    * step-with-repl; repl should return itself as the new trace func
    * continue-in-repl; repl loop should "continue" in while and read new input
    * step-without-repl

    """
    bang = bang.lower()
    if bang in ("!e", "!exit", "!q", "!quit"):
        exit()
    elif bang in ("!s", "!step"):
        return "step-with-repl"
    elif bang in ("!r", "!run"):
        frame.f_trace = None
        sys.settrace(None)
        return "step-without-repl"
    elif bang in ("!t", "!traceback", "!tb"):
        print_tb(frame, 0)  # there are no seapie related frames to hide since
        # there is no exception going on.
        return "continue-in-repl"
    elif bang in ("!b", "!bar"):
        CURRENT_SETTINGS["show_bar"] = not CURRENT_SETTINGS["show_bar"]
        return "continue-in-repl"
    else:
        if bang.startswith("!"):  # got an invalid bang
            print(f"Invalid bang {bang}")
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
