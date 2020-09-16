.. _quickstart:

============
Quick Start
============

A quick introduction to Flux and flux-core.

.. _building-code:

-----------------
Building the Code
-----------------

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Spack: Recommended for curious users
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Flux maintains an up-to-date package in the `spack <https://github.com/spack/spack>`_ develop branch. If you’re already using spack, just run the following to install flux and all necessary dependencies:

.. code-block:: console

  $ spack install flux-sched

The above command will build and install the latest tagged version of flux-sched and flux-core.  To install the latest master branches, use the ``@master`` version specifier: ``spack install flux-sched@master``. If you want Flux to manage and schedule Nvidia GPUs, include the ``+cuda`` variant: ``spack install flux-sched+cuda``.  This builds a CUDA-aware version of hwloc.


For instructions on installing spack, see `Spack's installation documentation <https://spack.readthedocs.io/en/latest/getting_started.html#installation>`_.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Docker: Recommended for quick, single-node deployments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Flux has a continuously updated Docker image available for download on `Docker Hub <https://hub.docker.com/u/fluxrm>`_. If you already have docker installed, just run the following to download the latest Flux docker image and start a container from it:

.. code-block:: console

  $ docker run -ti fluxrm/flux-sched:latest
  $ flux getattr size
  1
  $ flux mini run printenv FLUX_JOB_ID
  2597498912768

.. note::
   Multi-node docker deployments of Flux is still an ongoing area of research.
   This installation method is recommended for developers and users curious to
   try single-node instances of Flux.

The default CMD for flux docker images is ``flux start /bin/bash``. To emulate a multi-node deployment within a single container, replace the default CMD by supplying args to ``docker run``:

.. code-block:: console

   $ docker run -ti fluxrm/flux-sched flux start --size 4
   $ flux getattr size
   4

If you are developing Flux and want to compile the modified code and run our testsuite within a docker container, you can use our helper script:

.. code-block:: console

   $ git clone https://github.com/flux-framework/flux-core.git
   Initialized empty Git repository in /home/fluxuser/flux-core/.git/
   $ cd flux-core
   $ ./src/test/docker/docker-run-checks.sh
   <snip>
   ============================================================================
   Testsuite summary for flux-core 0.16.0-371-gfe938825c
   ============================================================================
   # TOTAL: 2389
   # PASS:  2367
   # SKIP:  19
   # XFAIL: 3
   # FAIL:  0
   # XPASS: 0
   # ERROR: 0
   ============================================================================


.. note::
   Both the flux-core and flux-sched repositories have the ``docker-run-checks.sh`` helper script

.. _manual_installation:

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Manual Installation: Recommended for developers and contributors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ensure the latest list of requirements are installed. The current list of build requirements are detailed `here <http://flux-framework.org/docs/requirements/>`_.

Clone current flux-core master:

.. code-block:: console

  $ git clone https://github.com/flux-framework/flux-core.git
  Initialized empty Git repository in /home/fluxuser/flux-core/.git/
  $ cd flux-core

Build flux-core. In order to build python bindings, ensure you have python-3.6 and python-cffi available in your current environment:

.. code-block:: console

  $ ./autogen.sh && ./configure --prefix=$HOME/local
  Running aclocal ...
  Running libtoolize ...
  Running autoheader ...
  ...
  $ make -j 8
  ...

Ensure all is right with the world by running the built-in ``make check`` target:

.. code-block:: console

  $ make check
  Making check in src
  ...

Clone current flux-sched master:

.. code-block:: console

  $ git clone https://github.com/flux-framework/flux-sched.git
  Initialized empty Git repository in /home/fluxuser/flux-sched/.git/
  $ cd flux-sched

Build flux-sched. By default, flux-sched will attempt to configure against
flux-core found in the specified ``--prefix`` using the same
``PYTHON_VERSION``:

.. code-block:: console

  $ ./autogen.sh && ./configure --prefix=$HOME/local
  Running aclocal ...
  Running libtoolize ...
  Running autoheader ...
  ...
  $ make
  ...

