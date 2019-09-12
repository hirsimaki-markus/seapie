import sys
import ctypes
import code
import traceback
import inspect
import codeop

class Seapie:
    """Container class for seapie() and its helper functions"""
    def __init__(self):
        try: sys.ps1
        except AttributeError: sys.ps1 = ">>> "
        try: sys.ps2
        except AttributeError: sys.ps2 = "... "
        self.scope = 2
        self.prompt_open = True # allows magic_handler to break loop in seapie()
        self.seapie()

    def seapie(self):
        """Main code injector function"""
        print("SEAPIE v0.7 type !help for SEAPIE help")
        while self.prompt_open:
            parent_frame = sys._getframe(self.scope)
            parent_globals = parent_frame.f_globals
            parent_locals = parent_frame.f_locals
            codeblock = self.single_prompt()
            if isinstance(codeblock, str): # got magic string instead of code object
                self.magic_handler(codeblock)
            else:
                try:
                    exec(codeblock, parent_globals, parent_locals)
                    ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(parent_frame), ctypes.c_int(1))
                except Exception as error: # catch arbitary exceptions from exec
                    traceback.print_exc()

    def magic_handler(self, magicstring):
        """Any magic strings starting with ! are handled here"""
        if magicstring == "!exit":
            self.prompt_open = False
            return
        elif magicstring == "!scope":
            print(sys._getframe(self.scope+1).f_code.co_name)
            return
        elif magicstring == "!help":
            print("SEAPIE v0.7 type !help for SEAPIE help")
            print("commands: !help, !exit, !scope, !scope+, !scope-, !tree")
            print("scope commands move up(-) or down(+) one call stack level")
            return
        elif magicstring == "!scope+":
            if self.scope >= 3:
                self.scope -= 1
            else:
                print("cant go higher than current call")
            return
        elif magicstring == "!scope-":
            try:
                sys._getframe(self.scope+2) # skip over seapie.seapie to empty space. disallows hitting seapie. change to +1 to allow hittig seapie itself
            except ValueError:
                print("call stack is not deep enough")
            else:
                self.scope += 1
            return
        elif magicstring == "!tree":
            for frame in reversed(inspect.stack()[3:]):
                try:
                    context = frame.code_context[0].strip()
                except TypeError:
                    context = '""'
                print(frame.function, (10-len(str(frame.function)))*" ", "calling", context, "as ...")
            print("seapie")
            return
        else:
            print("Unknown magic command!")
            return

    def single_prompt(self):
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
            if accumulator == "" and raw_text.startswith("!"): # if reading first line
                return raw_text
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