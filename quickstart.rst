.. _quickstart:

============
Quick Start
============

A quick introduction to Flux and flux-core. If you are looking to see how Flux compares to your favorite resource manager, see :ref:`comparison-table`.
For reference, the :ref:`Glossary` contains definitions for a number of terms, Flux-specific concepts, and
acronyms mentioned in this guide and throughout our documentation site.

.. note::
   If your site runs Flux natively, you may wish to check with your help desk
   to see if you have a site-specific introduction to Flux, since Flux is
   configurable.  For example, LLNL has published an `Introduction to Flux
   <https://hpc-tutorials.llnl.gov/flux/>`_.  This document generally assumes
   you are exploring on your own.

.. _building-code:

-----------------
Building the Code
-----------------

.. _docker_installation:

^^^^^^
Docker
^^^^^^

    Recommended for quick, single-node deployments

Flux has a continuously updated Docker image available for download on
`Docker Hub <https://hub.docker.com/u/fluxrm>`_. If you already have docker
installed, just run the following to download the latest Flux docker image
and start a container from it:

.. code-block:: console

  $ docker run -ti fluxrm/flux-sched:latest
  $ flux getattr size
  1
  $ flux run printenv FLUX_JOB_ID
  2597498912768

.. note::
   Multi-node docker deployments of Flux is still an ongoing area of research.
   This installation method is recommended for developers and users curious to
   try single-node instances of Flux.

The default CMD for flux docker images is ``flux start /bin/bash``. To
emulate a multi-node deployment within a single container, replace the
default CMD by supplying args to ``docker run``:

.. code-block:: console

   $ docker run -ti fluxrm/flux-sched flux start --test-size 4
   $ flux getattr size
   4

Note that a more complete Docker tutorial is available at :ref:`flux-sched-container`.
If you are developing Flux and want to compile the modified code and run
our testsuite within a docker container, you can use our helper script:

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

.. _spack_installation:

^^^^^
Spack
^^^^^

    Recommended for curious users

Flux maintains an up-to-date package in the `spack
<https://github.com/spack/spack>`_ develop branch. If you’re already using
spack, just run the following to install flux and all necessary dependencies:

.. code-block:: console

  $ spack install flux-sched

The above command will build and install the latest tagged version of
flux-sched and flux-core.  To install the latest master branches, use the
``@master`` version specifier: ``spack install flux-sched@master``. If
you want Flux to manage and schedule Nvidia GPUs, include the ``+cuda``
variant: ``spack install flux-sched+cuda``.  This builds a CUDA-aware
version of hwloc.


For instructions on installing spack, see `Spack's installation documentation <https://spack.readthedocs.io/en/latest/getting_started.html>`_.

.. _manual_installation:

^^^^^^^^^^^^^^^^^^^
Manual Installation
^^^^^^^^^^^^^^^^^^^


   Recommended for developers and contributors

Ensure the latest list of requirements are installed. The
current list of build requirements are detailed `here <https://github.com/flux-framework/flux-core?tab=readme-ov-file#build-requirements>`_.

Clone current flux-core master:

.. code-block:: console

  $ git clone https://github.com/flux-framework/flux-core.git
  Initialized empty Git repository in /home/fluxuser/flux-core/.git/
  $ cd flux-core

Build flux-core. In order to build python bindings, ensure you have
python-3.6 and python-cffi available in your current environment:

.. code-block:: console

  $ ./autogen.sh && ./configure --prefix=$HOME/local
  Running aclocal ...
  Running libtoolize ...
  Running autoheader ...
  ...
  $ make -j 8
  ...

Ensure all is right with the world by running the built-in ``make check``
target:

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

Ensure all is right with the world by running the built-in ``make check``
target:

.. code-block:: console

  $ make check
  Making check in src
  ...

.. _starting-instance:

------------------------
Starting a Flux Instance
------------------------

In order to use Flux, you first must initiate a Flux *instance*.

A Flux instance is composed of a group of :ref:`flux-broker<flux-broker>` processes
which are launched via any parallel launch utility that supports :ref:`PMI<pmi>`. For
example, ``srun``, ``mpiexec.hydra``, etc., or locally for testing via the
``flux start`` command with the ``-s, --test-size=N`` option.