Ensure all is right with the world by running the built-in ``make check`` target:

.. code-block:: console

  $ make check
  Making check in src
  ...

.. _starting-instance:

------------------------
Starting a Flux Instance
------------------------

In order to use Flux, you first must initiate a Flux *instance* or *session*.

A Flux session is composed of a hierarchy of ``flux-broker`` processes which are launched via any parallel launch utility that supports PMI. For example, ``srun``, ``mpiexec.hydra``, etc., or locally for testing via the ``flux start`` command.

Before a Flux instance can be started, keys must be generated to encrypt and authenticate Flux messages.  This step is only required for first-time users of flux.

.. code-block:: console

  $ flux keygen
  Saving /home/fluxuser/.flux/curve/client
  Saving /home/fluxuser/.flux/curve/client_private
  Saving /home/fluxuser/.flux/curve/server
  Saving /home/fluxuser/.flux/curve/server_private
  $

To start a Flux session with 4 brokers on the local node, use ``flux start``:

.. code-block:: console

  $ flux start --size=4
  $

A flux session can be also be started under `Slurm <https://github.com/chaos/slurm>`_ using PMI. To start by using ``srun(1)``, simply run the ``flux start`` command without the ``--size`` option under a Slurm job. You will likely want to start a single broker process per node:

.. code-block:: console

  $ srun -N4 -n4 --pty flux start
  srun: Job is in held state, pending scheduler release
  srun: job 1136410 queued and waiting for resources
  srun: job 1136410 has been allocated resources
  $

After broker wire up is completed, the Flux session starts an “initial program” on rank 0 broker. By default, the initial program is an interactive shell, but an alternate program can be supplied on the ``flux start`` command line. Once the initial program terminates, the Flux session is considered complete and brokers exit.

To get help on any ``flux`` subcommand or API program, the ``flux help`` command may be used. For example, to view the man page for the ``flux-hwloc(1)`` command, use

.. code-block:: console

  $ flux help hwloc

``flux help`` can also be run by itself to see a list of commonly used Flux commands.

.. _interacting:

-------------------------------
Interacting with a Flux Session
-------------------------------

There are several low-level commands of interest to interact with a Flux session. For example, to view the total resources available to the current instance, ``flux hwloc info`` may be used:

.. code-block:: console

  $ flux hwloc info
  4 Machines, 144 Cores, 144 PUs

The size, current rank, comms URIs, logging levels, as well as other instance parameters are termed “attributes” and can be viewed and manipulated with the ``lsattr``, ``getattr``, and ``setattr`` commands, for example.

.. code-block:: console

  $ flux getattr rank
  0
  $ flux getattr size
  4

The current log level is also an attribute and can be modified at runtime:

.. code-block:: console

  $ flux getattr log-level
  6
  $ flux setattr log-level 4  # Make flux quieter
  $ flux getattr log-level
  4

To see a list of all attributes and their values, use ``flux lsattr -v``.

Log messages from each broker are kept in a local ring buffer. When log level has been quieted, recent log messages for the local rank may be dumped via the ``flux dmesg`` command:

.. code-block:: console

  $ flux dmesg | tail -4
  2016-08-12T17:53:24.073219Z broker.info[0]: insmod cron
  2016-08-12T17:53:24.073847Z cron.info[0]: synchronizing cron tasks to event hb
  2016-08-12T17:53:24.075824Z broker.info[0]: Run level 1 Exited (rc=0)
  2016-08-12T17:53:24.075831Z broker.info[0]: Run level 2 starting

Services within a Flux session may be implemented by modules loaded in the ``flux-broker`` process on one or more ranks of the session. To query and manage broker modules, Flux provides a ``flux module`` command:

