#!/usr/bin/env python3


import codeop
import ctypes
import sys
from .version import seapie_ver
from .status import print_status_bar, get_status
from .bang import bang_handler, print_tb

# These can be set to anything
PS1 = ">>> "  # Allows customizing sys.ps1 equivalent for seapie.
PS2 = "... "  # Allows customizing sys.ps2 equivalent for seapie.

# State that will persist over different calls to prompt().
# These settings can be modified by anyone anywhere. they are not passed as
# arguments.
CURRENT_SETTINGS = {"show_bar": True}


def repl_input(frame):
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
            print_tb(frame, num_frames_to_hide=4)
            # hiding: repl_input, codeop.compile_command, codeop._maybe_compile, codeop._compile
            lines = []
            continue
            # return entry  # anna tarkoituksella mennä läpi, exec hajoaa


def repl_exec(frame, source):
    """str representing python sauce. and compiles it. assume that the code is

    performs exec in arbitrary frame and attempts to modify its state like
    interactive interpreter would
    """
    # todo: miksi str ja single
    compiled_code = codeop.compile_command(source, "<string>", "single")
    # nää asetukset saa execin toimimaan ja myös prittaamaan niinkuin repl

    # dont save compiled to code as compilation failed. code remains str

    exec(compiled_code, frame.f_globals, frame.f_locals)

    # This c lvel calls allows use to arbitarily change the variables in the
    # frame including introducing new ones.
    # todo: dokumentoi magic constant c_int 1
    # the magic value 1 tells the function to clear local variables so that
    # the changes are found when referring to variable as x instead of only
    # frame.x
    c_frame = ctypes.py_object(frame)
    c_int1 = ctypes.c_int(1)
    ctypes.pythonapi.PyFrame_LocalsToFast(c_frame, c_int1)


def repl_print():
    """Poista tää kaikista importeista myös"""
    pass


def repl_loop(frame, event, arg):
    """read-evaluate-print-loop that gets called when tracing code. this
    basically gets run between evey line

    * repl_input
    * repl_exec # also does printing if necessary
    * loop back to start in while true

    always returns repl_loop itself so it will be used for both local and
    global tracing. under the hood the return value is ignored or used to set
    local trace function depending on the event.
    """

    # Unhandled exception happened in orginal source code
    # guard tracing into error handling mechanism
    # stop tracing on exception. there is no use in tracing the internal error handling logic.
    if hasattr(sys, "last_traceback"):
        frame.f_trace = None
        sys.settrace(None)
        return

    while True:
        # status
        print_status_bar(get_status(frame, event))

        # read

        user_input = repl_input(frame)

        next_action = bang_handler(user_input, frame)
        if next_action == "step-with-repl":  # step source, reopen repl
            return repl_loop
        elif next_action == "step-without-repl":  # step source, disabe trace
            return None
        elif next_action == "continue-in-repl":  # don't step, continue this repl
            continue
        else:
            pass  # got code

        # evaluate
        try:
            repl_exec(frame, user_input)
        except SystemExit:  # Separate exit before catching base exception.
            exit()
        except BaseException:
            print_tb(frame, num_frames_to_hide=3)  # Seapie occupies 3 frames here.
            # the frames are repl-loop, repl-exec, <string> from exec()
            continue

        # loop


def prompt():
    """
    the name might be confusing . this function is not the prompt itself but
    sets the system trace function >repl_loop< which acts like the prompt when
    set as the trace function.

    starts traving if trace func is none. if trace func is repl_llop
    this call does nothing. if trace func is something else raise.
    """
    if (trace := sys.gettrace()) is None:
        pyver = (
            f"{sys.version_info.major}."
            f"{sys.version_info.minor}."
            f"{sys.version_info.micro}"
        )
        print(
            f"Stopped on breakpoint. Seapie {seapie_ver} running on Python {pyver} on {sys.platform}."
        )
        print("Type '!help' for help menu. See status bar at the top for info.")
        sys.settrace(repl_loop)  # Tracing would start on next traceable event.
        sys._getframe(1).f_trace = repl_loop  # Start tracing now instead.
    elif trace is not repl_loop:
        msg = (
            "Trace function was already set by some other tool. Use"
            " sys.gettrace() or sys.settrace(None) to inspect or clear it."
        )
        raise RuntimeError(msg)
    else:
        pass  # seapie already tracing