To start a Flux instance with 4 brokers on the local node, use ``flux start``:

.. code-block:: console

  $ flux start --test-size=4
  $

A Flux :ref:`instance<flux-instance>` can be also be started under `Slurm
<https://github.com/chaos/slurm>`_ using PMI. To start by using ``srun(1)``,
simply run the ``flux start`` command without the ``--test-size`` option under
a Slurm job. You will likely want to start a single broker process per node:

.. code-block:: console

  $ srun -N4 -n4 --pty flux start
  srun: Job is in held state, pending scheduler release
  srun: job 1136410 queued and waiting for resources
  srun: job 1136410 has been allocated resources
  $

An interactive Flux instance can also be started under Flux with
:core:man1:`flux-alloc`:

.. code-block:: console

  $ flux alloc -n144 -N4
  $

.. note::
  ``flux alloc`` requires the ``-n, --nslots=N`` parameter, which by
  default will allocate 1 core per slot. The command above will request
  to allocate 144 core across 4 nodes (for example, for a system with
  36 cores)

After broker wire up is completed, the Flux instance starts an “initial
program” on rank 0 broker. By default, the initial program is an
interactive shell, but an alternate program can be supplied on the ``flux
start`` command line. Once the initial program terminates, the Flux instance
is considered complete and brokers exit.

To get help on any ``flux`` subcommand or API function, the ``flux
help`` command may be used. For example, to view the man page for the
``flux-top(1)`` command, use

.. code-block:: console

  $ flux help top

``flux help`` can also be run by itself to see a list of commonly used
Flux commands.

.. _interacting:

-------------------------------
Interacting with a Flux Session
-------------------------------

There are several low-level commands of interest to interact with a Flux
instance. For example, to view the total resources available in the current
instance, ``flux resource status`` may be used:

.. code-block:: console

  $ flux resource status
      STATUS NNODES RANKS           NODELIST
       avail      4 0-3             quartz[2306,2306,2306,2306]


To view the scheduling state of resources use ``flux resource list``:

.. code-block:: console

  $ flux resource list
       STATE NNODES   NCORES    NGPUS NODELIST
        free      4      144        0 quartz[2306,2306,2306,2306]
   allocated      0        0        0
        down      0        0        0

.. note::
  Since we are running a test instance with 4 brokers on the same host
  via the ``--test-size=4`` option, those hosts are repeated in the
  ``NODELIST`` above. This allows Flux to simulate a multi-node cluster
  on a single node.

The size, broker rank, URIs, logging levels, as well as other instance
parameters are termed “broker attributes” and can be viewed and manipulated
with the ``lsattr``, ``getattr``, and ``setattr`` commands, for example. For
a description of all attributes see :core:man7:`flux-broker-attributes`

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

Attributes are per-broker so to set or get a value on a different broker
rank or across the entire instance ``flux getattr`` or ``flux setattr``
should be run via :core:man1:`flux-exec`.

To see a list of all attributes and their values, use ``flux lsattr -v``.

Log messages from each broker are kept in a local ring buffer. Recent log
messages for the local rank may be dumped via the ``flux dmesg`` command:

.. code-block:: console

  $ flux dmesg | tail -4
  2016-08-12T17:53:24.073219Z broker.info[0]: insmod cron
  2016-08-12T17:53:24.073847Z cron.info[0]: synchronizing cron tasks to event hb
  2016-08-12T17:53:24.075824Z broker.info[0]: Run level 1 Exited (rc=0)
  2016-08-12T17:53:24.075831Z broker.info[0]: Run level 2 starting

Services within a Flux instance may be implemented by modules loaded in the
``flux-broker`` process on one or more ranks of the instance. To query and
manage broker modules, Flux provides a ``flux module`` command:

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

The most basic functionality of these service modules can be tested with
the :core:man1:`flux-ping` utility, which targets a builtin ``*.ping`` handler
registered by default with each module.

