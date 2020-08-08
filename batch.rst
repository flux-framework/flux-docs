.. _batch:

==========
Batch Jobs
==========

In Flux, a batch job is a script submitted along
with a request for resources. When resources become
available, the script is run as the
`initial program <https://flux-framework.readthedocs.io/projects/flux-rfc/en/latest/spec_8.html#initial-program-program-1>`_ of a new single-user instance of Flux,
with the batch user as `instance owner <https://flux-framework.readthedocs.io/projects/flux-rfc/en/latest/spec_8.html#terminology>`_.
Thus, in contrast to a traditional batch scheduler, a Flux batch job
has access to fully featured resource manager instance, and may not only
serially execute work on allocated resources, but load custom modules
or customize parameters of existing modules, monitor
and update status of allocated resources, and even submit
more batch jobs to run further sub-instances of Flux.

.. note::
   In the following, batch jobs will be described using single-user Flux,
   but it is important to note that the same commands and techniques
   will also work at the system level.

----------------------------------
Launching Flux in Interactive Mode
----------------------------------

For this demonstration, we first launch Flux under SLURM and get an interactive shell.

.. code-block:: console

  $ salloc -N4 -ppdebug
  salloc: Granted job allocation 5620626
  $ srun -N ${SLURM_NNODES} 4 -n ${SLURM_NNODES} --pty --mpi=none --mpibind=off flux start

.. note::
   If launching under SLURM is not possible or convenient, a single-node
   single user instance of Flux can be started with ``flux start -s 4``.

------------------
Mini Batch Command
------------------

The high-level Flux command that users can use to submit a
batch script is ``flux mini batch``.

``sleep_batch.sh``:

.. code-block:: sh

  #!/bin/bash
  
  echo "Starting my batch job"
  echo "Print the resources allocated to this batch job"
  flux hwloc info
  
  echo "Use sleep to emulate a parallel program"
  echo "Run the program at a total of 4 processes each requiring"
  echo "1 core. These processes are equally spread across 2 nodes."
  flux mini run -N 2 -n 4 sleep 120
  flux mini run -N 2 -n 4 sleep 120

The name of your batch script is ``sleep_batch.sh``.
As shown from the ``flux mini run`` lines in this script, you can see the the
overall resource requirement is 4 cores equally spread
across two nodes as the default numbers of cores assigned to each task
(specified by the ``-n`` option) is just one.

We now submit this script interactively three times using ``flux mini batch``.

.. code-block:: console

  $ flux mini batch --nslots=2 --cores-per-slot=2 --nodes=2 ./sleep_batch.sh
  $ flux mini batch --nslots=2 --cores-per-slot=2 --nodes=2 ./sleep_batch.sh
  $ flux mini batch --nslots=2 --cores-per-slot=2 --nodes=2 ./sleep_batch.sh

Users must specify the overall resource requirement of each
job using ``--nslots``, which is the only required option, along with
other optional options including those describing the resource shape
of each slot and how the slots are distributed across different nodes.
In this example, each job requests two slots each with
2 cores (``--cores-per-slot=2``) and these slots must be equally spread
across two nodes (``--nodes=4``).

Currently, if you want a script to be exclusively allocated to a set of
nodes, the recommended option set is:
``--nslots=<NUM OF NODES>`` ``--cores-per-slot=<MAX NUM OF CORES PER NODE>``
and ``--nodes=<NUM OF NODES>``

.. note::
   Internally, Flux will create a nested Flux instance allocated
   to the requested resources per batch job and run the batch
   script inside that nested instance. While a batch script is
   expected to launch parallel jobs using ``flux mini run`` or
   ``flux mini submit`` at this level, nothing prevents the
   script from further batching other `sub-batch-jobs` using
   the ``flux mini batch`` interface, if desired.

You can check the status of these batch jobs:

