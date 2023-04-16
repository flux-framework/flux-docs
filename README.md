# Documentation

Edits should be made to the `.rst` files.
The documentation can be built with `make html` or `make man`.
The generated files will be found in the `_build` directory. Note that if you
want to build the docs, it is recommended to use the development environment to have
the Flux Python bindings available, e.g.,:

```python
import flux
# no error
```

If you build the docs in an environment without the bindings, the sphinx gallery examples
will not properly generate. This is OK if you don't edit them.

## VSCode Development Container

We provide a VSCode [Development Container](https://code.visualstudio.com/docs/remote/containers)
to provide an environment for you to easily work on the documentation, and ensure that Flux
is installed to generate some of our Sphinx Gallery (TBA) tutorials. This works by way
of the assets in [.devcontainer](https://code.visualstudio.com/docs/remote/containers#_create-a-devcontainerjson-file).

## Manual Development Container

If you want to generate the container manually, this is also an option! First build it:

```bash
$ docker build -f ./.devcontainer/Dockerfile -t flux-docs .
```
This will build the base environment. You can then bind your container to the present working directory to
build, either interactively:

```bash
$ docker run -it --rm -v $PWD/:/workspace/flux-docs flux-docs flux start make html
```

You can also go in interactively - just be careful and don't commit from within the container.

```bash
$ docker run -it --rm -v $PWD/:/workspace/flux-docs flux-docs bash
```

### Setup

You can follow the [tutorial](https://code.visualstudio.com/docs/remote/containers-tutorial) where you'll basically
need to:

1. Install Docker
2. Install the [Development Containers](vscode:extension/ms-vscode-remote.remote-containers) extension

Then you can go to the command palette (View -> Command Palette) and select `Dev Containers: Open Workspace in Container.`
and select your cloned Flux Docs repository root. This will build a development environment from [fluxrm/flux-sched](https://hub.docker.com/r/fluxrm/flux-sched/tags).

While this uses the focal base, you are free to change the base image and rebuild if you need to test on another operating system! 
When your container is built, when you open `Terminal -> New Terminal` and you'll be in the container! 
You should be able to build docs:

```bash
$ flux start make html
```

If you don't have Flux Python bindings or don't want to generate them, just fall back
to:

```bash
$ make html
```

The build will detect that the Flux Python bindings are not available and build everything
except for the examples gallery. And then you can do as you would do on your host to start a local webserver:

```console
..
The HTML pages are in _build/html.

$ cd _build/html/
$ python3 -m http.server 9999
Serving HTTP on 0.0.0.0 port 9999 (http://0.0.0.0:9999/) ...
```
VSCode is smart enough to see you open the port and give you a button to click to open it in
the browser! If not, you can open your browser to [http://localhost:9999/](http://localhost:9999/).
We will provide further instructions here for building sphinx examples as they are added.

**Important** it's recommended that you commit (or otherwise write to the .git folder) from the outside
of the container. This will allow you to sign commits with your (not mounted to the container) key,
and will ensure the permissions of the commit are not done by a root user. If you update the sphinx
examples, the permissions can also get wonky. In either case, you can run this from your terminal outside of VSCode:

```bash
$ sudo chown -R $USER .
$ sudo chown -R $USER .git/ .
# and then commit
```

## Installing Sphinx

Sphinx is used to generate man pages from the `.rst` files.
If Sphinx is not installed on the system, the following may be used to install Sphinx and the required theme.

``` shell
pip install -r requirements.txt
```

Users may want to install these packages into a [Python Virtual Environment](https://docs.python.org/3/tutorial/venv.html)

## Release

SPDX-License-Identifier: LGPL-3.0

LLNL-CODE-764420
