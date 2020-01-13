"""Seapie is debugger like tool. SEAPIE stands for Scope Escaping Arbitary Python Injection Executor

usage as breakpoint: import seapie;seapie.seapie()

usage as true exec: import seapie;seapie.true_exec(codeblock, scope=0)
    * where codeblock is raw string or compiled code suitable normal exec()
    * where scope states how many scope should be escape. 0 stands for executing in parent scope.

example: import seapie;seapie.true_exec("x=5", scope=0)
    * changes x in calling scope to value of 5.
    * this cant create new variables. they will nameError.
    * scope=1 would change value of x in the scope that encloses the caller of true_exec
"""

import sys
import ctypes
import code
import traceback
import inspect
import codeop


class SingletonException(Exception):
    """helper exception used in case someone tries to initialize seapie instance instead of using the class without instance"""
    pass

class SeapieReplExitException(Exception):
    """raised to close seapie repl"""
    pass

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

    # __instance = None
    scope = 1          # 2+ avoids going into seapie itself
    # executable = executable  # seapie runs only this if not none

    def __init__(self):
        """Initializes a seapie instance. seapie objects should not be saved"""
        """this class is singleton so the instance is actually stored 'as' the class information. dont make more instances. its gonna blow up"""
        # if Seapie.__instance is not None:
        raise SingletonException("The Seapie class is a logical and instanceless singleton! Access the prompt with Seapie.repl() or convenient seapie() that points to Seapie.repl()")
        # else:
        #     Seapie.__instance = self

    @classmethod
    def repl(cls):
        """Main code injector loop"""
        # if cls.executable is None:
        #     print("=======[  SEAPIE v1.2 type !help for SEAPIE help  ]=======")
        while True:
            # parent = sys._getframe(cls.scope)  # frame enclosing seapie() call
            # parent_globals = parent.f_globals
            # parent_locals = parent.f_locals
            # if cls.executable:                 # if executable block is given
            #     codeblock = cls.executable     # only the executable is ran
            #     cls.prompt_open = False        # and prompt closes after it
            # else:
            #     codeblock = cls.single_prompt()
            codeblock = cls.single_prompt()
            
            if isinstance(codeblock, str):  # got magic string
                try:
                    cls.magic_handler(codeblock)
                    continue # magic is handled. get new command
                except SeapieReplExitException: # this is raised in magic handler if the repl should exit. magic handler never returns anything
                    return
            else:
                try:
                    cls.arbitary_executor(codeblock, cls.scope)
                except Exception:  # catch arbitary exceptions from exec
                    traceback.print_exc()
        # if cls.executable is None:
        #     print("=======[  Closing SEAPIE v1.1 prompt. Continuing  ]=======")

    @staticmethod
    def arbitary_executor(codeblock, scope=0):
        parent = sys._getframe(scope+1)  # frame enclosing seapie() call. +1 escapes this arbitary_executor function itself
        parent_globals = parent.f_globals
        parent_locals = parent.f_locals
        exec(codeblock, parent_globals, parent_locals)
        # the following call forces update to locals()
        # adding new variables is allowed but calling them requires
        # some indirection like using exec() or a placeholder
        # otherwise you will get nameerror
        # the magic value 1 stands for ability to introduce new variables. 0 for update-only
        ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(parent),
                                                      ctypes.c_int(1))


    @classmethod
    def magic_handler(cls, magicstring):
        """Any magic strings starting with ! are handled here"""
        if magicstring == "!exit":
            raise SeapieReplExitException
        elif magicstring == "!scope":
            print(sys._getframe(cls.scope+1).f_code.co_name)
        elif magicstring == "!help":
            print("SEAPIE v1.1 type !help for SEAPIE help\n")
            print("!help   : this message")
            print("!exit   : exit seapie and continue exection")
            print("!scope  : view currently used namespace from callstack")
            print("!tree   : view current call stack")
            print("!scope+ : increase scope, move towards global namespace")
            print("!scope- : decrease scope, move towards local namespace")
        elif magicstring == "!scope-":
            if cls.scope >= 3:  # avoid going into seapie module itself
                cls.scope -= 1
            else:
                print("cant go higher than current call")
        elif magicstring == "!scope+":
            try:
                sys._getframe(cls.scope+2)  # avoid calling nonexisting frame
            except ValueError:
                print("call stack is not deep enough")
            else:
                cls.scope += 1
        elif magicstring == "!tree":
            print()
            for call in traceback.format_stack()[:-2]:
                print(call)
        else:
            print("Unknown magic command!")

    @staticmethod
    def single_prompt():
        """Interactive prompt that stays open until it can return single compiled expression/statement or magic string"""
        accumulator = ""
        raw_text = ""
        while True:
            try:
                if not accumulator:  # if on first line of incoming block
                    raw_text = input(str("<S> " + sys.ps1))
                else:  # if on continuing line
                    raw_text = input(str("<S> " + sys.ps2))
            except KeyboardInterrupt:  # emulate behaviour of ctrl+c
                print("\nKeyboardInterrupt")
                accumulator = ""
                continue
            except EOFError:  # emulate behaviour of ctrl+z
                sys.exit(1)
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

# THIS BLOCK IS RUN AT IMPORT TIME
# it is INTENTIONALLY not placed inside of """ if name: '__main__': """
# as it is used to initialize the library during import
# and it is used to initialize sys.ps1 and sys.ps2

try:  # enables support for sys.ps1
    sys.ps1
except AttributeError:
    sys.ps1 = ">>> "
try:  # enables support for sys.ps2
   sys.ps2
except AttributeError:
    sys.ps2 = "... "

seapie = Seapie.repl
true_exec = Seapie.arbitary_executor

