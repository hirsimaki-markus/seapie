<img src="https://raw.githubusercontent.com/hirsimaki-markus/SEAPIE/master/images/SEAPIE.png" width="70" height="70"/>

# SEAPIE

``SEAPIE`` stands for ``Scope Escaping Arbitrary Python Injection Executor``

You can call ``seapie()`` _anywhere_ in your code to open python interpeter like console that can edit global, local and any other variable available in _any_ scope that is in the current call stack.

## Example

```python
from seapie.py import seapie
markdown = Redcarpet.new("Hello World!")
puts markdown.to_html
```

## Unlicensing
Distributed under [The Unlicense](https://choosealicense.com/licenses/unlicense/) <img src="https://raw.githubusercontent.com/hirsimaki-markus/SEAPIE/master/images/unlisence.png" width="12" height="12"/> by Markus Hirsimäki in 2019
