.. _faqs:

==========
FAQs
==========
Some frequently asked questions about flux and their answers.

.. _flux_run_mac:

-----------------------
Does flux run on a mac?
-----------------------

Not yet. We have an open `issue <https://github.com/flux-framework/flux-core/issues/2892>`_
on GitHub tracking the progress towards the goal of natively compiling on a
mac. In the meantime, you can use Docker, see: :ref:`quickstart`.

.. _bug_report_how:

----------------------
How do I report a bug?
----------------------

You can read up on reporting bugs here: :ref:`contributing` or report one
directly for flux `core <https://github.com/flux-framework/flux-core/issues>`_
or `sched <https://github.com/flux-framework/flux-sched/issues>`_.

.. _not_managing_all_resources:

---------------------------------------------------------------------------------
Why is Flux not discovering and managing all of the resources on the system/node?
---------------------------------------------------------------------------------

This can be due to various bind flags that need to be passed parallel launcher
that started Flux. For example at LLNL you must pass ``--mpibind=off`` to
``srun`` and ``--bind=none`` to ``jsrun``.

Also on all systems, Flux relies on hwloc to auto-detect the on-node resources
available for scheduling.  The hwloc that Flux is linked against must be
configured with ``--enable-cuda`` for Flux to be able to detect Nvidia GPUs.

You can test to see if your system default hwloc is CUDA-enabled with:

.. code-block:: sh

  lstopo | grep CoProc

If no output is produced, then your hwloc is not CUDA-enabled.

.. _launch_large_num_jobs:

------------------------------------------------------------
How do I efficiently launch a large number of jobs to Flux?
------------------------------------------------------------

See `bulksubmit.py <https://github.com/flux-framework/flux-workflow-examples/tree/master/async-bulk-job-submit>`_
for an example workflow or flux `tree <https://github.com/flux-framework/flux-sched/blob/master/src/cmd/flux-tree>`_.

.. _node_memory_exhaustion:

------------------------------------------------------------------
Memory exhaustion on a node when running large ensembles with Flux
------------------------------------------------------------------

Flux's in-memory KVS is backed by an on-disk content store.  The default
location for the content store is ``/tmp``, which for some systems is
configured as a RAMDisk.  To minimize Flux's memory footprint at the cost
of a slower content store, set ``rundir`` so that the content store is not
saved to ``/tmp`` but to filesystem.  An example command to set the ``rundir``
could look like:

.. code-block:: sh

    flux start -o,-Srundir=/path/to/rundir

.. _mimic_slurm_jobstep:

-------------------------------------------
How do I mimic Slurm's job step semantics ?
-------------------------------------------

Using ``flux mini submit`` to submit a script containing multiple
``flux mini run`` invocations will not result in Slurm-style job steps unless
the job script is prefixed with ``flux start`` .

.. _mpi_bootstrap_fails:

----------------------------------------------------------------------------------------------
Flux is failing to bootstrap a specific MPI implementation (e.g. OpenMPI, MPICH, Spectrum MPI)
----------------------------------------------------------------------------------------------

Flux's shell plugins for Intel MPI, MVAPICH, and OpenMPI run by default with
every job. If you experience any issues bootstrapping these MPIs, use the
``flux mini run/submit -o mpi=`` option when running or submitting, or
please open an issue: :ref:`bug_report_how`


For Spectrum MPI follow the instructions here: :ref:`coral_spectrum_mpi`

.. _message_callback_not_run:

-----------------------------------------------------
My message callback is not being run. How do I debug?
-----------------------------------------------------

* Check the error codes from ``flux_msg_handler_addvec``,
  ``flux_register_service``, ``flux_rpc_get``, etc
* Use ``FLUX_O_TRACE`` and ``FLUX_HANDLE_TRACE`` to see messages moving
  through the overlay
* ``FLUX_HANDLE_TRACE`` is set when starting a Flux instance:
  ``FLUX_HANDLE_TRACE=t flux start``
