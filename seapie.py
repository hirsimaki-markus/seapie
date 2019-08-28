import sys
import ctypes
import codeop
import traceback

def seapie(scope=1):
    """Scope Escaping Arbitrary Python Injection Executor"""
    # https://www.python.org/dev/peps/pep-0558/
    # https://faster-cpython.readthedocs.io/mutable.html
    # https://docs.python.org/3/library/codeop.html#codeop.compile_command
    # https://docs.python.org/3/library/code.html#module-code

    def single_prompt():
            accumulator = ""
            while True:
                try:
                    if not accumulator: raw_text = input(">>> ")
                    else:               raw_text = input("... ")
                except KeyboardInterrupt:
                    raw_text = ""
                    print("\nKeyboardInterrupt")
                # next two lines catch magic values when they are entered alone
                if accumulator == "":
                    if raw_text == "!exit": return "!exit"
                accumulator += "\n"+raw_text
                # add newline to as input doesnt read it. this will add extra
                # newline at start
                
                try:
                    result = codeop.compile_command(accumulator)
                except SyntaxError:
                    #result = accumulator
                    return accumulator  # allow syntax to pass thru to pass thru
                if result != None: # captured one complete command
                    compiled = compile(accumulator[1:], '<stdin>', 'single') # this compilation allows for 1;1;1 to work as expected
                    return compiled


    parent_frame = sys._getframe(1)
    local_frame = sys._getframe(0)
    local_frame.f_locals.update(parent_frame.f_locals)
    ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(local_frame),ctypes.c_int(1))
    print("SEAPIE v0.3 type !help for SEAPIE help")
    while True:
        # local variables can be assinged by modifying locals() but cannot be
        # edited nor deleted via it

        codeblock = single_prompt()
        if codeblock == "!exit":
            break # this block allows reacting to magic values
        try:
            exec(codeblock)
        except Exception as error:      # so we need to catch the error
            traceback.print_exc()       # and print traceback


        # purge updates from vairables used in this function to avoid
        # recursive namespaces and other pollution
        updates = dict(local_frame.f_locals)
        for i in ("injection", "frame", "__doc__", "single_prompt",
                 "codeblock", "parent_frame", "local_frame", "updates", "scope", "i"):
            try:
                updates.pop(i)
            except KeyError: # remove local variables if they exist to avoid
                pass         # polluting namespace

        # push updates to parent namespace. this cannot delete items
        local_frame.f_locals.update(updates)
        ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(parent_frame),ctypes.c_int(1))
        
        # find items that are locally deleted and whose deletion should be propagated to parent scope
        deleted_items = { k : parent_frame.f_locals[k] for k in set(parent_frame.f_locals) - set(updates)}
        for i in deleted_items:
            del parent_frame.f_locals[i]
            ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(parent_frame),ctypes.c_int(1))


