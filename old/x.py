#!/usr/bin/env python3

# verified for 3.10. python saw significant changes to how interpreter parsing and lexing etc works between [seapie 2 patch date] release and 3.10 https://github.com/python/cpython/issues/90679

import os
from os import get_terminal_size
import sys
import traceback
from codeop import compile_command
import ctypes
import inspect
from textwrap import indent
from itertools import count
import linecache

max_w = lambda: get_terminal_size().columns


class Trace:
    """asd asdas da dad ad asd"""

    print_info_when_stepping = True
    steps_left = 0
    until_target = None
    repeat_with_kbint = False

    should_step = False
    should_stop_tracing = False

    latest_input = "None"
    saved_input = "None"

    def __init__(self):
        Trace.instance = self
        Trace.__new__ = lambda _class: Trace.instance

    def fetch_latest_input(self):
        """Fake python repl until function can return meaningful code.
        ja voi antaa keybardintteruptin tai eof errorin valua esiin
        tämö funktio lupaa palauttaa jotain, mutta se jokin voi nostaa herjan
        lupaa myös että lukemista ei lopeteta liian aikaisin
        bangs are case insensitive
        mutable defaults trickery alert
        """
        lines = ""
        for (
            i
        ) in (
            count()
        ):  # read input until it is completed or fails or is detexted to be a bang
            try:
                line = input("..... " if lines else ">>>>> ")
                lines += line if not lines else f"\n{line}"
                if line.startswith("!") and i == 0:
                    break  # got banged
                if (
                    compile_command(lines, "<string>", "single") is not None
                ):  # none returned for partial but ok code. could also raise. tässä täytyy olla "string" että sama kuin execillä
                    break  # return the uncompiled. allow exec to compile later so that allr eturn values from here are strs
            except (
                KeyboardInterrupt
            ) as e:  # raised by input # If input causes an error, it likely wont print a newline. silently print it manually to make everythiing formatted uniformly. then reraise.
                if self.repeat_with_kbint:
                    print(
                        "KeyboardInterrupt: repeating saved input"
                    )  # tässä kans se printin sliceeminen?
                    print(indent(self.saved_input, "      "))
                    self.latest_input = self.saved_input
                    # break
                    return
                print()
                raise type(
                    e
                ) from None  # reraise from none to hide part of traceback. it is ok to lose any extra info for these exceptions by raising from none
                # it is important that the raising happens in this module. so that this module
                # can be hidden when printing traceback later
            except EOFError as e:  # raised by input
                print()  # If input causes an error, it likely wont print a newline. silently print it manually to make everythiing formatted uniformly. then reraise.
                raise type(
                    e
                ) from None  # reraise from none to hide part of traceback. it is ok to lose any extra info for these exceptions by raising from none
                # it is important that the raising happens in this module. so that this module
                # can be hidden when printing traceback later
            except (
                SyntaxError,
                ValueError,
                OverflowError,
            ) as e:  # invalid literal # raised by compile
                break
        self.latest_input = lines
        if lines:
            self.saved_input = lines

    def bang_handler(self, frame):
        """returns None if repl should continue without stepping
        returns True if repl should step
        returns false if repl should quit (tracing stopped)

        bang defautls to empty string so that using 'raise Bang' will not crash
        extra args are ignored from bang errors. only first one is parsed
        all args and kwargs are inorex except for the first one which is None by default
        """
        bang = self.latest_input
        try:
            assert type(bang) == str  # is now now a string
            assert len(bang) >= 2  # is a string, can check lenght, is now "xx_"
            assert bang[0] == "!"  # is now "!x_" or longer
            assert bang.count(" ") in (0, 1)  # is now "!x_" or "!x_ _"

            if len(_bang := bang.lower()[1:].split(" ")) == 1:
                bang_name, bang_arg = _bang[0], None
            else:
                bang_name, bang_arg = _bang[0], int(_bang[1])
                assert bang_arg >= 0
        except (AssertionError, ValueError):  # valuerror from int conversion
            print("Bang must be a string in the format: '!<bangname> [integer]'.")
            return

        try:
            if "step".startswith(bang_name):
                # assert bang_arg is None
                self.should_step = True
                if bang_arg is not None:
                    self.steps_left = bang_arg
            # elif "walk".startswith(bang_name):
            #    assert bang_arg is not None
            #    self.walking_counter = bang_arg
            elif "until".startswith(bang_name):
                assert bang_arg is not None
                self.until_target = bang_arg
            elif "continue".startswith(bang_name):
                assert bang_arg is None
                frame.f_trace = None  # clear global trace
                sys.settrace(None)  # clear local trace
                print("Tracing stopped. Trace function cleared")
                self.should_stop_tracing = True
            elif "quit".startswith(bang_name) or "exit".startswith(bang_name):
                assert bang_arg is None
                exit()
            elif "repeat".startswith(bang_name):
                assert bang_arg is None
                self.repeat_with_kbint = not self.repeat_with_kbint
                print("Repeat set to", self.repeat_with_kbint)
            elif "help".startswith(bang_name):
                assert bang_arg is None
                print("help here ayooooo.")
            elif "variables".startswith(bang_name) or "vars".startswith(bang_name):
                assert bang_arg is None
                if frame.f_locals.keys() == frame.f_globals.keys():
                    print("Global and local variables:")
                    print("    ".join(frame.f_locals.keys()))
                else:
                    print("Global variables:")
                    print("    ".join(frame.f_globals.keys()))
                    print("Local variables:")
                    print("    ".join(frame.f_locals.keys()))
            elif "jump".startswith(bang_name):
                assert bang_arg is not None
                try:
                    frame.f_lineno = bang_arg
                except ValueError as e:
                    print("Jump failed:", str(e))
                else:
                    print("Jump succeeded. Next line to execute is", bang_arg)
            # elif "verbosity".startswith(bang_name):
            #    assert bang_arg is None
            #    self.print_info_when_stepping = not self.print_info_when_stepping
            #    print("Verbosity changed.")
            elif "traceback".startswith(bang_name):
                assert bang_arg is None
                traceback_exc = traceback.TracebackException(*sys.exc_info())
                # tämä lupaa piilottaa kaiken tästä moduulista, eli mikään mitä täältä moduulista kutsutaan ei saa nostaa itse herjaa tai se tulee näkyville!
                stack = (
                    traceback.extract_stack(frame) + traceback_exc.stack
                )  # add frames from prog
                stack = [
                    framesummary
                    for framesummary in stack
                    if framesummary.filename != inspect.getfile(Trace)
                ]  # hide debugger
                traceback_exc.stack = traceback.StackSummary(stack)
                if sys.exc_info() == (None, None, None):
                    print(
                        "".join(list(traceback_exc.format())[:-1])[:-1]
                    )  # slice "None: None" from print and slice newline
                else:
                    print("".join(traceback_exc.format())[:-1])
            elif "where".startswith(bang_name):
                assert bang_arg is None
                try:
                    filename = inspect.getfile(frame)
                except Exception as e:
                    print(f"Failed to fetch source filename: {repr(str(e))}.")
                else:
                    max_pad = len(str(frame.f_lineno + 5))
                    for i in range(frame.f_lineno - 5, frame.f_lineno + 5):
                        # getline returns "" for empty lines. otherwise lines
                        # will include a newline
                        if i == frame.f_lineno:
                            print("►")
                        if (line := linecache.getline(filename, i)) != "":
                            printable = f"  {str(i).rjust(max_pad)} {line}".rstrip()
                            if (diff := len(printable) - max_w()) > 0:
                                printable = (
                                    printable[: -diff - 3] + "..."
                                )  # hide extra. replace with ...
                            print(printable)
            elif "frame".startswith(bang_name):
                assert bang_arg is None
                frame.f_globals["FRAME"] = frame
                print(
                    "Global variable 'FRAME' has been added. Remember to 'del FRAME' afterwards to avoid reference cycles."
                )
            else:
                print("Unknown bang.")
                # case "frame": # temporarily inject the frame variable into locals
                # case up
                # case down
                # case where
        except AssertionError:
            print("Incorrect number of arguments given for the bang used.")
        except Exception as e:
            print(f"Bang failed unexpectedly: {repr(str(e))}.")

    def true_exec(self, frame):
        "str representing python sauce. and compiles it. assume that the code is"
        code = self.latest_input
        try:
            compiled_code = compile_command(code, "<string>", "single")
        except (SyntaxError, ValueError, OverflowError):
            # dont save compiled to code as compilation failed. code remains str
            pass  # invalid literal found in compiling. ignore the errors in compiling. compiling should not raise anything else than this.
            # and allow exec to raise. exec will raise on the correct level which (this module) and makes it easy to hdie it later
        else:  # save compiled to code. its no longer string this guarantees that expressions are printed since it was compiled as single.
            # giving str to exec in the other case does not matter; it will merely raise so there is no xpression to print
            code = compiled_code

        if frame.f_globals == frame.f_locals:  # bottom frame aka global frame
            exec(
                code, frame.f_globals, frame.f_locals
            )  # TODO: dokumentoi että globaaleihin ylikirjoteaan lokaalit.
        else:
            # inject locals to globals to allow for list comprehensions work
            # like [asd[0] for i in asd] where asd was defined in original code

            # TÄMÄ PAKOTTAA KAIKKI MUUTOKSET SIIRTYMÄÄN MUKANA. MYÖS KAIKKI TULEVAT!
            frame.f_globals.update(frame.f_locals)
            exec(
                code, frame.f_globals, frame.f_locals
            )  # TODO: dokumentoi että globaaleihin ylikirjoteaan lokaalit. voi ehkä vaikuttaa nonlocal tai global tjsp kw
            # exec(code, frame.f_globals | frame.f_locals, frame.f_locals) # TODO: dokumentoi että globaaleihin ylikirjoteaan lokaalit. voi ehkä vaikuttaa nonlocal tai global tjsp kw
            # exec(code, {}, frame.f_globals | frame.f_locals) # TODO: dokumentoi että globaaleihin ylikirjoteaan lokaalit. voi ehkä vaikuttaa nonlocal tai global tjsp kw

        # tämä korjaa list comprehension ongelman jossa aiemmin [asd[0] for i in asd] ei toimi jos asd määritelty sorsassa.
        # mutta joissain tilanteissa koodi mikä tutkii globalsia ja localsia interaktiivisessa sessiossa debugerissa voi kusta.
        # mutta normaalisti ei ongelma koska locals lookup tulee ensin.
        # This c lvel calls allows use to arbitarily change the variables in the frame including introducing new ones.
        ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(1))
        # eg:
        # foo=1
        # breakpoint()# value of foo changed to 2

    @staticmethod
    def __call__(
        frame, event, arg
    ):  # this was previously _trace ! this is the main repl loop!
        """only one trace function is used for global and local tracing"""
        self = (
            Trace.instance
        )  # create self manually since trace function should have the signature frame, event, arg

        # guard tracing self
        if frame.f_code.co_filename == inspect.getfile(
            Trace
        ):  # do not trace anything in this module. do not show it in errors.
            # linkittyikö tää siihen että voi olla monta breakpoint peräkkäin? tarkista.
            # tai ehkä liitty siihen että loopis kutsuu bk?
            return self

        # guard tracing into error handling mechanism
        if hasattr(
            sys, "last_traceback"
        ):  # Unhandled exception happened in orginal source code
            frame.f_trace = None  # stop tracing on exception. there is no use in tracing the internal error handling logic.
            sys.settrace(None)
            return  # attempt to stop tracing by also returning no new trace func

        # show info every time code was stepped
        if self.print_info_when_stepping:
            match event:
                case "call":
                    switch = "entering scope."
                case "line":
                    switch = "executing line."
                case "return":
                    switch = f"returning {object.__repr__(arg)}."
                case "exception":
                    switch = f"raising {arg[0].__name__}."
                case _:
                    raise NotImplementedError(f"Unsupported tracing event: {event}")
            print(
                f"Next: line {frame.f_lineno} in {frame.f_code.co_name} at "
                f"{os.path.basename((frame.f_code.co_filename))}, {switch}"
            )

        # this is the main repl loop that is triggered between original source lines
        while True:
            try:
                if self.steps_left > 0:
                    self.steps_left -= 1
                    self.latest_input = "!step"
                else:
                    self.fetch_latest_input()  # can raise kbi and eofe
                # elif (target_lineno := settings["until_target"]) is not None:
                #    if frame.f_lineno != target_lineno:
                #        raise BangInterrupt("!step")
                #    else:
                #        settings["until_target"] = None # quarantee one extra step
                #        raise BangInterrupt("!step")

                if self.latest_input.startswith("!"):
                    self.bang_handler(frame)
                else:
                    self.true_exec(frame)  # can raise anything
            except (
                SystemExit
            ):  # gotta separate systemexit before catching base exception
                exit()
            except (
                BaseException
            ):  # kb+eof from input # BaseException would also catch SystemExit and BaseExceptionGroup. list exceptions manually
                self.latest_input = "!traceback"
                self.bang_handler(frame)
            if self.should_stop_tracing:
                self.should_stop_tracing = False
                return
            if self.should_step:
                self.should_step = False
                return self


