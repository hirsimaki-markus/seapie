#!/usr/bin/env python3

"""the only function you should use from here is prompt.

there is global state and everything is monolitchic to simplify the structure
of the debugger; the amount of argument passing is reduced and there is no
need for a class. The top priority was to simlify prompt() and repl_loop()

dokumentoi mihin tarkoitukseen seapie directory on
"""

import codeop
import ctypes
import inspect
import sys

from .bang import bang_handler, do_tb
from .helpers import (
    check_rw_access,
    escape_frame,
    init_seapie_dir_and_reset_state,
    print_start_banner,
    step_until_condition,
    update_magic_vars,
)
from .state import __STATE__, STATE
from .status import update_status_bar
from .version import ver

LIPPU = False

# These can be set to anything
PS1 = ">>> "  # Allows customizing sys.ps1 equivalent for seapie.
PS2 = "... "  # Allows customizing sys.ps2 equivalent for seapie.


def get_repl_input(frame):
    """Fake python repl until we can return meaningful code.
    ja voi antaa keybardintteruptin tai eof errorin valua esiin
    tämö funktio lupaa palauttaa jotain, mutta se jokin voi nostaa herjan
    lupaa myös että lukemista ei lopeteta liian aikaisin
    bangs are case insensitive
    mutable defaults trickery alert

    always returns str, compiling is done later by the receiver.

    returned str might cause error when compiling.

    uus: can raise: eoferror, kbinterrupt. these mut be caught in repl loop.
    uusin: this funktin shoul never raise so error handling is easier
    in the rest of the repl

    the prompt provided will look like one of these:

    1 >>>


    2 >>>
    ...
    ...


    3 >>>
    KeyboardInterrupt
    >>>

    4 >>>
    (exit due to eof)


    frame is required as argument to correcly print traceback if needed

    this function prints tracebacks instead of raising to make repl loop
    cleaner
    """

    # Check if previous bang should be echoed instead of reading te user input.
    if STATE["echo_count"] > 0:
        STATE["echo_count"] -= 1
        return STATE["previous_bang"]

    # Readline is required on systems where it is available to make the input
    # behave properly when using non-printable key presses like arrow keys.
    # Notably, readline is not available on Windows.
    try:
        import readline  # noqa: F401  # Ignore unused import in flake8.
    except ImportError:
        pass

    lines = []
    while True:  # read input until it is completed or fails or we get a bang
        try:
            line = input(PS1 if not lines else PS2)
        except KeyboardInterrupt:  # ctrl+c
            print("\nKeyboardInterrupt")
            lines = []
            continue
        except EOFError:  # ctrl+d or ctrl+z
            print()
            exit()
        except ValueError:
            # I/O operation on closed file. rarely happens when seapie
            # prompt is being reopened?
            print(
                "\nFailed to read from stdin with input(). Was there another"
                " breakpoint after try-except in which you called !e or exit()"
                " during an exception event? If that was the cause, use"
                " os._exit(0) instead."
            )
            # one way to cause this is to step into try-except block and
            # exit() during exception event while there is new breakpoint
            # below the try-except. exit() takes a moment to propagate. use !q
            # instead.
            exit()

        if line.startswith("!") and not lines:
            return line

        # Lines should not have trailing newlines so newlines are added BEFORE
        # the input text for all but the first line.
        lines.append(line)

        # none returned for partial but ok code. could also raise. tässä
        # täytyy olla "string" että sama kuin execillä
        try:
            entry = "\n".join(lines)  # todo: selitä string ja single valinta
            # string nimi koska exec käyttää samaa
            if codeop.compile_command(entry, "<string>", "single") is not None:
                return entry
        except (SyntaxError, ValueError, OverflowError):
            # raise type(e) from None  # todo: onko tää oikein? rereaise none?
            do_tb(frame, num_frames_to_hide=4)
            # hiding: repl_input, codeop.compile_command,
            # codeop._maybe_compile, codeop._compile
            lines = []
            continue
            # return entry  # anna tarkoituksella mennä läpi, exec hajoaa


def repl_exec(frame, source):
    """str representing python sauce. and compiles it. assume that the code is

    performs exec in arbitrary frame and attempts to modify its state like
    interactive interpreter would
    """
    # todo: miksi str ja single

    try:
        compiled_code = codeop.compile_command(source, "<string>", "single")
        exec(compiled_code, frame.f_globals, frame.f_locals)
    except SystemExit:  # Separate exit before catching base exception.
        exit()
    except BaseException:
        # Seapie occupies 2 frames here.
        # the frames are repl-exec, <string> from exec()
        do_tb(frame, num_frames_to_hide=2)

    # the magic value 1 tells the function to clear local variables so that
    # the changes are found when referring to variable as x instead of only
    # frame.x

    # This call allows seapie to overwrite stuff like functions in source.
    ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(1))


def repl_loop(frame, event, arg):
    """read-evaluate-print-loop that gets called when tracing code. this
    basically gets run between evey line

    if returning something else than none, always returns repl_loop itself so
    it will be used for both local and global trace func


    under the hood the return value is ignored or used to set
    local trace function depending on the event.

    the input and exec both have their own error handling so this main loop
    does not need error handling

    this function is essentially called between every source line

    most parts of this function use the global settings.
    """

    if hasattr(sys, "last_traceback"):  # Unhandled error in original source.
        return  # Don't return trace func to not trace Python's error handling.

    if frame.f_globals.get("prompt") is prompt:  # Dont trace new prompt calls.
        return  # Not returning a local trace function to skip seapie's frame.

    while True:  # This is the main repl (>>> ... ... ...) loop.
        current_frame = escape_frame(frame)  # Escape frame based on settings.

        update_magic_vars(current_frame, event, arg)  # Uses global settings.
        update_status_bar(current_frame, event, arg)  # Uses global settings.

        if step_until_condition(frame):  # Note: frame, not current_frame.
            return repl_loop

        if (user_input := get_repl_input(current_frame)).startswith("!"):
            if bang_handler(user_input, current_frame, event, arg):
                return repl_loop
            continue

        repl_exec(current_frame, user_input)  # All guard clauses passed; exec.


def prompt():
    """
    set_trace function

    the name might be confusing . this function is not the prompt itself but
    sets the system trace function >repl_loop< which acts like the prompt when
    set as the trace function.

    starts traving if trace func is none. if trace func is repl_llop
    this call does nothing. if trace func is something else raise.

    if not tracing:
       banner,
       init,
       Set trace function for active frame and then for all future frames.
    """
    if (trace := sys.gettrace()) is None:
        print_start_banner()
        init_seapie_dir_and_reset_state()
        inspect.currentframe().f_back.f_trace = repl_loop
        sys.settrace(repl_loop)
    elif trace is not repl_loop:
        raise RuntimeError(f"Another trace function already set: {trace}")
    else:
        print("Ignoring call to prompt() because seapie is already tracing.")
