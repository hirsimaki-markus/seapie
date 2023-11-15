# seapie
v3 coming soon.def do_where

## Additional licensing
<details><summary>Show details</summary>

This software is licensed under The Unlicense as the author's protest towards
the modern copyright landscape. If you need a different lisence for a legal or
compability reasons, just ask.

</details>





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
  seapie$ seapie$ python -m twine check dist/*
  seapie$ python -m twine upload dist/*
  seapie$ rm -rf dist/
  ```

</details>