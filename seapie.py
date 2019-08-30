import sys
import ctypes
import code
import traceback

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
            if accumulator == "": # if reading first line
                if raw_text == "!exit": return "!exit" # capture magic values
            accumulator += "\n"+raw_text # input cant read newline. add it manually

            try:
                result = code.compile_command(accumulator)
            except SyntaxError: # allow incorrect command to just pass thru
                return accumulator
            if result == None:
                pass # incomplete but possibly valid command
            else:
                return result

    parent_frame = sys._getframe(scope)
    parent_globals = parent_frame.f_globals
    parent_locals = parent_frame.f_locals

    print("SEAPIE v0.5 type !help for SEAPIE help")
    while True:
        codeblock = single_prompt()
        if codeblock == "!exit":
            break # this block allows reacting to magic values
        try:
            exec(codeblock, parent_globals, parent_locals)
            ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(parent_frame), ctypes.c_int(1))
        except Exception as error: # catch arbitary exceptions from exec
            traceback.print_exc()