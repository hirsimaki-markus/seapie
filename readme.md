<div align="center">
    <img src="./img/seapie.svg" alt="seapie" height="80">

_Get the **`>>> _`** shell anywhere in your scipt –  **`pip install seapie`**_
</div>

<div align="center">

[![Python Version](https://img.shields.io/badge/Python-3.6_to_3.13%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Made with ❤️ in Finland](https://img.shields.io/badge/made_with_%E2%9D%A4%20in-Finland-blue)](https://en.wikipedia.org/wiki/Finland)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-blue?logo=github)](https://github.com/hirsimaki-markus/seapie/graphs/contributors)
[![License: The Unlicense](https://img.shields.io/badge/⚖️_licence-The_Unlicence-purple)](https://choosealicense.com/licenses/unlicense/)
[![Lines of Code](https://img.shields.io/badge/💾_lines_of_code-<500-blue)](https://github.com/hirsimaki-markus/seapie)
[![Dependencies: None](https://img.shields.io/badge/dependencies-😎_None-blue)](https://www.python.org/)
[![PyPI Version](https://img.shields.io/pypi/v/seapie)](https://pypi.org/project/seapie/)
[![Downloads](https://static.pepy.tech/badge/seapie)](https://pypi.org/project/seapie/)
[![GitHub Contributors](https://img.shields.io/github/contributors/hirsimaki-markus/seapie?color=2b9348&logo=github)](https://github.com/hirsimaki-markus/seapie/graphs/contributors)
[![Stars](https://img.shields.io/github/stars/hirsimaki-markus/seapie)](https://github.com/hirsimaki-markus/seapie/stargazers)
[![Forks](https://img.shields.io/github/forks/hirsimaki-markus/seapie)](https://github.com/hirsimaki-markus/seapie/network/members)
</div>



<hr>



🥧 seapie is a modern and intuitive Python debugger. Get the familiar `>>> _` shell
anywhere in your scripts with `seapie.breakpoint()` to inspect, modify, and control
the flow. It's as easy as `>>> print(myvariable)`.


<div><i>somewhere in myscript.py</i></div>

```python
print("script says hello")
import seapie; seapie.breakpoint()  # Shell starts here
do_stuff(my_variable)
```

<div><i>terminal</i></div>

```
user@system:~/$ python myscript.py
script says hello!
🥧  seapie 3.1.1 (Python 3.13.1) [GCC 9.4.0] on linux
Type "!help" or "!h" for seapie help.
>>> _
```

## 🐜 Debugging features in the >>> shell
<b>New !commands in the shell</b>
<br>
• `>>> !step` and `>>> !walk <expr>` and `>>> !goto <line>` – Single & conditional stepping and jump
<br>
• `>>> !up` and `>>> !down` – Navigate up and down the frames in callstack 
<br>
• `>>> !info` and `>>> !help` – Get your location in the callstack, source and view built in help
<br>
• `>>> !continue` – Resume execution seamlessly, keeping only your modifications
<br>
• `>>> !pretty` – Toggle automatic prettyprinting of evaluated expressions
<br>
• `>>> !mode` – Toggle between tracing (`call/return/line/exception`) and fast profiling (`call/return`)
<br>

<b>New built in \_variables_ in the shell showing current debug event</b>
<br>
• `_line_` and `_source_` and `_path_` – next line's line number, and source text, and source file path
<br>
• `_event_` – Current debug event, one of `"call"`/`"return"`/`"line"`/`"exception"`
<br>
• `_return_` – Object to be returned if `_event_` is `"return"`
<br>
• `_callstack_` – List of frame names in the callstack
<br>

## 📖 Examples and FAQ
<details><summary>Using the powerful stepping functionality</summary>

Debug mode is toggled twice, first to fast profiling and later back to full tracing.
The code is condititionally stepped until current debug event is `"call"`, and next line
number to execute is `34`, and `x` is present in `locals()` and `x` is `None`.
The `locals()` check is used to avoid `NameError` in frames where `x` is undefined.

```console
>>> !mode
🏃  Debugging mode set to profiling only (calls and returns)
>>> !w _event_ == "call" and _line_ == 34 and "x" in locals() and x is None
🚶  Walk condition set. Stepping until bool(eval('_event_ == "call" and _line_ == 34 and "x" in locals() and x is None')) is True
>>> !mode
🐌  Debugging mode set to tracing (calls, returns, lines, exceptions)
>>> _
```
</details>



<details><summary>The !help command as seen in terminal</summary>

```console
>>> !help
This >>> shell mimics a normal Python shell. Classes, functions, and so on can
be can be defined and used like normal. Most built-in Python functions and
features work as expected. New !commands and magic variables are listed below:

⚡  Commands - can be called the same way as !help
  (!h)elp      Show this help message
  (!s)tep      Execute code until next debug event. See !m section for events
  (!w)alk <e>  Execute code until expression <e> evaluates to True in an event
  (!u)p        Move one function call up in callstack, towards current line
  (!d)own      Move one function call down in callstack, towards script start
  (!g)oto <l>  Jump to a given line <l> in the current frame
  (!i)nfo      Show callstack with debug events and source code in current frame.
  (!c)ontinue  Detach the debugger from the code and resume normal execution
  (!p)retty    Toggle prettyprinting of the output
  (!m)ode      Toggle mode between full tracing (slow) and profiling (fast)
               ├ Debugging events when tracing: call, return, line, exception
               └ Debugging events when profiling: call, return

🔮  Magic variables - new builtins, updated every event, try "print(_line_)"
  _line_       Next line's line number
  _source_     Next line's source code
  _path_   Next line's source file
  _return_     Object to be returned if _event_ is return
  _event_      Current debug event, one of call/return/line/exception
  _callstack_  List of frame names in the callstack
  _            Latest evaluated expression (updated on input, not on event)

📝  Examples for !step and !walk - when !m is set to tracing
  Single step                  !s
  Step until line 8 in ok.py   !w _line_ == 8 and _path_ == '/mydir/abc.py'
  Until an exception event     !w _event_ == 'exception'
  Step forever                 !w False     # Will never eval to True
  No effect                    !w True      # Immediately evals to True
  Step until xyz.asd is found  !w xyz in locals() and hasattr(xyz, 'asd')

📝  Examples for !step and !walk - when !m is set to profiling
  Step to next return or call  !s
  Step until specific call     !w _event_ == 'call' and _line_ == 123
  Step until specific return   !w _event_ == 'return' and _return_ == None
>>> _
```
</details>


<details><summary>Manually patching the return value of a function</summary>
The debugger is used to patch in a placeholder response before continuing normal
execution.

```console
user@system:~/$ python myscript.py
25-02-23 13:38:04  Response: {}
🥧  seapie 3.1.1 (Python 3.13.1) [GCC 9.4.0] on linux
Type "!help" or "!h" for seapie help.
>>>
>>> !i
Callstack (currently selected frame marked):
  <'line' event on line 34 in 'network_func' at myscript.py> 👈
  <'call' event on line 41 in '<module>' at myscript.py>

Source lines (selected frame):
  25
  27     response = get_json_over_http("http://example.com")
  28
  29     logger.info(" Response: %s", response)
  30
  31     if not response:
  32         import seapie; seapie.breakpoint()
  33
  34     return converted(response) 👈
  35
  41 network_func()
>>>
>>> response = {"status": 200, "value": "44b883b3-caed-460c-9eba-665a7a9d1913"}
>>>
>>> !step
  <'line' event on line 34 in 'network_func' at myscript.py>
>>> !step
  <'call' event on line 4 in 'converted' at myscript.py>
>>> !continue
🔌  Detaching seapie
user@system:~/$
user@system:~/$ _
```
</details>
<details><summary>Pdb vs seapie ?</summary>

| Selling point                                                           | seapie  | pdb  |
| :---------------------------------------------------------------------- | :-----: | :--: |
| Intuitive interface                                                     |   ✔️    | ❌  |
| Automatically updated debugging variables                               |   ✔️¹   | ❌  |
| Supports complex conditional code stepping                              |   ✔️¹   | ❌  |
| Switch between slow tracing and fast profiling                          |   ✔️    | ⚠️² |
| Arbitrarily change state of the target program                          |   ✔️    | ⚠️³ |

¹ State can be inspected or stepped using `_line_`, `_source_`, `_path_`, `_return_`, `_event_`, `_callstack_`
<br>
² yes, but requires manually managing `sys.setprofile` and `sys.settrace`
<br>
³ can't do some things such as adding new variables to non-global scope
</details>
<details><summary>Multiprocessing and multithreading ?</summary>
In multiprocessing, seapie can be opened in any single process. If opened in multiple
processes at the same time, they should be connected to different terminals to avoid
confusing situations in the shell. In multithreading, a single thread can be debugged
at a time.
</details>
<details><summary>Post mortem debugging ?</summary>
You can achieve post mortem functionality using this try-except construct. The except
should be placed to as close to the source of the exception as possible to prevent
unrolling the callstack more than necessary. Currently seapie does not support moving
into the unrolled frames found in the exc_info but feature and pull requests are open.

```python
try:
    danger()
except Exception:  # Callstack gets unrolled from danger's exception until this block.
    import sys; info = sys.exc_info()  # Unrolled part of callstack is found in info.
    import seapie; seapie.breakpoint()
    pass  # Debugger prompt gets called on this line, the pass statement is necessary.
```
</details>
<details><summary>Dev stuff & licensing & contact ?</summary>

•  Install from source for dev: `seapie$ pip install -e .`
<br>
• Install from source: `seapie$ pip install .`
<br>
• Build & publish:
```bash
# Remember: increment __version__ in __init__.py
# Remember: .pypirc file is needed.
seapie$ python -m build --wheel
seapie$ rm -rf build/ && rm -rf src/seapie.egg-info/
seapie$ python -m twine check dist/*
seapie$ python -m twine upload dist/*
seapie$ rm -rf dist/
```
This project is in public domain. Feature requests and contributions are welcome. The
project is released under The Unlicense as a personal protest from the author against
the modern copyright landscape. If you need an alternative license, just contact me.
Email: ɯoɔ˙lᴉɐɯƃ (ʇɐ) snʞɹɐɯ˙ᴉʞɐɯᴉsɹᴉɥ




