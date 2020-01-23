# Documentation

Edits should be made to the `.rst` files.
The documentation can be built with `make html` or `make man`.
The generated files will be found in the `_build` directory.

## Installing Sphinx

Sphinx is used to generate man pages from the `.rst` files.
If Sphinx is not installed on the system, the following may be used to install Sphinx and the required theme.

``` shell
pip install sphinx
pip install sphinx_rtd_theme
```

Users may want to install these packages into a [Python Virtual Environment](https://docs.python.org/3/tutorial/venv.html)
