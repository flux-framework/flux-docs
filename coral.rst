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

  module use /usr/global/tools/flux/blueos_3_ppc64le_ib/modulefiles

If you are using the ORNL system Summit, run:

.. code-block:: sh

  module use /sw/summit/modulefiles/ums/gen007flux/Core

------------------
Launching Flux
------------------

Launching Flux on CORAL systems requires a shim layer to provide `PMI
<https://www.mcs.anl.gov/papers/P1760.pdf>`_ on top of the PMIx interface
provided by the CORAL system launcher jsrun.  PMI is a common interface
for bootstrapping parallel applications like MPI, SHMEM, and Flux.  To load this
module along with our side-installed Flux, run:

.. code-block:: sh

  module load pmi-shim flux

We also suggest that you launch Flux using jsrun with the following arguments:

.. code-block:: sh

  PMIX_MCA_gds="^ds12,ds21" jsrun -a 1 -c ALL_CPUS -g ALL_GPUS -n ${NUM_NODES} --bind=none --smpiargs="-disable_gpu_hooks" flux start

The ``PMIX_MCA_gds`` environment variable works around `a bug in OpenPMIx
<https://github.com/openpmix/openpmix/issues/1396>`_ that causes a hang when
using the PMI compatibility shim.  The ``${NUM_NODES}`` variable is the number of
nodes that you want to launch the Flux instance across. The remaining arguments
ensure that all on-node resources are available to Flux for scheduling.

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

On all systems, Flux relies on hwloc to auto-detect the on-node resources
available for scheduling.  The hwloc that Flux is linked against must be
configured with ``--enable-cuda`` for Flux to be able to detect Nvidia GPUs.

If running on an LLNL CORAL system, you can load a CUDA-enabled hwloc with:

.. code-block:: sh

  module load hwloc/1.11.10-cuda

You can test to see if the hwloc that Flux is linked against is CUDA-enabled by
running:

.. code-block:: terminal

  $ flux start flux resource list
        STATE NNODES   NCORES    NGPUS
         free      1       40        4
    allocated      0        0        0
         down      0        0        0

If the number of free GPUs is 0, then the hwloc that Flux is linked against is
not CUDA-enabled.