.. code-block:: console

  $ flux module list
  Module                   Size Digest  Idle  S Service
  job-exec              1274936 D83AE37    4  S
  job-manager           1331496 1F432DD    4  S
  kvs-watch             1299400 AA90CE6    4  S
  kvs                   1558712 7D8432C    0  S
  sched-simple          1241744 AA85006    4  S sched
  job-info              1348608 CA590E9    4  S
  barrier               1124360 DDA1A3A    4  S
  cron                  1202792 1B2DFD1    0  S
  connector-local       1110736 5AE480D    0  R
  job-ingest            1214040 19306CA    4  S
  userdb                1122432 0AA8778    4  S
  content-sqlite        1126920 EB0D5E9    4  S content-backing
  aggregator            1141184 5E1E0B6    4  S

The most basic functionality of these service modules can be tested with the ``flux ping`` utility, which targets a builtin ``*.ping`` handler registered by default with each module.

.. code-block:: console

  flux ping --count=2 kvs
  kvs.ping pad=0 seq=0 time=0.648 ms (1F18F!09552!0!EEE45)
  kvs.ping pad=0 seq=1 time=0.666 ms (1F18F!09552!0!EEE45)

By default the local (or closest) instance of the service is targeted, but a specific rank can be selected with the ``--rank`` option.

.. code-block:: console

  $ flux ping --rank=3 --count=2 kvs
  3!kvs.ping pad=0 seq=0 time=1.888 ms (CBF78!09552!0!1!3!BBC94)
  3!kvs.ping pad=0 seq=1 time=1.792 ms (CBF78!09552!0!1!3!BBC94)

The ``flux-ping`` utility is a good way to test the round-trip latency to any rank within a Flux session.

.. _flux-kvs:

--------
Flux KVS
--------

The key-value store (kvs) is a core component of a Flux instance. The ``flux kvs`` command provides a utility to list and manipulate values of the KVS. For example, hwloc information for the current instance is loaded into the kvs by the ``resource-hwloc`` module at instance startup. The resource information is available under the kvs key ``resource.hwloc``. For example, the count of total Cores available on rank 0 can be obtained from the kvs via:

.. code-block:: console

  $ flux kvs get resource.hwloc.by_rank
  {"[0-3]": {"NUMANode": 2, "Package": 2, "Core": 36, "PU": 36, "cpuset": "0-35"}}

See ``flux help kvs`` for more information.

.. _launching-work:

--------------------------------
Launching Work in a Flux Session
--------------------------------

Flux has two methods to launch “remote” tasks and parallel work within a session. The ``flux exec`` utility is a low-level remote execution framework which depends on as few other services as possible and is used primarily for testing. By default, ``flux exec`` runs a single copy of the provided ``COMMAND`` on each rank in a session:

.. code-block:: console

  $ flux exec flux getattr rank
  0
  3
  2
  1

Though individual ranks may be targeted:

.. code-block:: console

  $ flux exec -r 3 flux getattr rank
  3

The second method for launching and submitting jobs is a Minimal Job Submission Tool named "mini". The "mini" tool consists of a ``flux mini`` frontend command; ``flux job`` is another low-level tool that can be used for querying job information.

For a full description of the ``flux mini`` command, see ``flux help mini``.

* Run 4 copies of hostname.

.. code-block:: console

  $ flux mini run -n4 --label-io hostname
  3: quartz15
  2: quartz15
  1: quartz15
  0: quartz15

* Run an MPI job (for MPI that supports PMI).

.. code-block:: console

  $ flux mini run -n128 ./hello
  completed MPI_Init in 0.944s.  There are 128 tasks
  completed first barrier
  completed MPI_Finalize

* Run a job and immediately detach. (Since jobs are KVS based, jobs can run completely detached from any “front end” command.)

.. code-block:: console

  $ flux mini submit -n128 ./hello
  4095117099008

Here, the allocated ID for the job is immediately echoed to stdout.

* View output of a job.

.. code-block:: console

  $ flux job attach 4095117099008
  completed MPI_Init in 0.932s.  There are 128 tasks
  completed first barrier
  completed MPI_Finalize

* List jobs.

.. code-block:: console

  $ flux jobs
          JOBID USER        NAME       STATE    NTASKS NNODES  RUNTIME RANKS
  1378382512128 fluxuser    sleep      RUN           1      1   5.015s 0
  1355649384448 fluxuser    sleep      RUN           1      1   6.368s 0
