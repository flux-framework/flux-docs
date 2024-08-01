.. _coral:

===============================
CORAL: Flux launched by IBM LSF
===============================

The LLNL and ORNL `CORAL systems <https://asc.llnl.gov/CORAL/>`_
Lassen, Sierra, and Summit are pre-exascale supercomputers built by IBM.  They
run a specialized software stack that requires additional components to
integrate properly with Flux.  These components are provided as `Lmod
<https://lmod.readthedocs.io/en/latest/>`_ modules on all three systems.

To setup your environment to use these modules on the LLNL systems Lassen and
Sierra, run:

.. code-block:: sh

  module use /usr/tce/modulefiles/Core # if not already in use
  module use /usr/global/tools/flux/blueos_3_ppc64le_ib/modulefiles

If you are using the ORNL system Summit, run:

.. code-block:: sh

  module use /sw/summit/modulefiles/ums/gen007flux/linux-rhel8-ppc64le/Core


.. _launch-flux-on-lassen:

--------------
Launching Flux
--------------

You can load the latest Flux-team managed installation on LLNL and ORNL CORAL
machines using:

.. code-block:: sh

  module load flux

.. note::

  If you are using an installation of Flux that is not provided by the Flux
  team and that is configured without ``--enable-pmix-bootstrap`` (e.g., a
  spack-installed Flux), launching it on CORAL systems requires a shim layer to
  provide `PMI <https://www.mcs.anl.gov/papers/P1760.pdf>`_ on top of the PMIx
  interface provided by the CORAL system launcher ``jsrun``. To load this module
  alongside your side-installed Flux, run ``module load pmi-shim``.

We also suggest that you launch Flux using ``jsrun`` with the following arguments:

.. code-block:: sh

  jsrun -a 1 -c ALL_CPUS -g ALL_GPUS -n ${NUM_NODES} --bind=none --smpiargs="-disable_gpu_hooks" flux start

The ``${NUM_NODES}`` variable is the number of nodes that you want to launch
the Flux instance across. The remaining arguments ensure that all on-node
resources are available to Flux for scheduling.

.. note::

  If you are using the ``pmi-shim`` module mentioned above, you will need to set
  ``PMIX_MCA_gds="^ds12,ds21"`` in your environment before calling ``jsrun``. The
  ``PMIX_MCA_gds`` environment variable works around `a bug in OpenPMIx
  <https://github.com/openpmix/pmi-shim/issues/3>`_ that causes a hang when
  using the PMI compatibility shim.

.. _coral_spectrum_mpi:

----------------------------------
Launching Spectrum MPI within Flux
----------------------------------

If you want to run MPI applications compiled with Spectrum MPI under Flux, then
one additional step is required.  When you run a Spectrum MPI binary under flux,
you must enable Flux's Spectrum MPI plugin.  From the CLI, this looks like:

.. code-block:: sh

  flux run -o mpi=spectrum my_mpi_binary

From the Python API, this looks like::

  #!/usr/bin/env python3

  import os
  import flux
  from flux import job

  fh = flux.Flux()

  jobspec = job.JobspecV1.from_command(['my_mpi_binary'])
  jobspec.environment = dict(os.environ)
  jobspec.setattr_shell_option('mpi', 'spectrum')

  jobid = job.submit(fh, jobspec)
  print(jobid)

---------------
Scheduling GPUs
---------------

On all systems, Flux relies on ``hwloc`` to auto-detect the on-node resources
available for scheduling.  The ``hwloc`` that Flux is linked against must be
configured with ``--enable-cuda`` for Flux to be able to detect Nvidia GPUs.

The LLNL and ORNL CORAL ``flux`` modules automatically loads an ``hwloc`` configured
against a system-provided ``cuda``.

For all systems, you can test to see if the ``hwloc`` that Flux is linked against
is CUDA-enabled by running:

.. code-block:: console

  $ flux start flux resource list
        STATE NNODES   NCORES    NGPUS
         free      1       40        4
    allocated      0        0        0
         down      0        0        0

If the number of free GPUs is 0, then the ``hwloc`` that Flux is linked against is
not CUDA-enabled.

In addition, please refer to :core:man1:`flux-run` or :core:man1:`flux-submit`
to run or to submit an MPI job with a specific CPU/GPU set
and affinity using its shell options.
For example, to run a job at 4 MPI processes
each binding to 10 CPU cores and 1 GPU on a compute node:

.. code-block:: sh

  flux run -N 1 -n 4 -c 10 -g 1 -o mpi=spectrum -o cpu-affinity=per-task -o gpu-affinity=per-task my_mpi_binary

----------------------------
Launching Flux Interactively
----------------------------

CORAL systems use IBM's Spectrum LSF scheduler which, unlike Slurm, does not support running ``jsrun`` commands in a pseudo-
terminal. This limits users' ability to run Flux sessions interactively.

A workaround for this is to submit a script to run Flux for some amount of time as a job, and then connect to that Flux session
remotely by resolving the URI. Below is an example script to create a 2 node Flux session in the debug queue, which will run for
two hours. 

.. code-block:: sh
  
  #!/bin/bash
  #BSUB -q pdebug
  #BSUB -W 120
  #BSUB -nnodes 3
  #BSUB -J fluxsesh

  module use /usr/tce/modulefiles/Core
  module use /usr/global/tools/flux/blueos_3_ppc64le_ib/modulefiles
  module load pmi-shim

  PMIX_MCA_gds="^ds12,ds21" jsrun -a 1 -c ALL_CPUS -g ALL_GPUS -n 3 --bind=none --smpiargs="-disable_gpu_hooks" flux start sleep inf

When this is submitted, the system will print out a job ID. You can check the status of the job with ``bjobs``:

.. code-block:: sh
  
  [elvis@lassen709:~]$ bsub < flux_session_submit.sh 
  Job <3750480> is submitted to queue <pdebug>.
  ...
  [elvis@lassen709:~]$ bjobs
  JOBID      USER    STAT  QUEUE      FROM_HOST   EXEC_HOST   JOB_NAME   SUBMIT_TIME
  3750480    elvis   RUN   pdebug     lassen709   1*launch_ho fluxsesh   Jul 25 12:44
                                                  80*debug_hosts

Once the job starts to run, you can resolve the URI, and connect to the session remotely.

.. code-block:: sh
  
  [elvis@lassen709:~]$ flux uri --remote lsf:3750480
  ssh://lassen32/var/tmp/flux-aXQh0w/local-0

  [elvis@lassen709:~]$ flux proxy ssh://lassen32/var/tmp/flux-aXQh0w/local-0
  [elvis@lassen709:~]$ flux resource list
       STATE NNODES   NCORES    NGPUS NODELIST
        free      2       80        0 lassen[32,34]
   allocated      0        0        0 
        down      0        0        0 

.. note::

  In order to connect to remote sessions via ``flux proxy`` SSH keys must be configured. `To set up SSH keys on Livermore 
  Computing resources, see this Confluence article (login required). <https://lc.llnl.gov/confluence/display/SIERRA/Quickstart+Guide>`_
