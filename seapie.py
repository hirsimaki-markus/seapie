import sys
import ctypes
import code
import traceback
import inspect
import codeop

def seapie(scope=1):
    """Scope Escaping Arbitrary Python Injection Executor"""
    try:
        sys.ps1
    except AttributeError:
        sys.ps1 = ">>> "
    try:
        sys.ps2
    except AttributeError:
        sys.ps2 = "... "

    def single_prompt():
        """Emulates python interactive prompt to capture one complete and valid command"""
        accumulator = ""
        raw_text = ""
        while True:
            try:
                if not accumulator: # if on first line
                    raw_text = input(str(sys.ps1))
                else: # if on continuing line
                    raw_text = input(str(sys.ps2))
            except KeyboardInterrupt: # emulate behaviour of ctrl+c
                print("\nKeyboardInterrupt")
                accumulator = ""
                continue
            if accumulator == "": # if reading first line
                if raw_text == "!exit": return "!exit" # capture magic values
                if raw_text == "!scope+": return "!scope+" # capture magic values
                if raw_text == "!scope-": return "!scope-" # capture magic values
                if raw_text == "!help": return "!help" # capture magic values
                if raw_text == "!tree": return "!tree" # capture magic values
                if raw_text == "!scope": return "!scope" # capture magic values
            else:
                if raw_text == "": # this block should catch failing empty lines enterred after def and such
                    try:
                        codeop.compile_command("\n"+accumulator, "<input>", "eval")
                    except Exception as error: # catch arbitary exceptions from exec
                        traceback.print_exc()
                        accumulator = ""
                        continue
            accumulator += "\n"+raw_text # input cant read newline. add it manually

            try:
                result = code.compile_command(accumulator)
            except SyntaxError: # allow incorrect command to just pass thru
                return accumulator
            if result == None:
                pass # incomplete but possibly valid command
            else:
                return result

    print("SEAPIE v0.5 type !help for SEAPIE help")
    while True:
        parent_frame = sys._getframe(scope)
        parent_globals = parent_frame.f_globals
        parent_locals = parent_frame.f_locals
        codeblock = single_prompt()
        if codeblock == "!exit":
            break # this block allows reacting to magic values
        if codeblock == "!scope":
            print(sys._getframe(scope).f_code.co_name)
            continue
        if codeblock == "!help":
            print("SEAPIE v0.7 type !help for SEAPIE help")
            print("commands: !help, !exit, !scope, !scope+, !scope-, !tree")
            print("scope commands move up(-) or down(+) one call stack level")
            continue
        if codeblock == "!scope+":
            if scope >= 1:
                scope -= 1
            else:
                print("cant go higher than current call")
            continue
        if codeblock == "!scope-":
            try:
                sys._getframe(scope+2) # skip over seapie.seapie to empty space. disallows hitting seapie. change to +1 to allow hittig seapie itself
            except ValueError:
                print("call stack is not deep enough")
            else:
                scope += 1
            continue
        if codeblock == "!tree":
            for frame in reversed(inspect.stack()[1:]):
                try:
                    context = frame.code_context[0].strip()
                except TypeError:
                    context = '""'
                print(frame.function, (10-len(str(frame.function)))*" ", "calling", context, "as ...")
            continue
        try:
            exec(codeblock, parent_globals, parent_locals)
            ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(parent_frame), ctypes.c_int(1))
        except Exception as error: # catch arbitary exceptions from exec
            traceback.print_exc()