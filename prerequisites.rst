.. _prerequisites:

===================
Build Prerequisites
===================

This page is intended to list build requirements for base Flux framework projects, notably `flux-core <https://github.com/flux-framework/flux-core>`_, which is the foundation for most other framework projects.

The major requirements are listed in the sections below. Requirements are also kept up to date in a Travis-CI helper script in the flux-core source, `travis-dep-builder.sh <https://github.com/flux-framework/flux-core/blob/master/src/test/travis-dep-builder.sh>`_, which can either be run by hand to download requirements, or viewed to determine latest required versions and packages. `travis-dep-builder.sh` requires `pip` and `luarocks` to fetch python and Lua dependencies:

.. code-block:: console

    ~/flux-core.git $ src/test/travis-dep-builder.sh
    ...
    ~/flux-core.git $ $(src/test/travis-dep-builder.sh --printenv)
    ~/flux-core.git $ ./autogen.sh && ./configure 

Alternately `Spack <https://github.com/scalability-llnl/spack>`_ can be used to build all flux dependencies with either `spack install flux` or `spack diy flux@master` from inside a clone of the flux repository.

.. _zeromq:

------
ZeroMQ
------

Flux core messaging is built on the excellent `zeromq <http://zeromq.org/>`_ messaging library. Flux currently requires a relatively recent version of zeromq, built with libsodium support, as well as the `czmq <https://github.com/zeromq/czmq>`_ bindings for C:

+-------------+----------+--------------------------+
| Requirement | Version  |   Notes                  |
+=============+==========+==========================+
| `libsoduim` | `>1.0.1` |                          |
+-------------+----------+--------------------------+
| `zeromq`    | `>4.0.4` | built `--with-libsodium` |
+-------------+----------+--------------------------+
| `czmq`      | `=3.0.2` |                          |
+-------------+----------+--------------------------+

.. _json:

----
JSON
----

Flux makes heavy use of JSON encoding for messages. The code currently requires `jansson <https://github.com/akheron/jansson/>`_ v2.6 or greater.

.. _munge:

-----
MUNGE
-----

 * `libmunge <https://github.com/dun/munge>`_ v0.5.11 or greater

.. _hwloc:

-----
hwloc
-----

 * `hwloc <https://www.open-mpi.org/projects/hwloc/>`_ v1.11.1 or greater

.. _sqlite3:

-------
sqlite3
-------

 * `sqlite <https://sqlite.org/download.html>`_ version 3

.. _yaml-cpp:

-------
yaml-cpp
-------

 * `yaml-cpp <https://github.com/jbeder/yaml-cpp>`_ v0.5.1 or greater

.. _lua:

---
Lua
---
 
Flux makes use of Lua scripts and bindings for some functionality. Lua 5.1 is required for now. However, support for v5.2 and v5.3 is planned in the near future.

Lua module requirements include:
 
 * luaposix

Internal versions of `lua-hostlist` and `lua-affinity` are supplied with flux-core.

.. _python:

------
Python
------

Generation of flux-core bindings for python requires the following version of Python and support libs

+-------------+----------+--------------------------+
| Requirement | Version  |   Notes                  |
+=============+==========+==========================+
| `python`    | `>=2.7`  |                          |
+-------------+----------+--------------------------+
| `cffi`      | `>=1.0`  |                          |
+-------------+----------+--------------------------+
| `pycparser` | `>=2.2`  |                          |
+-------------+----------+--------------------------+
| `ply`       | `>=3.6`  |                          |
+-------------+----------+--------------------------+

.. _asciidoc:

--------
Asciidoc
--------

Manual pages are written in asciidoc. For man page generation `asciidoc` is required.
