<div align="center">
    <img src="./img/seapie.svg" alt="seapie" height="100">
    <pre>pip install <a href="https://github.com/hirsimaki-markus/seapie">seapie</a></pre>
    <em>Inject the <b>>>></b> shell anywhere, debug, and resume seamlessly</em>
</div>
<br>
<div align="center">
    <a href="https://www.python.org/downloads/">
        <img src="https://img.shields.io/badge/Python-3.6_to_3.13%2B-blue.svg?logo=python&logoColor=white" alt="Python Version">
    </a>
    <a href="https://en.wikipedia.org/wiki/Finland">
        <img src="https://img.shields.io/badge/made_with_%E2%9D%A4%20in-Finland-blue"/>
    </a>
    <a href="https://github.com/hirsimaki-markus/seapie/graphs/contributors">
        <img src="https://img.shields.io/badge/contributions-welcome-blue?logo=github"/>
    </a>
    <a href="https://choosealicense.com/licenses/unlicense/">
        <img src="https://img.shields.io/badge/⚖️_licence-The_Unlicence-purple"/>
    </a>
    <a href="https://github.com/hirsimaki-markus/seapie">
        <img src="https://img.shields.io/badge/💾_lines_of_code->500-blue"/>
    </a>
    <a href="https://www.python.org/">
        <img src="https://img.shields.io/badge/Dependencies-😎_None-blue"/>
    </a>
    <a href="https://github.com/hirsimaki-markus/seapie">
        <img src="https://img.shields.io/pypi/v/seapie">
    </a>
    <a href="https://pypi.org/project/seapie/">
        <img src="https://static.pepy.tech/badge/seapie">
    </a>
    <a href="https://github.com/hirsimaki-markus/seapie/graphs/contributors">
        <img alt="GitHub contributors" src="https://img.shields.io/github/contributors/hirsimaki-markus/seapie?color=2b9348&logo=github">
    </a>
    <a href="https://github.com/hirsimaki-markus/seapie/stargazers">
        <img src="https://img.shields.io/github/stars/hirsimaki-markus/seapie" alt="Stars Badge"/>
    </a>
    <a href="https://github.com/hirsimaki-markus/seapie/network/members">
        <img src="https://img.shields.io/github/forks/hirsimaki-markus/seapie" alt="Forks Badge"/>
    </a>
</div>
<hr>
<br>

🥧 seapie is a modern and intuitive Python debugger. Get an instant interactive shell
anywhere in your scripts with `seapie.breakpoint()` to inspect, modify, and control
program state like the normal python shell: `>>> print("hello world")`
<br>

<div><i>somewhere in myscript.py</i></div>

```python
...
my_variable = 123
import seapie; seapie.breakpoint()  # Shell starts here
do_stuff(my_variable)
...
```

<div><i>terminal</i></div>

```
user@system:~/$ python myscript.py
script says hello!
🥧  seapie 3.1.1 (Python 3.13.1) [GCC 9.4.0] on linux
Type "!help" or "!h" for seapie help.
>>>
>>> _
```

## Features

In the shell new `!commands` and built in `_magic_` variables are available.
These can be used for example to step until condition is met: `>>> !w _line_ > 17 and _event_ == "return"`
<br>

**🛠️ New !commands added to the shell**
<br>
• `>>> !step` and `>>> !walk <expression>` – Single stepping and conditional stepping
<br>
• `>>> !up` and `>>> !down` – Navigate up and down the frames in callstack 
<br>
• `>>> !goto <line>` – Skip ahead or rewind execution within the current frame
<br>
• `>>> !info` – Get your location in the callstack and source file 
<br>
• `>>> !continue` – Resume execution seamlessly, keeping only your modifications
<br>
• `>>> !pretty` – Toggle automatic prettyprinting of evaluated expressions
<br>
• `>>> !mode` – Switch between fast profiling and detailed tracing with
<br>

**🔮 New built in \_magic_ variables added to the shell, updated on each debug event**
<br>
• `_line_` – New built in magic variable: next line's line number
<br>
• `_source_` – Next line's source code
<br>
• `_filepath_` – Next line's source file
<br>
• `_return_` – Object to be returned if `_event_` is `"return"`
<br>
• `_event_` – Current debug event, one of `"call"`/`"return"`/`"line"`/`"exception"`
<br>
• `_callstack_` – List of frame names in the callstack
<br>
• `_` – Latest evaluated expression (updated on input, unlike others)




