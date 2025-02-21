<div align="center">
    <img src="./img/seapie.svg" alt="seapie" height="100">
    <pre>pip install <a href="https://github.com/hirsimaki-markus/seapie">seapie</a></pre>
    <em>Get the <b>>>></b> shell in your scipt, debug, resume</em>
</div>



<br>



<div align="center">

[![Python Version](https://img.shields.io/badge/Python-3.6_to_3.13%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Made with ❤️ in Finland](https://img.shields.io/badge/made_with_%E2%9D%A4%20in-Finland-blue)](https://en.wikipedia.org/wiki/Finland)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-blue?logo=github)](https://github.com/hirsimaki-markus/seapie/graphs/contributors)
[![License: The Unlicense](https://img.shields.io/badge/⚖️_licence-The_Unlicence-purple)](https://choosealicense.com/licenses/unlicense/)
[![Lines of Code](https://img.shields.io/badge/💾_lines_of_code-<500-blue)](https://github.com/hirsimaki-markus/seapie)
[![Dependencies: None](https://img.shields.io/badge/dependencies-😎_None-blue)](https://www.python.org/)
[![PyPI Version](https://img.shields.io/pypi/v/seapie)](https://github.com/hirsimaki-markus/seapie)
[![Downloads](https://static.pepy.tech/badge/seapie)](https://pypi.org/project/seapie/)
[![GitHub Contributors](https://img.shields.io/github/contributors/hirsimaki-markus/seapie?color=2b9348&logo=github)](https://github.com/hirsimaki-markus/seapie/graphs/contributors)
[![Stars](https://img.shields.io/github/stars/hirsimaki-markus/seapie)](https://github.com/hirsimaki-markus/seapie/stargazers)
[![Forks](https://img.shields.io/github/forks/hirsimaki-markus/seapie)](https://github.com/hirsimaki-markus/seapie/network/members)

</div>



<hr>



🥧 seapie is a modern & intuitive Python debugger. Get the familiar shell
anywhere in your scripts with `seapie.breakpoint()` to interact and control
the program flow. It's that easy: `>>> print("myvar:", x)`


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