* ``FLUX_O_TRACE`` is passed as a flag to
  `flux_open <https://github.com/flux-framework/flux-core/blob/9822c63f5e6edf329ab3efb9ce3b8bfe5811e8ab/doc/man3/flux_open.adoc>`_

.. _parallel_run_hang:

-------------------------------------------------------------------------------
I'm experiencing a hang while running my parallel application. How can I debug?
-------------------------------------------------------------------------------

* Run ``flux mini run/submit`` with the ``-vvv`` argument
* If it is hanging in startup, try adding the ``PMI_DEBUG`` environment
  variable: ``PMI_DEBUG=t flux mini run my_app.exe``

.. _versioning_multi_repo:

-------------------------------------------------------------------
How does the versioning of Flux work with its multi-repo structure?
-------------------------------------------------------------------

For any given repository, the versioning is typical semantic `versioning <https://semver.org/>`_.
All of the Flux repos are still < v1.0, so all of our interfaces are subject
to change. Once a repo hits v1.0, the interfaces for that repo will only break
backwards compatibility on major version increments. New features get added in
minor releases. Etc

The interesting part of the versioning comes from the multi-repo structure.
Flux-sched is it's own repo with it's own versioning scheme. A release on
flux-core may not break anything in flux-sched or require changes and thus
might not warrant a new release. So the flux-core and flux-sched versions do
not get incremented in lockstep. Already as of June 2020, flux-core is on
0.16.0 and flux-sched is on 0.8.0. We have the compatibility of the various
flux-core/flux-sched versions codified in our
`spack packages <https://github.com/spack/spack/blob/5108fe314b92409027c2821698fabb62c0ec3b5d/var/spack/repos/builtin/packages/flux-sched/package.py>`_,
and that will get more extensive as we add additional repos like flux-depend
and flux-accounting.

A 'flux' meta-package (such as in spack or distro package managers) that would
pull in compatible versions of the various sub-packages/repos is also versioned
independently of any of its subcomponents. It is a similar situation for the
flux-docs repo and the documentation up on readthedocs. Each repo has it's own
documentation and that gets tagged and released along with the code, but the
high-level "meta" documentation has it's own versioning that is divorced from
any particular sub-packages/repos versioning.

.. TODO: we should make a table and put it in the docs too

----------------------------------------
What versions of OpenMPI work with Flux?
----------------------------------------

Flux plugins were added to OpenMPI 3.0.0.  Generally, these plugins enable
OpenMPI major versions 3 and 4 to work with Flux.  OpenMPI must be configured
with the Flux plugins enabled.  Your installed version may be checked with:

.. code-block:: console

 $ ompi_info|grep flux
                 MCA pmix: flux (MCA v2.1.0, API v2.0.0, Component v4.0.3)
               MCA schizo: flux (MCA v2.1.0, API v1.0.0, Component v4.0.3)

Unfortunately, `an OpenMPI bug <https://github.com/open-mpi/ompi/issues/6730>`_
broke the Flux plugins in OpenMPI versions 3.0.0-3.0.4, 3.1.0-3.1.4, and
4.0.0-4.0.1.  The `fix <https://github.com/open-mpi/ompi/pull/6764/commits/d4070d5f58f0c65aef89eea5910b202b8402e48b>`_
was backported such that the 3.0.5+, 3.1.5+, and 4.0.2+ series do not
experience this issue.

A slightly different `OpenMPI bug <https://github.com/open-mpi/ompi/pull/8380>`_
caused segfaults of MPI in ``MPI_Finalize`` when UCX PML was used.
`The fix <https://github.com/open-mpi/ompi/pull/8380>`_ was backported to
4.0.6 and 4.1.1.  If you are using UCX PML in OpenMPI, we recommend using
4.0.6+ or 4.1.1+.

A special `job shell plugin <https://github.com/flux-framework/flux-pmix>`_,
offered as a separate package, is required to bootstrap the upcoming openmpi
5.0.x releases.  Once installed, the plugin is activated by submitting a job
with the ``-ompi=openmpi@5`` option.
