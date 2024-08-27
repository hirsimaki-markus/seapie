"""helper functions that do not belong in other places"""

import contextlib
import linecache
import platform
import sys
import traceback

import seapie.helpers


class Step(BaseException):
    """Used to trigger step in seapie repl loop."""

class Continue(BaseException):
    """Used to trigger continue in seapie repl loop"""


@contextlib.contextmanager
def handle_input_exceptions(working_f):
    """Handles possible errors produced by get_repl_input. Continue exception signals control flow to repl."""
    try:  # Code from the with statement gets executed here in yield.
        yield
    except EOFError:  # Mimic EOF behaviour from ctrl+d / ctrl+z by user in input.
        exit(print())  # Print a newline before exit. Return value doesn't get printed.
    except KeyboardInterrupt:  # Mimic kbint from ctrl+c by user in input.
        seapie.helpers.mimic_traceback(working_f, frames_to_hide=2)
        raise Continue
    except (SyntaxError, ValueError, OverflowError):  # Parsing fail in get_repl_input.
        seapie.helpers.mimic_traceback(working_f, frames_to_hide=5)
        raise Continue

@contextlib.contextmanager
def handle_exec_exceptions(working_f):
    """Handles possible errors produced by exec_input. Continue exception signals control flow to repl."""
    try:  # Code from the with statement gets executed here in yield.
        yield
    except (MemoryError, SystemExit):  # Must reraise critical errors.
        raise
    except seapie.helpers.Step:  # A handler signaled that repl loop mus step.
        raise  # Reraise the exception so that it can propagate. prevent getting caught in baseexception
    except seapie.helpers.Continue:
        raise
    except BaseException:  # Show trace for misc. exec_input errors like invalid syntax.
        seapie.helpers.mimic_traceback(working_f, 1)



def inject_magic_vars(current_frame, event, arg):
    # inject useful variables to the frame. this change should propagate
    # since we are in trace function. and running 3.12.
    # this must happen before exec (i think)
    # otherwise we would need
    # ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame),
    # ctypes.c_int(1))
    # maybe. or it works because we are in the trace function.

    accum = []
    callstack_frame = current_frame
    while callstack_frame:
        accum.append(callstack_frame.f_code.co_name)
        callstack_frame = callstack_frame.f_back

    current_frame.f_locals["__callstack__"] = list(reversed(accum))

    current_frame.f_locals["__lineno__"] = current_frame.f_lineno

    # current_frame.f_locals["__scope__"] = current_frame.f_code.co_name

    current_frame.f_locals["__event__"] = event

    try:
        filename = current_frame.f_code.co_filename
        lineno = current_frame.f_lineno
        current_line = linecache.getline(filename, lineno)
        source = current_line.strip()
    except Exception:
        source = None
    current_frame.f_locals["__source__"] = source

    if event == "return":
        current_frame.f_locals["__returnval__"] = arg
    else:
        current_frame.f_locals["__returnval__"] = None

    if event == "exception":
        current_frame.f_locals["__exception__"] = arg[1]
    else:
        current_frame.f_locals["__exception__"] = None


def show_banner():
    from seapie import __version__ as version  # Avoid circular import at startup.
    if hasattr(sys, "ps1"):
        print("Warning: using seapie outside of scripts can cause undefined behaviour.")
    print(f'Starting seapie {version} on {platform.system()}. Type "!h" for help.')


def mimic_traceback(frame, frames_to_hide):
    """
    mimics interactive interpreter traceback print but hides seapie

    if exception occurs in seapie, frames_to_hide tells how many seapie
    relatd frames to hide from the traceback found in exception.
    this is joined with other frames found with tb.extact_stack to show
    all frames from original source and frames from input but not seape itself
    frames to hide is how many frames to hide from the middle of traceback to hdie
    seapie
    """

    traceback_exc = traceback.TracebackException(*sys.exc_info())

    # seapie would be present here so we hide it from the middle of the stack
    # Exclude the frames occupied by the debugger
    tb_exc_stack_filtered = traceback_exc.stack[frames_to_hide:]

    # we have to use both traceback.extract_stack(frame) and
    # traceback_exc.stack
    # because otherwise frames created in seapie repl would not be visible
    # or frames created in original source would not be visible
    tb_frames = traceback.extract_stack(frame) + tb_exc_stack_filtered

    # Format the filtered traceback
    formatted_traceback = "".join(traceback.format_list(tb_frames))

    print("Traceback (most recent call last):")  # Print header.
    print(formatted_traceback, end="")  # Print traceback,

    exc_type, exc_val, _exc_tb = sys.exc_info()  # Get active exception if any.
    if exc_type is not None and exc_val is not None:  # Print active exception.
        if str(exc_val):  # str casting is necessary for correct truth checking.
            print(f"{exc_type.__name__}: {exc_val}", file=sys.stderr)
        else:
            print(exc_type.__name__, file=sys.stderr)
