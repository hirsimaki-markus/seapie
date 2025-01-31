#!/usr/bin/env python3

"""the only function you should use from here is prompt.

there is global state and everything is monolitchic to simplify the structure
of the debugger; the amount of argument passing is reduced and there is no
need for a class. The top priority was to simlify prompt() and repl_loop()

dokumentoi mihin tarkoitukseen seapie directory on
"""

import codeop
import ctypes
import sys

import seapie.handlers
import seapie.helpers


def get_repl_input():
    """Fake python repl until we can return code as string or a bang.
    the code could cause an error when compiling and then bang  not be
    valid. The functionmight read multiple input() calls for each function call
    to mimic a python interpreter.

    no error handlnig is done here, everything is done in the enclosing repl function
    """

    lines = []
    while True:  # read input until it is completed or fails or we get a bang
        if not sys.stdin.closed:  # Check for closed status to avoid printing prompt unnecessarily when already closed
            #sys.stdin was closed > input fail > python is closing > exit().
            lines.append(input(">>> " if not lines else "... "))
        else:
            exit()

        if lines[0].startswith("!"):  # Got a bang on first line.
            return lines[0]

        compiled = codeop.compile_command("\n".join(lines), "<seapie>", "single")
        if compiled:  # "compiled" is None if "lines" was start of valid code.
            return compiled


# !help - perus helppi
# !quit - alias for exit()

# !up - kävele stäkkiä  (saisko jostain reset??) (argumentti montako framea?)
# !down - kävele stäkkiä  (saisko jostainr reset??) (argumentti montako framea?)

# !step
# !continue - sama kuin run, jatka suoritus, lopeta tracetus
# !jump - goto

# !where - tähän traceback printtaus, ehkä highlight että mikä frame valittu?
# !list - uus where (tämä ottamaan argumenttejä niinku pdb? tai joku muu tapa?)

# !to lineno (tähän argumentti toimimaan niinku pdb?) (mieluummin !to koska !up jo käytös)
# !event - return, line, exception, call


def exec_repl_input(frame, event, arg, user_input):
    if not isinstance(user_input, str):  # Input was valid python code, exec it.
        exec(user_input, frame.f_globals, frame.f_locals)
        ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(1))
        raise seapie.helpers.Continue

    bang, *bang_args = user_input[1:].lower().split(" ") # Separate bang from argument(s).
    func, needs_arg = {
        "h": (seapie.handlers.do_help, False),
        "q": (seapie.handlers.do_quit, False),

        "u": (seapie.handlers.do_up, False),
        "d": (seapie.handlers.do_down, False),

        "s": (seapie.handlers.do_step, False),
        "c": (seapie.handlers.do_continue, False),
        "j": (seapie.handlers.do_jump, True),  # true, accepts arguement

        "w": (seapie.handlers.do_where, False),
        "l": (seapie.handlers.do_list, False),
        "p": (seapie.handlers.do_prettyprint, False),


        "i": (seapie.handlers.do_info, False),

        "t": (seapie.handlers.do_to, True),
        "e": (seapie.handlers.do_event, True),
    }.get(bang, (None, None))
    if len(bang_args) not in (0, 1):
        print("Bangs can have one argument at most.")
    elif func is None:
        print(f"Invalid bang !{bang}")
    elif (len(bang_args) and not needs_arg) or (not len(bang_args) and needs_arg):
        print(f"Usage: !{bang} argument" if needs_arg else f"Usage: !{bang}")
    else:
        func(frame, event, arg, bang_args[0] if bang_args else None)
    raise seapie.helpers.Continue



def skip_handler(frame, event, arg):


    # Skip tracing certain frames.
    if hasattr(sys, "last_exc") or frame.f_code in (exit.__call__.__code__, seapie.set_trace.__code__):
        #return  # Don't trace uncaught error process, exit() process, or own breakpoint.
        raise seapie.helpers.Skip


    if not hasattr(skip_handler, "until"): # init the flag if not set already by until_bang
        skip_handler.until = None

    if skip_handler.until is not None:
        if skip_handler.until == event:
            skip_handler.until = None
        else:
            raise seapie.helpers.Skip

    #print(frame.f_lineno)



def repl(frame, event, arg):
    """args: frame, event, arg

    read-evaluate-print-loop that gets called when tracing code. this
    basically gets run between evey line

    under the hood the return value is ignored or used to set
    local trace function depending on the event.

    the input and exec both have their own error handling so this main loop
    does not need error handling

    """

    while True:  # This is the main repl (>>> ... ... ...) loop. It's triggered between every line of source code
        seapie.helpers.inject_magic_vars(frame, event, arg)
        try:

            #assert 0 # skip handler tähän,  hasattr last exc + until
            # until vois vaihtaa jotenkin skip handlerin koodit?
            # jos se funktio jotenkin "exposaa" untilille jonkin attribuutin?.
            # saako inject magic vars edes olla ennen tätä chekkiä? ehkä
            skip_handler(frame, event, arg)


            with seapie.helpers.handle_input_exceptions(frame):
                user_input = get_repl_input()  # input is either code or bang
            with seapie.helpers.handle_exec_exceptions(frame):
                exec_repl_input(frame, event, arg, user_input)
                # handlers might return a new working frame or they might raise Step. in case of raise, a f is not updated
        except seapie.helpers.Step:  # Got step signal from input or handle input
            return repl  # Steps code forward. no continue was raised.
        except seapie.helpers.Continue:  # Got continue signal from input or handle input
            continue  # keep in current repl loop, dont step code.
        except seapie.helpers.Frame as e:
            frame = e.args[0]
        except seapie.helpers.Skip:
            return