.. code-block:: console

  $ flux jobs -a
     JOBID USER     NAME       ST NTASKS NNODES  RUNTIME RANKS
  ƒWZEQa8X dahn     sleep_batc  R      2      2   1.931s [0-1]
  ƒW8eCV2o dahn     sleep_batc  R      2      2   2.896s [0-1]
  ƒVhYLeJB dahn     sleep_batc  R      2      2   3.878s [0-1]

By default, the ``stdout``/``stderr`` of each batch job will be redirected
to the ``flux-${JOBID}.out`` file and you can easily change the name
of this file by passing ``--output=<FILE NAME1>``
and ``--error=<FILE NAME2>``.

Checking the output file of one of the batch job: 

.. code-block:: console

  $ flux job attach ƒWZEQa8X
  0: stdout redirected to flux-1125147213824.out
  0: stderr redirected to flux-1125147213824.out

  $ cat flux-1125147213824.out
  Print the resources allocated to this batch job
  2 Machines, 4 Cores, 8 PUs
  Use sleep to emulate a parallel program
  Run the program at a total of 4 processes each requiring
  1 core. These processes are equally spread across 2 nodes.


------------------------------------
Launching Flux in SLURM's Batch Mode
------------------------------------

Users may want to script the above procedures within a script
to submit to another resource manager such SLURM.

An example sbatch script:

.. code-block:: sh

  #!/bin/sh
  #SBATCH -N 4

  srun -N ${SLURM_NNODES} 4 -n ${SLURM_NNODES} --mpi=none --mpibind=off flux start flux_batch.sh

.. note::
   ``--pty`` is not used in this case because this option
   is known to produce a side effect in a non-interactive batch
   environment.

``flux_batch.sh``:

.. code-block:: sh

  #!/bin/sh
  flux mini batch --nslots=2 --cores-per-slot=2 --nodes=2 ./sleep_batch.sh
  flux mini batch --nslots=2 --cores-per-slot=2 --nodes=2 ./sleep_batch.sh
  flux mini batch --nslots=2 --cores-per-slot=2 --nodes=2 ./sleep_batch.sh
  flux queue drain


----------------------------------
Blocking and Non-blocking Commands
----------------------------------

It is important to note that some of the Flux commands used above are
blocking and some of them are non-blocking.

Both ``flux mini submit`` and ``flux mini batch`` have `submit` semantics
and as such they submit a parallel program or batch script and return
shortly after.
To avoid the exiting of the containing script, you can use
``flux queue drain`` which drains the queue such that no job can
be submitted and then waits until all submitted jobs complete.
Thus, it is recommended not to run those commands in background.

By contrast, ``flux mini run`` blocks until the target program
completes.


-----------------
Fluxion Scheduler
-----------------

With our Fluxion graph-based scheduler, users can easily specialize
their scheduling behaviors tailored to the characteristics
of their workloads.

As an example, we will describe how you can set the queue and backfill
policies of the submitting Flux to a simple policy named
`EASY <https://hal.archives-ouvertes.fr/hal-01522459/document>`_
while still keeping the policy of the nested Flux instances default:
First Come First Served (FCFS).

.. code-block:: console

  $ salloc -N4 -ppdebug
  salloc: Granted job allocation 5620626
  $ cat sched-fluxion-qmanager.toml
  [sched-fluxion-qmanager]

    queue-policy = "easy"

  $ srun -N ${SLURM_NNODES} 4 -n ${SLURM_NNODES} --pty --mpi=none --mpibind=off flux start -o,--config-path=./


``sched-fluxion-qmanager`` is the one of the modules from Fluxion and
``sched-fluxion-qmanager.toml`` in the current working directory is our TOML
configuration file that changes the queue/backfilling policy to EASY-backfilling.
This backfill-capable queue policy can significantly increase
the makespan of batch jobs.

.. note::
   Note that we pass the current working directory to ``-o,--config-path``
   so that Fluxion can use this TOML file in customizing its scheduling.
   This file will not affect any other nested Flux instances unless they
   are also passed with the same ``-o,--config-path`` option.
   