trace = Trace()  # the singleton is now instanced. There is no other references to it.


def set_trace():
    if (
        sys.gettrace() is trace
    ):  # trace already set. # do not trace anything in this module. do not show it in errors.
        print("XXX already tracing. Ignoring breakpoint.")
        return
    banner_text = "┤ xxx starting trace. use !help for help ├"
    pad_width = (max_w() - len(banner_text)) // 2
    print(f"{'─'*pad_width}{banner_text}{'─'*pad_width}")
    sys.settrace(trace)  # activate tracing. it will trigger on next traceable event
    sys._getframe(
        1
    ).f_trace = (
        trace  # us _getframe is ok. we depend on c python for exec in frame anyways.
    )
    # but we do not activate tracing in this functions frame because there is no need for it


if __name__ == "__main__":
    print("Did you mean to import XXX instead of running it?")
else:
    print(
        "xxx.set_breakpointhook was called automatically on import. breakpoint() will now trigger xxx."
    )
    # print("Setting PYTHONBREAKPOINT environment variable to XXX.set_trace(). Calling breakpoint() will now use XXX.set_trace() instead of pdb.set_trace()")
    os.environ["PYTHONBREAKPOINT"] = "xxx.set_trace"
    sys.breakpointhook = set_trace  # remove this in prod !!! XXX TODO
    try:  # fix console input on linux. use try since modile is not available on windows.
        import readline
    except ModuleNotFoundError:
        pass

