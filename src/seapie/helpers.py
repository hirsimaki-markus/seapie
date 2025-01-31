"""helper functions that do not belong in other places"""

import builtins
import contextlib
import dataclasses
import inspect
import linecache
import os
import platform
import pprint
import shutil
import sys
import traceback
import types
import typing

import seapie.helpers
import seapie.prompt


@dataclasses.dataclass
class TraceEventInfo:
    exception: str
    lineno: int
    source: str
    event: str
    stack: typing.List[str]
    frame: types.FrameType


class Skip(BaseException):
    """Used to trigger skip in seapie repl loop."""

class Step(BaseException):
    """Used to trigger step in seapie repl loop."""

class Continue(BaseException):
    """Used to trigger continue in seapie repl loop"""

class Frame(BaseException):
    """Used to trigger ascend/descend in seapie repl loop"""


def invert(text):
    return f"\033[7m{text}\033[0m"


@contextlib.contextmanager
def handle_input_exceptions(working_f):
    """Handles possible errors produced by get_repl_input. Continue exception signals control flow to repl.
    exceptions that wont be handled: seapie control flow exceptions. maybe something else?
    """
    try:  # Code from the with statement gets executed here in yield.
        yield
    except EOFError:  # Mimic EOF behaviour from ctrl+d / ctrl+z by user in input.
        exit(print())  # Print a newline before exit. Return value doesn't get printed.
    except KeyboardInterrupt:  # Mimic kbint from ctrl+c by user in input.
        print()
        seapie.helpers.show_traceback(frames_to_hide=4)
        raise Continue
    except (SyntaxError, ValueError, OverflowError):  # Parsing fail in get_repl_input.
        seapie.helpers.show_traceback(frames_to_hide=4)
        raise Continue

@contextlib.contextmanager
def handle_exec_exceptions(working_f):
    """Handles possible errors produced by exec_input. Continue exception signals control flow to repl.
    exceptions that wont be handled: seapie control flow exceptions. maybe something else?"""
    try:  # Code from the with statement gets executed here in yield.
        yield
    except (MemoryError, SystemExit):  # Must reraise critical errors.
        raise
    except (seapie.helpers.Step, seapie.helpers.Continue, seapie.helpers.Frame):
        raise  # Allow seapie contol flow exceptions to propagate instead of catching.
    except BaseException:  # Show trace for misc. exec_input errors like invalid syntax.
        seapie.helpers.show_traceback(frames_to_hide=4)



def inject_magic_vars(frame, event, arg):
    import ctypes

    class WeakFrame:
        def __init__(self, frame):
            # Store the id of the frame (which is the memory address)
            self.frame_id = id(frame)

        def get(self):
            # Attempt to retrieve the frame using its id
            frame = ctypes.cast(self.frame_id, ctypes.py_object).value
            return frame if self._is_frame_alive(frame) else None

        def _is_frame_alive(self, frame):
            # Check if the retrieved object is indeed a frame and hasn't been replaced
            return isinstance(frame, types.FrameType)

        def __getattr__(self, attr):
            # When the WeakFrame instance is accessed, return the frame
            frame = self.get()
            if frame is None:
                raise ReferenceError("The referenced frame has been garbage collected.")
            return getattr(frame, attr)

        def __repr__(self):
            # Optional: Provide a meaningful string representation
            frame = self.get()
            return f"WeakFrame({frame})" if frame else "WeakFrame(None)"


    builtins.___ = TraceEventInfo(
        stack=[f_inf.function for f_inf in inspect.getouterframes(frame, context=1)],
        source=linecache.getline(frame.f_code.co_filename, frame.f_lineno).strip(),
        lineno=frame.f_lineno,
        event=event,
        exception=arg[0].__name__ if event == "exception" else "",
        frame=WeakFrame(frame),
    )
    linecache.clearcache()






def show_traceback(frames_to_hide):
    """inspect.stack for frames, traceback.extract_stack for formatted tb"""
    print("Traceback (most recent call last):", file=sys.stderr)
    print("".join(traceback.format_stack()[:-frames_to_hide]), end="", file=sys.stderr)
    ex_type, ex, _ex_tb = sys.exc_info() # Print the exception, if any.
    if ex_type is not None:
        print(f"{ex_type.__name__}{': ' + str(ex) if str(ex) else ''}", file=sys.stderr)

def show_callstack(frame):
    """similar to show tb but easier to read at glance, doesnt show errors."""
    print("Callstack (selected frame highlighted):")
    for frame_info in reversed(inspect.stack()[4:]):
        printable = f"<Line {frame_info.lineno} in <{frame_info.function}> at {os.path.basename(frame_info.filename)}>"[:shutil.get_terminal_size()[0]]
        if frame == frame_info.frame:
            printable = seapie.helpers.invert(printable)
        print(f"  {printable}")

def show_source(frame):
    # Print 13 source line surrounding current line
    all_lines = linecache.getlines(frame.f_code.co_filename)  # Get all source lines.
    linecache.clearcache()
    start_line = max(frame.f_lineno - 13, 1)  # Avoid negative lines with max.
    end_line = min(frame.f_lineno + 13, len(all_lines))  # min avoids lines past EOF.
    print(f"Source lines (selected frame) (next line: {frame.f_lineno}):")
    for lineno in range(start_line, end_line + 1):
        formatted_lineno = f" {str(lineno).rjust(len(str(end_line)))} "
        line_content = all_lines[lineno - 1].rstrip()
        formatted_lineno = formatted_lineno if lineno != frame.f_lineno else invert(formatted_lineno) # Mark next line.
        print(f" {formatted_lineno} {line_content}"[:shutil.get_terminal_size()[0]])


def show_info(frame, event, arg):
    print(f"Event: {event}")
    # print("Tracing information:")
    # print(f"    e: {repr(event)}")
    # if event == "exception":
    #     argument = (arg[0].__name__, str(arg[1]), "<traceback object>")
    # else:
    #     argument = repr(arg)
    # print(f"    e argument: {argument}")
    # print()


def displayhook_factory(pretty):
    """Creates a displayhook to handle _ in the prompt. Supports prettyprinting."""
    def displayhook(item):
        if item is not None:
            pprint.pp(item, width=shutil.get_terminal_size()[0]-1) if pretty else print(item)
            builtins._ = item
    return displayhook


def set_trace():
    """
    essentially equivalent of pdb.set_trace function.  set traceto repl_loop.
    """

    if sys.gettrace() is None:
        try:
            import readline  # noqa # readline (if available) needed for line editing.
        finally:
            sys.displayhook = seapie.helpers.displayhook_factory(pretty=True)

            if hasattr(sys, "ps1"):
                print("Warning: using seapie outside of scripts can cause undefined behaviour.")
            print(f'Starting seapie {seapie.__version__} on {platform.system()}. Type "!h" for help.')

            sys.settrace(seapie.prompt.repl)
            frame = sys._getframe(1)
            while frame:
                frame.f_trace = seapie.prompt.repl
                frame = frame.f_back
            # using inspect module here seems to cause unexpected behaviour
            # inspect.currentframe() returns same frame but does not work here, it doesnt seem to return immediately

