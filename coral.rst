.. _coral:

==============
CORAL Systems
==============

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

------------------
Launching Flux
------------------

You can load the latest Flux-team managed installation on LLNL and ORNL CORAL
machines using:

.. code-block:: sh

  module load flux

.. note::

  If you are using an installation of Flux that is not provided by the Flux
  team and that is configured without ``--enabled-pmix-bootstrap`` (e.g., a
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
  <https://github.com/openpmix/openpmix/issues/1396>`_ that causes a hang when
  using the PMI compatibility shim.

.. _coral_spectrum_mpi:

----------------------------------
Launching Spectrum MPI within Flux
----------------------------------

If you want to run MPI applications compiled with Spectrum MPI under Flux, then
one additional step is required.  When you run a Spectrum MPI binary under flux,
you must enable Flux's Spectrum MPI plugin.  From the CLI, this looks like:

.. code-block:: sh

  flux mini run -o mpi=spectrum my_mpi_binary

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

In addition, please refer to the manual page of the
`flux-mini(1) <https://flux-framework.readthedocs.io/projects/flux-core/en/latest/man1/flux-mini.html>`_
command to run or to submit an MPI job with a specific CPU/GPU set
and affinity using its shell options.
For example, to run a job at 4 MPI processes
each binding to 10 CPU cores and 1 GPU on a compute node:

.. code-block:: sh

  flux mini run -N 1 -n 4 -c 10 -g 1 -o mpi=spectrum -o cpu-affinity=per-task -o gpu-affinity=per-task my_mpi_binary
