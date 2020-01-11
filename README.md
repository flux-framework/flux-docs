# Documentation

Edits should be made to the `.rst` files.
The documentation can be built with `make html` or `make man`.
The generated files will be found in the `_build` directory.

## Installing Sphinx

Sphinx is used to generate man pages from the `.rst` files.
If Sphinx is not installed on the system, the following may be used to install Sphinx into a virtualenv.

``` shell
virtualenv --system-site-packages env
source env/bin/activate
pip install sphinx
```

If using this method, then source the virtualenv before running the Makefile steps below:

``` shell
source env/bin/activate
```
