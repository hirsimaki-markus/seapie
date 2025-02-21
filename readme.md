<div align="center">
    <img src="./img/seapie.svg" alt="seapie" height="80">
    <pre>pip install <a href="https://github.com/hirsimaki-markus/seapie">seapie</a></pre>
    <em>Get the <b>>>></b> shell anywhere in your scipt, debug, and continue</em>
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



🥧 seapie is a modern and intuitive Python debugger. Get the familiar shell
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

## Debugging features in the >>> shell
<b>🛠️ New !commands in the shell</b>
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
• `>>> !mode` – Toggle between full tracing (`call/return/line/exception`) and fast profiling (`call/return`)
<br>
• `>>> !help` – Show the debugger help message
<br>

<b>🔮 New built in \_variables_ in the shell showing current debug event</b>
<br>
• `_line_` and `_source_` and `_filepath_` – next line's line number, and source text, and source file path
<br>
• `_event_` – Current debug event, one of `"call"`/`"return"`/`"line"`/`"exception"`
<br>
• `_return_` – Object to be returned if `_event_` is `"return"`
<br>
• `_callstack_` – List of frame names in the callstack
<br>
• `_` – Latest evaluated expression (updated on output, not event)
<br>

<b>📖 Examples</b>
<br>
• Screenshot – here? or collapsible section?
<br>
• `>>> !w _line_ > 17 and _event_ == "return"`

## FAQ
<details><summary>🥧 seapie vs pdb / ipdb / pudb ?</summary>
“Why use seapie?” bullet list. A quick pitch with the main reasons to prefer seapie over
alternatives (e.g., built-in pdb, ipdb, pudb) could help new users decide faster.
</details>
<details><summary>🧵 multiprocessing and multithreading</summary>
“Why use seapie?” bullet list. A quick pitch with the main reasons to prefer seapie over
alternatives (e.g., built-in pdb, ipdb, pudb) could help new users decide faster.
</details>
<details><summary>💻 testing, building, and publishing</summary>
“Why use seapie?” bullet list. A quick pitch with the main reasons to prefer seapie over
alternatives (e.g., built-in pdb, ipdb, pudb) could help new users decide faster.
</details>
<details><summary>🤝 licensing and contributing</summary>
want to contat me? ɯoɔ˙lᴉɐɯƃ (ʇɐ) snʞɹɐɯ˙ᴉʞɐɯᴉsɹᴉɥ
“Why use seapie?” bullet list. A quick pitch with the main reasons to prefer seapie over
alternatives (e.g., built-in pdb, ipdb, pudb) could help new users decide faster.
</details>
<details><summary>🚩 known issues</summary>
“Why use seapie?” bullet list. A quick pitch with the main reasons to prefer seapie over
alternatives (e.g., built-in pdb, ipdb, pudb) could help new users decide faster.
</details>
