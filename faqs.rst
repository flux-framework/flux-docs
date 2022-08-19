.. _faqs:

####
FAQs
####

Some frequently asked questions about flux and their answers.

.. _flux_run_mac:


*****************
General Questions
*****************

Does flux run on a mac?
=======================

Not yet. We have an open `issue <https://github.com/flux-framework/flux-core/issues/2892>`_
on GitHub tracking the progress towards the goal of natively compiling on a
mac. In the meantime, you can use Docker, see: :ref:`quickstart`.

.. _bug_report_how:

How do I report a bug?
======================

You can read up on reporting bugs here: :ref:`contributing` or report one
directly for flux `core <https://github.com/flux-framework/flux-core/issues>`_
or `sched <https://github.com/flux-framework/flux-sched/issues>`_.

.. _not_managing_all_resources:

Why is Flux not discovering and managing all of the resources on the system/node?
=================================================================================

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

How do I efficiently launch a large number of jobs to Flux?
===========================================================

See `bulksubmit.py <https://github.com/flux-framework/flux-workflow-examples/tree/master/async-bulk-job-submit>`_
for an example workflow. You can also submit many copies of the same job using
``flux mini submit --cc=IDSET``, or submit many jobs based on a series of
inputs on ``stdin`` or the command line via ``flux mini bulksubmit``. See the
`flux-mini <https://flux-framework.readthedocs.io/projects/flux-core/en/latest/man1/flux-mini.html#bulksubmit>`_
manual page for more details.


.. _overcommit_resources:

How can I oversubscribe tasks to resources in Flux?
===================================================

There is no ``--overcommit`` or similar option for Flux at this time.
However, there are several different ways to accomplish something similar,
depending on what you want to do.

If you simply want to oversubscribe tasks to resources, you can use the
``per-resource.`` job shell option. This will tell the job shell to ignore
the ``tasks`` section of the submitted jobspec, and instead launch the
designated number of tasks per ``type`` of allocated resource. The currently
supported types are ``node`` and ``core``. When specifying this option, both
a ``type`` and ``count`` are required. For example, to launch 100 tasks
per node across 2 nodes:

.. code-block:: console

 $ flux mini run -o per-resource.type=node -o per-resource.count=100 -N2 COMMAND

Another method to more generally oversubscribe resources is to launch
multiple Flux brokers per node. This can be done locally for testing, e.g.

.. code-block:: console

 $ flux start -s 4

or can be done by launching a job with multiple ``flux start`` commands
per node, e.g. to run 8 brokers across 2 nodes

.. code-block:: console

 $ flux mini submit -o cpu-affinity=off -N2 -n8 flux start SCRIPT

One final method is to use the ``alloc-bypass``
`jobtap plugin <https://flux-framework.readthedocs.io/projects/flux-core/en/latest/man7/flux-jobtap-plugins.html>`_, which allows a job to bypass the
scheduler entirely by supplying its own resource set. When this plugin
is loaded, an instance owner can submit a job with the
``system.alloc-bypass.R`` attribute set to a valid
`Resource Set Specification <https://flux-framework.readthedocs.io/projects/flux-rfc/en/latest/spec_20.html>`_. The job will then be executed
immediately on the specified resources. This is useful for co-locating
a job with another job, e.g. to run debugger or other services.

.. code-block:: console

 $ flux jobtap load alloc-bypass.so
 $ flux mini submit -N4 sleep 60
 ƒ2WU24J4NT
 $ flux mini run --setattr=system.alloc-bypass.R="$(flux job info ƒ2WU24J4NT R)" -n 4 flux getattr rank
 3
 2
 1
 0


.. _node_memory_exhaustion:

Memory exhaustion on a node when running large ensembles with Flux
==================================================================

Flux's in-memory KVS, or more properly, its content-addressable storage
subsystem, is backed by an `SQLite <https://www.sqlite.org>`_ database file,
located by default in *rundir*, which is usually in ``/tmp``.  On some systems,
``/tmp`` is a RAM-backed file system.  To minimize Flux's memory footprint
on such systems, Flux may be launched with the database file redirected to
a more appropriate location by setting the *statedir* broker attribute.  For
example:

