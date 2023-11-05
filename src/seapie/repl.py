#!/usr/bin/env python3

import codeop
import ctypes
import sys
from .version import seapie_ver

# These can be set to anything
PS1 = ">>> "  # Allows customizing sys.ps1 equivalent for seapie.
PS2 = "... "  # Allows customizing sys.ps2 equivalent for seapie.


def repl_input(pre_ps1, pre_ps2):
    """Fake python repl until we can return meaningful code.
    ja voi antaa keybardintteruptin tai eof errorin valua esiin
    tämö funktio lupaa palauttaa jotain, mutta se jokin voi nostaa herjan
    lupaa myös että lukemista ei lopeteta liian aikaisin
    bangs are case insensitive
    mutable defaults trickery alert

    always returns str, compiling is done later by the receiver.
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
            line = input(f"{pre_ps1}{PS1}" if not lines else f"{pre_ps2}{PS2}")
        except (EOFError, KeyboardInterrupt) as e:
            # If input causes an error, it likely wont print a newline.
            # silently print newlie manually to make everything behave like
            # the normal interpreter and then reraise from None to hide part
            # of the traceback. it is important that the raising happens in
            # this module. so that this module can be hidden when printing
            # traceback later
            print()
            raise type(e) from None

        if line.startswith("!") and not lines:
            return line

        # Lines should not have trailing newlines so newlines are added BEFORE
        # the input text for all but the first line.
        lines.append(line)

        # none returned for partial but ok code. could also raise. tässä
        # täytyy olla "string" että sama kuin execillä
        try:
            entry = "\n".join(lines)  # todo: selitä string ja single valinta
            if codeop.compile_command(entry, "<string>", "single") is not None:
                return entry
        except (SyntaxError, ValueError, OverflowError) as e:
            raise type(e) from None  # todo: onko tää oikein? rereaise none?


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

    match event:
        case "call":  # arg is None.
            caller_name = frame.f_back.f_code.co_name
            callee_name = frame.f_code.co_name
            pre_ps1 = f"call {caller_name} → {callee_name} "
            pre_ps2 = f"call {caller_name} → {callee_name} "
        case "line":  # arg is None
            pre_ps1 = f"line# {frame.f_lineno} "
            pre_ps2 = f"line# {frame.f_lineno} "
        case "return":  # arg is the value that will be returned, None if raising.
            caller_name = frame.f_back.f_code.co_name
            callee_name = frame.f_code.co_name
            pre_ps1 = f"return {caller_name} ← {callee_name} "
            pre_ps2 = f"return {caller_name} ← {callee_name} "
            # switch = f"returning {object.__repr__(arg)}."
        case "exception":  # arg is (exception, value, traceback
            pre_ps1 = "error "
            pre_ps2 = "error "
            print(arg)
            # switch = f"raising {arg[0].__name__}."
        case _:
            pre_ps1 = "unknown "
            pre_ps2 = "unknown "

    pre_ps1 = pre_ps1.ljust(20)
    pre_ps2 = pre_ps2.ljust(20)

    # sys.stdout.write("\033[s")  # Save the current cursor position
    # sys.stdout.write(f"\033[{0};{0}H")  # Move the cursor to position

    sys.stdout.write("\033[7m")  # Set the text to inverted mode
    # Print text with inverted colors
    print()
    print("Inverted Text")
    sys.stdout.write("\033[0m")  # Reset to default text attributes

    sys.stdout.write("\033[A")
    sys.stdout.write("\033[A")

    # sys.stdout.write("\033[u")

    # print(
    #    f"Next: line {frame.f_lineno} in {frame.f_code.co_name} at "
    #    f"{os.path.basename((frame.f_code.co_filename))}, {switch}"
    #    )

    while True:
        user_input = repl_input(pre_ps1, pre_ps2)
        if user_input == "!s":
            break
        if user_input == "!q":
            sys.stdout.write("\033[?1049h")  # alternate buffer
            sys.stdout.write("\033[?1049l")  # leave alternate buffer
            exit()

        repl_exec(frame, user_input)

    return repl_loop


def breakpoint():
    """starts traving if trace func is none. if trace func is repl_llop
    this call does nothing. if trace func is something else raise.
    """
    if (trace := sys.gettrace()) is None:
        pyver = (
            f"{sys.version_info.major}."
            f"{sys.version_info.minor}."
            f"{sys.version_info.micro}"
        )

        print()
        print(f"Seapie {seapie_ver} repl running on Python {pyver} on {sys.platform}")
        print("""Type "!help" for more information.""")
        print()
        print("Current event being traced is shown here")
        print("  |")
        print("  |")
        print("  V")

        sys.settrace(repl_loop)  # Tracing would start on next traceable event.
        sys._getframe(1).f_trace = repl_loop  # Start tracing now instead.
    elif trace is not repl_loop:
        msg = (
            "Trace function was already set by some other tool. Use"
            " sys.gettrace() or sys.settrace(None) to inspect or clear it."
        )
        raise RuntimeError(msg)
    else:
        pass  # Seapie was already tracing.