.. code-block:: console

  $ flux ping --count=2 kvs
  kvs.ping pad=0 seq=0 time=0.402 ms (2da0be18!301c7e16!3e4f235f!9cea08f1)
  kvs.ping pad=0 seq=1 time=0.307 ms (2da0be18!301c7e16!3e4f235f!9cea08f1)


.. _flux-kvs:

--------
Flux KVS
--------

The :ref:`kvs<kvs>` (Key-Value Store) is a core component of a Flux instance. The
``flux kvs`` command provides a utility to list and manipulate values of
the KVS. For example, resource information for the current instance is loaded
into the kvs by the ``resource`` module at instance startup. The
resource information is available under the kvs key ``resource.R``. For
example, the count of total Cores available on rank 0 can be obtained from
the kvs via:

.. code-block:: console

  $ flux kvs get resource.R
  {"version": 1, "execution": {"R_lite": [{"rank": "0-3", "children": {"core": "0-35"}}], "starttime": 0.0, "expiration": 0.0, "nodelist": ["quartz[2306,2306,2306,2306]"]}}

See ``flux help kvs`` for more information.

.. _launching-work:

--------------------------------
Launching Work in a Flux Session
--------------------------------

Flux has two methods to launch “remote” tasks and parallel work within
a instance. The ``flux exec`` utility is a low-level remote execution
framework which depends on as few other services as possible and is used
primarily for testing. By default, ``flux exec`` runs a single copy of
the provided ``COMMAND`` on each rank in a instance:

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

The second method for launching work is using one of the Flux job submission
tools:

 * :core:man1:`flux-run` - interactively run jobs
 * :core:man1:`flux-submit` - enqueue one or more jobs
 * :core:man1:`flux-batch` - enqueue a batch script
 * :core:man1:`flux-alloc` - allocate a new instance for interactive use
 * :core:man1:`flux-bulksubmit` - enqueue jobs in bulk

* Run 4 copies of hostname.

.. code-block:: console

  $ flux run -n4 --label-io hostname
  3: quartz15
  2: quartz15
  1: quartz15
  0: quartz15

* Run an MPI job (for MPI that supports PMI).

.. code-block:: console

  $ flux run -n128 ./hello
  completed MPI_Init in 0.944s.  There are 128 tasks
  completed first barrier
  completed MPI_Finalize

* Run a job and immediately detach. (Since jobs are KVS based, jobs can run completely detached from any “front end” command.)

.. code-block:: console

  $ flux submit -n128 ./hello
  ƒA6oPHNjh

Here, the allocated ID for the job is immediately echoed to stdout.

The ``flux job`` command also includes many subcommands which are useful,
including

* View output of a job.

.. code-block:: console

  $ flux job attach ƒA6oPHNjh
  completed MPI_Init in 0.932s.  There are 128 tasks
  completed first barrier
  completed MPI_Finalize

* Cancel a pending or running job, or send a signal to a running job

.. code-block:: console

  $ flux cancel ƒMjstRfzF

or

.. code-block:: console

  $ flux job kill ƒMjstRfzF

* Active jobs can be listed with :core:man1:`flux-jobs`:

.. code-block:: console

  $ flux jobs
       JOBID USER     NAME       ST NTASKS NNODES  RUNTIME NODELIST
   ƒPugMu2Ty fluxuser sleep       R      1      1   1.564s quartz2306
   ƒPugLR3Bd fluxuser sleep       R      1      1   1.565s quartz2306

* To include jobs which have completed for the current user add the
  ``-a`` option

.. code-block:: console

  $ flux jobs -a
       JOBID USER     NAME       ST NTASKS NNODES  RUNTIME NODELIST
   ƒPugMu2Ty fluxuser sleep       R      1      1   1.564s quartz2306
   ƒPugLR3Bd fluxuser sleep       R      1      1   1.565s quartz2306
    ƒP55Ntdd fluxuser sleep      CD      1      1   4.052s quartz2306
    ƒ8QzNhZh fluxuser hostname   CD      1      1   0.053s quartz2306

By default ``flux jobs -a`` will list up to 1000 jobs. To limit output
use the ``-c, --count=N`` option.