# joka bängin pitää antaa feedback. tutki kaikkien printien leveys
# PAKOTA PRINTTI PPRINTIKSI INTERPRETERISSÄ? TAI EXECIN BUILTINISSÄ?
# pitääkö breakpoinin ignoraaminen kuuluttaa?
# global framessa kaikki toimii
# locals framess et voi def lol(): lol() ja rekursoida mutta voi silti lista koska local inject global
# BANGI ARGUMENTIN CHEKKAUS PITÄIS OLLA INPUTISSA. ??
# joku komento breakpointtien? ignoraamiselle?
# continuen vastine mikä tracettaa ja lopettaa kun sejatämä?
# tämän tracingin infoprinteille joku oma tyyli? muuten walk menee sotkuun kaiekn muun kanssa mitä vois printtaa source
# joku erityinen post mortem työkalu?
# pin value/expression (ja unpin?)
# default settings palautus?
# ominaisuus että steppaa eventtien mukaan? vai onko turhaa koska lineno toimii?
# mutta ei voi kyl tracee ilman linenoa jos ei oo tarjol
# dokumetoi että repeatin ctrl+c nappaa VAIN input promptin ctrl+c
# skoopin highlightaus kun antaa !t ja samalla myös stack walk. pitäiskö inputin antaa katsoa kans
# settingseihin tjsp? main loop olis siistimpi
# ja sen lisäksi where näyttämään source linet
# rivi 160 ja up/down. ja settings vois olla ehkä luoka ominaisuus. siivoais myös mutable defaultit.
# !t pitäis näyttää missä framessa oot
# !where rivin pituuden leikaaminen puuttuu
# locals ja globals vois näytää vaa nimet nii ei floodaaaaa
# ehkä !step:in sijaan joku step in file ja step into? pitäis pystyä heittään se kiinni johonki black boxiin kuten siilo

# bang handlerin lisäksi pitää tehä joku settings handler niin ei oo sekalaista purkkaa että joskus
# inputti korvautuu bangillä itekseen

# Nopdb
# not pdb
# notbpd

# joku info missä näkyy mikä python interpreter käytössä?