.. code-block:: sh

    flux start -o,-Sstatedir=/scratch/mydir

.. _mimic_slurm_jobstep:

Note the following:

* The database is only accessed by rank 0 so *statedir* need not be shared
  with the other ranks.
* *statedir* must exist before starting Flux.
* If *statedir* contains ``content.sqlite`` it will be reused.  Unless you are
  intentionally restarting on the same nodes, remove it before starting Flux.
* Unlike *rundir*, *statedir* and the ``content.sqlite`` file with in it
  are not cleaned up when Flux exits.

See also: `flux-broker-attributes(7) <https://flux-framework.readthedocs.io/projects/flux-core/en/latest/man7/flux-broker-attributes.html>`_

How do I mimic Slurm's job step semantics ?
===========================================

Using ``flux mini submit`` to submit a script containing multiple
``flux mini run`` invocations will not result in Slurm-style job steps unless
the job script is prefixed with ``flux start`` .

.. _mpi_bootstrap_fails:

Flux is failing to bootstrap a specific MPI implementation (e.g. OpenMPI, MPICH, Spectrum MPI)
==============================================================================================

Flux's shell plugins for Intel MPI, MVAPICH, and OpenMPI run by default with
every job. If you experience any issues bootstrapping these MPIs, use the
``flux mini run/submit -o mpi=`` option when running or submitting, or
please open an issue: :ref:`bug_report_how`


For Spectrum MPI follow the instructions here: :ref:`coral_spectrum_mpi`

.. _message_callback_not_run:

My message callback is not being run. How do I debug?
=====================================================

* Check the error codes from ``flux_msg_handler_addvec``,
  ``flux_register_service``, ``flux_rpc_get``, etc
* Use ``FLUX_O_TRACE`` and ``FLUX_HANDLE_TRACE`` to see messages moving
  through the overlay
* ``FLUX_HANDLE_TRACE`` is set when starting a Flux instance:
  ``FLUX_HANDLE_TRACE=t flux start``
* ``FLUX_O_TRACE`` is passed as a flag to
  `flux_open(3) <https://flux-framework.readthedocs.io/projects/flux-core/en/latest/man3/flux_open.html>`_

.. _parallel_run_hang:

I'm experiencing a hang while running my parallel application. How can I debug?
===============================================================================

* Run ``flux mini run/submit`` with the ``-vvv`` argument
* If it is hanging in startup, try adding the ``PMI_DEBUG`` environment
  variable: ``PMI_DEBUG=t flux mini run my_app.exe``

.. _versioning_multi_repo:

How does the versioning of Flux work with its multi-repo structure?
===================================================================

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

What versions of OpenMPI work with Flux?
========================================

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

Why does the ``flux mini bulksubmit`` command hang?
===================================================

The ``flux mini bulksubmit`` command works similar to GNU parallel or
``xargs`` and is likely blocked waiting for input from ``stdin``.
Typical usage is to send output of some command to ``bulksubmit`` and,
like ``xargs -I``, substitute the input with ``{}``. For example:

.. code-block:: console

 $ seq 1 4 | flux mini bulksubmit --watch echo {}
 ƒ2jBnW4zK
 ƒ2jBoz4Gf
 ƒ2jBoz4Gg
 ƒ2jBoz4Gh
 1
 2
 3
 4

As an alternative to reading from ``stdin``, the ``bulksubmit`` utility can
also take inputs on the command line separated by ``:::``.

The ``--dry-run`` option to ``flux mini bulksubmit`` may be useful to
see what would be submitted to Flux without actually running any jobs

.. code-block:: console

 $ flux mini bulksubmit --dry-run echo {} ::: 1 2 3
 flux-mini: submit echo 1
 flux-mini: submit echo 2
 flux-mini: submit echo 3

For more help and examples, see the `BULKSUBMIT <https://flux-framework.readthedocs.io/projects/flux-core/en/latest/man1/flux-mini.html#bulksubmit>`_
section of the ``flux-mini(1)`` manual page.
