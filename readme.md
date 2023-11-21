<h1>seapie</h1>
<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=25&duration=3000&pause=700&color=46BDFF&vCenter=true&random=false&width=350&height=40&lines=intuitive+debugger;free+and+open+source;powerful+code+stepping;remote+debugging" alt="Typing SVG" /></a>

<img src="./img/seapie.png" alt="seapie" height='110' align="right">

<div>
<p align="left">
  <a href="https://pypi.org/project/seapie/"><img src="https://static.pepy.tech/badge/seapie"></a>
  &nbsp;
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.12.0-blue?logo=python&logoColor=white"/></a>
  <br>
  <a href="https://choosealicense.com/licenses/unlicense/"><img src="https://img.shields.io/badge/licence-The_Unlicence-purple"/></a>
  &nbsp;
  <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/style-black-000000"/></a>
  <br>
  <a href="https://en.wikipedia.org/wiki/Finland"><img src="https://img.shields.io/badge/made_with_%E2%9D%A4%20in-Finland-blue"/></a>
  &nbsp;
  <a href="https://github.com/hirsimaki-markus/seapie/graphs/contributors"><img src="https://img.shields.io/badge/contributions-welcome-blue"/></a>
  <br>
  <a href="https://github.com/hirsimaki-markus/seapie"><img src="https://img.shields.io/badge/lines_of_code-1k-blue"/></a>
  &nbsp;
  <a href="https://github.com/hirsimaki-markus/seapie"><img src="https://img.shields.io/pypi/v/seapie"></a>
</p>
</div>


<div align="center">
    <br>
    <pre>pip install <a href="https://github.com/hirsimaki-markus/seapie">seapie</a></pre>
    <br>
    <br>
</div>

## Additional licensing
<details><summary>Show details</summary>

This software is licensed under The Unlicense as the author's protest towards
the modern copyright landscape. If you need a different lisence for a legal or
compability reasons, just ask.

</details>

<br>
<br>

## Documentation
<details><summary>Show details</summary>

```python
>>> import seapie
>>> help(seapie)
>>> # Or take a look at the well documented source.
```

</details>

<br>
<br>





## Development details
<details><summary>Show details</summary>

  **Linting**
  ```bash
  seapie$ python -m isort .
  seapie$ python -m black .
  seapie$ python -m flake8 src/ test/
  ```

  **Testing**
  ```bash
  seapie$ python test/??????
  ```

  **Building & releasing**
  ```bash
  # Remember to increment __version__ in __init__.py
  seapie$ python -m build --wheel && rm -rf build/ && rm -rf src/seapie.egg-info/
  seapie$ python -m twine check dist/*
  seapie$ python -m twine upload dist/*
  seapie$ rm -rf dist/
  ```

</details>