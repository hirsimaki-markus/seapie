"""Seapie is debugger like tool with ability to escape scopes in call stack

example use:
    from seapie import Seapie as seapie

    def test():
        seapie(1, "a_variable_in_scope_of_test2_only = 'hacked'")
        # seapie escapes the scopes and modifies it anyways

    def test2():
        a_variable_in_scope_of_test2_only = 1
        test()
        print(a_variable_in_scope_of_test2_only)

    test2()

example use2:
    from seapie import Seapie as seapie

    # your program here
    # ...
    seapie()  # and use !help when the prompt opens
    # more of your program here
    # ...
"""

import sys
import ctypes
import code
import traceback
import inspect
import codeop


class Seapie:
    """Container class for seapie() and its helper functions.

    Usage:
        from seapie import Seapie as seapie
        seapie(steps=0, executable=None)

        # where "steps" means how many callstack frames seapie is supposed to
        # escape. 0 means current namespace, 1 means parent namespace etc.
        #
        # and where "executable" is either code object or executable string.
        # if no "executable" argument is given seapie opens interactive prompt.
    """

    def __init__(self, steps=0, executable=None):
        """Initializes a seapie instance. seapie objects should not be saved"""
        try:  # enables support for sys.ps1
            sys.ps1
        except AttributeError:
            sys.ps1 = ">>> "
        try:  # enables support for sys.ps2
            sys.ps2
        except AttributeError:
            sys.ps2 = "... "
        self.scope = steps+2          # 2+ avoids going into seapie itself
        self.prompt_open = True       # allows magic_handler to break repl
        self.executable = executable  # seapie runs only this if not none
        self.seapie()

    def seapie(self):
        """Main code injector loop"""
        if self.executable is None:
            print("=======[  SEAPIE v1.1 type !help for SEAPIE help  ]=======")
        while self.prompt_open:
            parent = sys._getframe(self.scope)  # frame enclosing seapie() call
            parent_globals = parent.f_globals
            parent_locals = parent.f_locals
            if self.executable:                 # if executable block is given
                codeblock = self.executable     # only the executable is ran
                self.prompt_open = False        # and prompt closes after it
            else:
                codeblock = self.single_prompt()
            if isinstance(codeblock, str):  # got string or failed code object
                if codeblock[0] == "!":     # got magic string
                    self.magic_handler(codeblock)
                    continue
            try:
                exec(codeblock, parent_globals, parent_locals)
                # the following call forces update to locals()
                # adding new variables is allowed but calling them requires
                # some indirection like using exec() or a placeholder
                # otherwise you will get nameerror
                ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(parent),
                                                      ctypes.c_int(1))
            except Exception:  # catch arbitary exceptions from exec
                traceback.print_exc()
        if self.executable is None:
            print("=======[  Closing SEAPIE v1.1 prompt. Continuing  ]=======")

    def magic_handler(self, magicstring):
        """Any magic strings starting with ! are handled here"""
        if magicstring == "!exit":
            self.prompt_open = False
        elif magicstring == "!scope":
            print(sys._getframe(self.scope+1).f_code.co_name)
        elif magicstring == "!help":
            print("SEAPIE v1.1 type !help for SEAPIE help\n")
            print("!help   : this message")
            print("!exit   : exit seapie and continue exection")
            print("!scope  : view currently used namespace from callstack")
            print("!tree   : view current call stack")
            print("!scope+ : increase scope, move towards global namespace")
            print("!scope- : decrease scope, move towards local namespace")
        elif magicstring == "!scope-":
            if self.scope >= 3:  # avoid going into seapie module itself
                self.scope -= 1
            else:
                print("cant go higher than current call")
        elif magicstring == "!scope+":
            try:
                sys._getframe(self.scope+2)  # avoid calling nonexisting frame
            except ValueError:
                print("call stack is not deep enough")
            else:
                self.scope += 1
        elif magicstring == "!tree":
            print()
            for call in traceback.format_stack()[:-3]:
                print(call)
        else:
            print("Unknown magic command!")

    @staticmethod
    def single_prompt():
        """Interactive prompt that returns single expression/statement"""
        accumulator = ""
        raw_text = ""
        while True:
            try:
                if not accumulator:  # if on first line of incoming block
                    raw_text = input(str(sys.ps1))
                else:  # if on continuing line
                    raw_text = input(str(sys.ps2))
            except KeyboardInterrupt:  # emulate behaviour of ctrl+c
                print("\nKeyboardInterrupt")
                accumulator = ""
                continue
            if accumulator == "" and raw_text.startswith("!"):  # got magic
                return raw_text
            # this block should catch situation where two or more newlines
            # are entered during function definition or other such things
            if raw_text == "":
                try:
                    accumulator = "\n"+accumulator
                    codeop.compile_command(accumulator, "<input>", "single")
                except:  # catch exceptions compiling and reset
                    traceback.print_exc()
                    accumulator = ""
                    continue
            accumulator += "\n"+raw_text  # manually add newline after inputs
            try:
                result = code.compile_command(accumulator)
            except SyntaxError:  # allow incorrect commands to just pass thru
                return accumulator
            if result is None:
                pass  # incomplete but possibly valid command
            else:
                return result

if __name__ == "__main__":
    print("""
    # You should probably not be running this file as is unless you wanted to
    # open seapie prompt outside of your program. try the following in your app
    # as using seapie from the interactive prompt might cause problems

    from seapie import Seapie as seapie
    def test():
        seapie(1, "a_variable_in_scope_of_test2_only = 'hacked'")
        # seapie escapes the scopes and modifies it anyways
    def test2():
        a_variable_in_scope_of_test2_only = 1
        test()
        print(a_variable_in_scope_of_test2_only)
    test2()
    """)
    def test():
        Seapie()
    def test2():
        a_variable_in_scope_of_test2_only = 1
        test()
    test2()
