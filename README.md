# Documentation

Edits should be made to the `.rst` files.
The documentation can be built with `make html` or `make man`.
The generated files will be found in the `_build` directory.

## VSCode Development Container

We provide a VSCode [Development Container](https://code.visualstudio.com/docs/remote/containers)
to provide an environment for you to easily work on the documentation, and ensure that Flux
is installed to generate some of our Sphinx Gallery (TBA) tutorials. This works by way
of the assets in [.devcontainer](https://code.visualstudio.com/docs/remote/containers#_create-a-devcontainerjson-file).

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
$ make html
```

And then you can do as you would do on your host to start a local webserver:

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
and will ensure the permissions of the commit are not done by a root user.
If you accidentally do this and need to fix, you can run this from your terminal outside of VSCode:

```bash
$ sudo chown -R $USER .git/
# and then commit
```

## Installing Sphinx

Sphinx is used to generate man pages from the `.rst` files.
If Sphinx is not installed on the system, the following may be used to install Sphinx and the required theme.

``` shell
pip install -r requirements.txt
```

Users may want to install these packages into a [Python Virtual Environment](https://docs.python.org/3/tutorial/venv.html)
