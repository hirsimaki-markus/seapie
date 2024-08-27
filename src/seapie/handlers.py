"""
bang handler stuff and related tools
"""

import ctypes
import inspect
import linecache
import os
import sys
import types

import seapie.helpers
import seapie.repl


def handle_input(frame, event, arg, user_input):
    # quit, run, help, info, step, where, up, down, frame, traceback, goto
    bang_map = {func.__name__: func for func in [q, r, h, i, s, w, u, d, f, t, g]}

    if isinstance(user_input, types.CodeType):
        exec(user_input, frame.f_globals, frame.f_locals)
        ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(1))
    else:
        bang_name, *trail = user_input[1:].split()  # Drop "!" with [1:].
        if len(trail) in (0, 1):
            bang = bang_map.get(bang_name.lower(), lambda *_: print(f"Invalid bang {repr(bang_name)}"))
            bang_arg = trail[0] if trail else None

            if bang_arg is not None and bang in [q, r, h, i, s, w, u, d, f, t]:
                print(f"This bang can't accept an argument. Usage: !{bang_name}")
                raise seapie.helpers.Continue
            if bang_arg is None and bang in [g]:
                print(f"This bang requires an argument. Usage: !{bang_name} arg")
                raise seapie.helpers.Continue

            bang(frame, event, arg, bang_arg)
        else:
            print("Bangs can have up to one argument. Got", len(trail))

    raise seapie.helpers.Continue



def f(working_frame, _event, _arg, _bang_arg):
    """Add reference to base frame locals. The frame added is the one
    currently operated on by interpeter."""
    working_frame.f_locals["__frame__"] = working_frame
    print(
        "Added local variable __frame__ to current frame. Remember to delete"
        " the reference with 'del __frame__' when you are done with the frame"
        " to avoid circular references or memory leaks."
    )


def g(frame, _event, _arg, bang_arg):
    """Wohoo. goto in python."""
    try:
        frame.f_lineno = int(bang_arg)
    except Exception as e:
        print("Goto failed:", str(e))
    else:
        print("Goto succeeded. Next line to execute is", bang_arg)




def s(_frame, _event, _arg, _bang_arg):
    # todo: voi steppaa miten sattuu koska callstack escape lvlei enää käytös
    raise seapie.helpers.Step  # step, dont update current working frame since trace fucnction is called again and gets a new frame

def r(frame, _event, _arg, _bang_arg):
    frame.f_trace = None
    sys.settrace(None)
    raise seapie.helpers.Step


def h(_frame, _event, _arg, _bang_arg):
    print("nice")


def q(_frame, _event, _arg, _bang_arg):
    exit()





def i(frame, event, arg, _bang_arg):
    def get_status(frame, event, arg):
        """Creates a status string based on a given frame and event(str)

        list of lines to use as status

        """
        lines = []
        sep = "  │  "  # This is not the same symbol as |

        # get variables to use in lines

        # not using the first line below this comment because it could differ from
        # __file__
        # filename = frame.f_code.co_filename or "None"
        filename = frame.f_globals.get("__file__", "None")

        # scope = repr(frame.f_code.co_name) or "None"

        # 0 callstack
        accum = []
        callstack_frame = frame
        while callstack_frame:
            accum.append(callstack_frame.f_code.co_name)
            callstack_frame = callstack_frame.f_back
        lines.append(f"callstack: {repr(list((reversed(accum))))}")

        # get lines 1-3
        lines.append(f"file: {repr(filename)}")  # 1

        try:  # 2
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno
            current_line = repr(linecache.getline(filename, lineno).strip())
        except Exception:
            current_line = repr(None)
        lines.append(f"lineno: {frame.f_lineno}{sep}source: {current_line}")

        if event == "return":  # 3
            retval = repr(arg)
            exception = repr(None)
        elif event == "exception":
            retval = repr(None)
            exception = repr(arg[1])
        else:
            retval = repr(None)
            exception = repr(None)
        lines.append(
            f"event: {repr(event)}{sep}retval: {retval}{sep}exception: {exception}"
        )

        return lines

    print("\n".join(get_status(frame, event, arg)))


def w(frame, _event, _arg, _bang_arg):
    """Reponds to term size

    it might be possible to make this fail?
    """
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
    if max_lineno_width < 6:
        max_lineno_width = 6  # the string ' Next ' is 6 character

    for lineno, line in enumerate(lines, start=1):
        line = line[:-1]  # Remove trailing newline with -1
        linenum = str(lineno).rjust(max_lineno_width)  # right aling lineno
        if abs(lineno - current_lineno) <= 10:  # show +- 10 lines.
            if lineno != current_lineno:
                out = f"{linenum} {line}"
            else:
                out = (
                    f"{invert_color}{' Next '.rjust(max_lineno_width)}"
                    f"{reset_color} {line}"
                )
            # invert color and reset color lenghts are added to width since
            # they are invisible and dont actually take up space
            out = out[:width]

            print(out)


def u(frame, _event, _arg, _bang_arg):
    upper_frame = frame.f_back
    if upper_frame is not None:
        print(f"Current working frame will be {repr(upper_frame.f_code.co_name)}")
        # update the frame in repl loop in hacky way to keep all bangs folloing the same
        # style: they cause side effects and return nothing.
        repl_f = sys._getframe(2)
        repl_f.f_locals["frame"] = upper_frame
        ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(repl_f), ctypes.c_int(1))
    else:
        print("Not enough frames in callstack to move higher!")



def d(frame, _event, _arg, _bang_arg):
    # Get full stack of frames.
    i = inspect.currentframe() # maybe use inspetct.stack?
    stack = []
    while i is not None:
        stack.append(i)
        i = i.f_back
    stack = stack[3:] # drop seapie frames

    # find lower frame
    for i in stack:
        #print(frame)
        if i.f_back == frame:
            lower_frame = i
            break
        else:
            lower_frame = None

    if lower_frame is not None:
        print(f"Current working frame will be {repr(lower_frame.f_code.co_name)}")
        # update the frame in repl loop in hacky way to keep all bangs folloing the same
        # style: they cause side effects and return nothing.
        repl_f = sys._getframe(2)
        repl_f.f_locals["frame"] = lower_frame
        ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(repl_f), ctypes.c_int(1))
    else:
        print("Not enough frames in callstack to move lower!")

def t(frame, _event, _arg, _bang_arg):
    seapie.helpers.mimic_traceback(frame, frames_to_hide=0)  # no ongoign exception, arg doesnt matter?