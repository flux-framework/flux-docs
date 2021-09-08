.. _coral2:

==============
CORAL2 Systems
==============

The LLNL, LBNL, and ORNL next-generation systems like RZNevada, Perlmutter,
El Capitan, and Frontier are in various stages of early access. They are
similar in that they all use the HPE Cray Shasta platform, which requires
a few additional components to integrate completely with Flux.

--------------
Things to Know
--------------
#.  Every multi-node running job on Shasta systems consumes two port numbers
    out of a global pool that Flux reserves. So if Flux has 1,000
    reserved ports, only 500 multi-node jobs may be active at any time.
    Attempting to run further multi-node jobs will cause the excess jobs
    to fail. There is no limit on *submitted* multi-node jobs, and
    single-node jobs do not count towards the limit.
#.  All nested Flux instances (e.g. instances created with ``flux mini batch``,
    ``flux mini alloc``, or ``flux mini submit ... flux start``
    should meet one of the following criteria:

    - Occupy a single node
    - Have exclusive access to the nodes they are running on (e.g. they
      do not share their resources with sibling instances).

    Instances that do not meet one of the above criteria will not work properly.

------------------------
Building Flux for CORAL2
------------------------

The basic steps to building Flux for Cray Shasta systems are as follows:

#.  :ref:`Build flux-core and flux-sched manually <manual_installation>`
    with some prefix *P*.
#.  Build `flux-coral2 <https://github.com/flux-framework/flux-coral2>`_
    with the same prefix *P*.
#.  Create a Flux config file specifying that the ``cray_pals_port_distributor.so``
    plugin should be loaded with some given port range (see below for an example).
    If you have other config files, put the new file in with the others.
    Before launching Flux, point Flux to the *directory* containing your config
    file(s) by setting the ``FLUX_CONF_DIR`` environment variable, or by passing
    ``-o"-c/path/to/config"`` to ``flux start``.
#.  As an alternative to creating a config file and setting ``FLUX_CONF_DIR``,
    you can, after starting Flux, execute ``flux jobtap load
    cray_pals_port_distributor.so port-min=$N port-max=$M`` for some *N* and *M*.


If you see job failures with an error message like "no cray_pals_port_distribution
event posted", check that you have the ``cray_pals_port_distributor.so`` plugin
loaded by running ``flux jobtap list``. If you don't see it in the list, retry
step 3 or 4 above.

A script to build Flux is below.

.. code-block:: sh

  #!/bin/bash

  set -e

  PREFIX=$HOME/local  # a good default, but modify as needed
  PORT_MIN=11000      # a good default, but modify as needed
  PORT_MAX=12000      # a good default, but modify as needed

  # Step 1: Build flux-core 0.29 or later

  wget https://github.com/flux-framework/flux-core/releases/download/v0.29.0/flux-core-0.29.0.tar.gz

  tar -xzvf flux-core-0.29.0.tar.gz && cd flux-core-0.29.0

  ./configure --prefix=$PREFIX && make -j && make install && cd ..

  # The `flux` executable will now be in ~/local/bin/flux but it needs some
  # additional flux-coral2 extensions


  # Step 2: Build flux-sched 0.18 or later (optional but recommended)

  wget https://github.com/flux-framework/flux-sched/releases/download/v0.18.0/flux-sched-0.18.0.tar.gz

  tar -xzvf flux-sched-0.18.0.tar.gz && cd flux-sched-0.18.0

  ./configure --prefix=$PREFIX && make -j && make install && cd ..


  # Step 3: Build flux-coral2

  git clone https://github.com/flux-framework/flux-coral2.git && cd flux-coral2

  ./autogen.sh && ./configure --prefix=$PREFIX && make -j && make install

  libtool --finish $PREFIX/lib/flux/job-manager/
  libtool --finish $PREFIX/lib/flux/shell/plugins/
  cd ..


  # Step 4: add a config file to automatically load a flux-coral2 plugin

  mkdir -p $PREFIX/etc/flux/config

  echo "[job-manager]
  plugins = [
     { load = \"cray_pals_port_distributor.so\", conf = { port-min = $PORT_MIN, port-max = $PORT_MAX } }
  ]
  " > $PREFIX/etc/flux/config/cray_pals_ports.toml

  echo "Done! Now set FLUX_CONF_DIR=$PREFIX/etc/flux/config
  in your environment and run with $PREFIX/bin/flux"

