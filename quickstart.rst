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

Build flux-core. In order to build python bindings ensure you have python-2.7 and python-cffi available in your current environment:

.. code-block:: console

  $ module load python/2.7 python-cffi python-pycparser 
  $ ./autogen.sh && ./configure 
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
  ==================================================================
  Testsuite summary for flux-core 0.4.0-8-gf289387
  ==================================================================
  # TOTAL: 1016
  # PASS:  1002
  # SKIP:  11
  # XFAIL: 3
  # FAIL:  0
  # XPASS: 0
  # ERROR: 0
  ==================================================================

.. _starting-instance:

------------------------
Starting a Flux Instance
------------------------

In order to use Flux you first must initiate a Flux instance or session.

A Flux session is composed of a hierarchy of ``flux-broker`` processes which are launched via any parallel launch utility that supports PMI. For example, ``srun``, ``mpiexec.hydra``, etc., or locally for testing via the ``flux start`` command.

To start a Flux session with 4 brokers on the local node, use ``flux start``:

.. code-block:: console

  $ src/cmd/flux start --size=4
  $

A flux session can be also be started under Slurm using PMI. To start by using ``srun(1)``, simply run the ``flux start`` command without the ``--size`` option under a Slurm job. You will likely want to start a single broker process per node:

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

To get help on any ``flux`` subcommand or API program, the ``flux help`` command may be used. For example, to view the man page for the ``flux-up(1)`` command, use

.. code-block:: console

  $ flux help up

.. _interacting:

-------------------------------
Interacting with a Flux Session
-------------------------------

There are several low-level commands of interest to interact with a Flux sessions. For example, to view states of broker ranks within the current session, ``flux up`` may be used:

.. code-block:: console

  $ flux up
  ok:     [0-3]
  slow:   
  fail:   
  unknown:

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
  Module               Size    Digest  Idle  S  Nodeset
  resource-hwloc       1139648 B1667DA    3  S  [0-3]
  barrier              1129400 578B987    3  S  [0-3]
  wrexec               1113904 87533D1    3  S  [0-3]
  cron                 1251072 CEB59B2    0  S  0
  kvs                  1306016 FF5317C    0  S  [0-3]
  content-sqlite       1131312 1B81581    3  S  0
  connector-local      1141848 65DB17D    0  R  [0-3]
  job                  1125968 2D10694    3  S  [0-3]

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

The key-value store (kvs) is a core component of a Flux instance. The ``flux kvs`` command provides a utility to list and manipulate values of the KVS. For example, hwloc information for the current instance is loaded into the kvs by the ``resource-hwloc`` module at instance startup. The resource information is available under the kvs key ``resource.hwloc`` For example, the count of total Cores available on rank 0 can be obtained from the kvs via:

.. code-block:: console

  $ flux kvs get resource.hwloc.by_rank.0.Core
  16

See ``flux help kvs`` for more information.

.. _lauching-work:

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

To view processes launched using ``flux exec``, a ``flux ps`` program is provided:

.. code-block:: console

  $ flux exec sleep 100 &
  [1] 161298
  $ $ flux ps
  OWNER     RANK       PID  COMMAND
  none         0    111760  /bin/bash
  8E20D        0    162394  sleep
  8E20D        3    162395  sleep
  8E20D        2    162396  sleep
  8E20D        1    162397  sleep

The ``OWNER`` field refers to a UUID of the requesting entity in the system not a user identity.

The second method for launching parallel jobs is a prototype based on use of the Flux KVS for parallel job management termed “WRECK”. The wreck prototype consists of a ``flux wreckru``n frontend command, and a ``flux wreck`` utility for operating and querying jobs run under the prototype.

For a full description of the ``flux wreckrun`` command, see ``flux help wreckrun``.

* Run 4 copies of hostname.

.. code-block:: console

  $ flux wreckrun -n4 --label-io hostname
  0: hype346
  2: hype349
  1: hype347
  3: hype350

* Run an MPI job (for MPI that supports PMI).

.. code-block:: console

  $ flux wreckrun -n128 ./hello
  0: completed MPI_Init in 0.944s.  There are 128 tasks
  0: completed first barrier
  0: completed MPI_Finalize

* Run a job and immediately detach. (Since jobs are KVS based, jobs can run completely detached from any “front end” command.)

.. code-block:: console

  $ flux wreckrun --detach -n128 ./hello
  7

Here, the allocated ID for the job is immediately echoed to stdout.

* View output of a job.

.. code-block:: console

  $ flux wreck attach 7
  0: completed MPI_Init in 0.932s.  There are 128 tasks
  0: completed first barrier
  0: completed MPI_Finalize

* Get status of a completed job.

.. code-block:: console

  $ flux wreck status 7
  Job 7 status: complete
  task[0-127]: exited with exit code 0

* List jobs.

.. code-block:: console

  $ flux wreck ls
      ID NTASKS STATE                    START      RUNTIME    RANKS COMMAND
       1      1 complete   2015-11-20T10:18:37       0.101s        0 hostname
       2      1 complete   2015-11-20T10:18:53       0.019s        0 hsotname
       3      1 complete   2015-11-20T10:19:00       0.014s        0 hostname
       4      4 complete   2015-11-20T10:19:05       0.105s    [0-3] hostname
       5      4 complete   2015-11-20T10:21:29       2.394s    [0-3] hello
       6    128 complete   2015-11-20T10:22:09       3.269s    [0-3] hello
       7    128 complete   2015-11-20T10:23:41       3.381s    [0-3] hello
