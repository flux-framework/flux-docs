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

Flux maintains an up-to-date package in the `spack <https://github.com/spack/spack>`_ develop branch, which builds all dependencies and flux itself from the current head of the master branch. If you’re already using spack, just run the following to install flux and all necessary dependencies:

.. code-block:: console

  $ spack install flux

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Manual: Recommended for developers and contributors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ensure the latest list of requirements are installed. The currrent list of build requirements are detailed `here <http://flux-framework.org/docs/requirements/>`_.

Clone current flux-core master:

.. code-block:: console

  $ git clone https://github.com/flux-framework/flux-core.git
  Initialized empty Git repository in /g/g0/grondo/flux-core/.git/
  $ cd flux-core

Build flux-core. In order to build python bindings, ensure you have python-3.6 and python-cffi available in your current environment:

.. code-block:: console

  $ module load python/3.6 python-cffi python-pycparser
  $ ./autogen.sh && ./configure
  Running aclocal ...
  Running libtoolize ...
  Running autoheader ...
  ...
  $ make -j 8
  ...

.. note::
   Flux still supports python-2.7, but we recommend that you use python-3.6 or higher
   as the Python community will stop maintaining this version in 2020.

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

To start a Flux session with 4 brokers on the local node, use ``flux start``:

.. code-block:: console

  $ src/cmd/flux start --size=4
  $

A flux session can be also be started under `Slurm <https://github.com/chaos/slurm>`_ using PMI. To start by using ``srun(1)``, simply run the ``flux start`` command without the ``--size`` option under a Slurm job. You will likely want to start a single broker process per node:

.. code-block:: console

  $ srun -N4 -n4 --pty src/cmd/flux start
  srun: Job is in held state, pending scheduler release
  srun: job 1136410 queued and waiting for resources
  srun: job 1136410 has been allocated resources
  $

After broker wireup is completed, the Flux session starts an “initial program” on rank 0 broker. By default, the initial program is an interactive shell, but an alternate program can be supplied on the ``flux start`` command line. Once the initial program terminates, the Flux session is considered complete and brokers exit.

By default, Flux sets the initial program environment such that the ``flux(1)`` command that was used to start the session is found first in ``PATH``, so within the initial program shell, running ``flux`` will work as expected:

.. code-block:: console

  $ flux
  Usage: flux [OPTIONS] COMMAND ARGS
    -h, --help             Display this message
    -v, --verbose          Be verbose about environment and command search
  [snip]
  $

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

  $ flux module list --rank=all
  Module                   Size Digest  Idle  S   Nodeset Service
  job-ingest            1143808 AF0B59E    4  S     [0-2]
  cron                  1150080 4734B87    0  S         0
  connector-local       1058616 30B79F6    0  R     [0-2]
  resource             15996328 C5E139A    3  S         0
  qmanager               841040 D40C2E0    3  S         0 sched
  userdb                1066296 56B5D15    4  S         0
  content-sqlite        1074088 7098AD8    0  S         0 content-backing
  job-manager           1200296 D97A9A2    3  S         0
  kvs                   1485416 23988F3    0  S     [0-2]
  kvs-watch             1231456 4F4618B    0  S     [0-2]
  job-info              1178896 CEB665F    4  S     [0-2]
  barrier               1067888 8AEA814    4  S     [0-2]
  aggregator            1085000 D967157    0  S     [0-2]
  job-exec              1176856 CED941E    4  S         0

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

  $ flux job list
    JOBID           STATE   USERID    PRI   T_SUBMIT
    640671547392    R       58985     16    2019-10-22T16:27:02Z
    1045388328960   R       58985     16    2019-10-22T16:27:26Z
