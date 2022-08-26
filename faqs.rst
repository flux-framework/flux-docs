.. _faqs:

####
FAQs
####

Some frequently asked questions about flux and their answers.

.. _flux_run_mac:


*****************
General Questions
*****************

What's with the fancy ƒ?
========================

Flux job IDs and their multiple encodings are described in
`RFC 19 <https://flux-framework.readthedocs.io/projects/flux-rfc/en/latest/spec_19.html>`_.  The ``ƒ`` prefix denotes the start of the F58 job ID encoding.
Flux tries to determine if the current locale supports UTF-8 multi-byte
characters before using ``ƒ``, and if it cannot, substitutes the alternate
ASCII ``f`` character.  If necessary, you may coerce the latter by setting
``FLUX_F58_FORCE_ASCII=1`` in your environment.

Most flux tools accept a job ID in any valid encoding.  You can convert from
F58 to another using the :core:man1:`flux-job` ``id`` subcommand, e.g.

.. code-block:: sh

   $ flux mini submit sleep 3600 | flux job id --to=words
   airline-alibi-index--tuna-maximum-adam
   $ flux job cancel airline-alibi-index--tuna-maximum-adam

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

Why is Flux ignoring my Nvidia GPUs?
====================================

When Flux is launched via a foreign resource manager like SLURM or LSF,
it must discover available resources from scratch using
`hwloc <https://www.open-mpi.org/projects/hwloc/>`_.  To print a resource
summary, run:

.. code-block:: sh

  $ flux resource info
  16 Nodes, 96 Cores, 16 GPUs

The version of hwloc that Flux is using at runtime must have been configured
with ``--enable-cuda`` for it to be able to detect Nvidia GPUs.  You can test
to see if hwloc is able to detect installed GPUs with:

.. code-block:: sh

  $ lstopo | grep CoProc

If no output is produced, then hwloc does not see any Nvidia GPUs.

This problem manifests itself differently on a Flux system instance where *R*
(the resource set) is configured, or when Flux receives *R* as an allocation
from the enclosing Flux instance.  In these cases Flux checks *R* against
resources reported by hwloc, and drains any nodes that have missing resources.

Why are resources missing in foreign-launched Flux?
===================================================

When Flux discovers resources via
`hwloc <https://www.open-mpi.org/projects/hwloc/>`_, it honors the current
core and GPU bindings, so if resources are missing, affinity and binding
from the parent resource manager should be checked.  In Slurm, try
``--mpibind=off``, in LSF jsrun, try ``--bind=none``.

.. _launch_large_num_jobs:

How do I efficiently launch a large number of jobs?
===================================================

If you have more than 10K fast-cycling jobs to run, here are some tips that
may help improve efficiency and throughput:

- Create a batch job or allocation to contain the jobs in a Flux sub-instance.
  This improves performance over submitting them directly to the Flux system
  instance and reduces the impact of your jobs on system resources and other
  users.  See also: :ref:`batch`.
- If scripting ``flux mini submit`` commands, avoid the pattern of one command
  per job as each command invocation has a startup cost.  Instead try to
  combine similar job submissions with ``flux mini submit --cc=IDSET``
  or `flux-mini builksubmit <https://flux-framework.readthedocs.io/projects/flux-core/en/latest/man1/flux-mini.html#bulksubmit>`_.
- By default ``flux mini submit --cc=IDSET`` and ``flux mini bulksubmit``
  will exit once all jobs have been submitted.  To wait for all jobs to
  complete before proceeding, use the ``--wait`` or ``--watch`` options to
  these tools.
- If multiple commands must be used to submit jobs before waiting for them,
  consider using ``--flags=waitable`` and ``flux job wait --all`` to wait for
  jobs to complete and capture any errors.
- If the jobs to be submitted cannot be combined with the ``flux mini`` tools,
  develop a workflow management script using the
  `Flux python interface <https://flux-framework.readthedocs.io/projects/flux-core/en/latest/python/index.html>`_.  The
  `flux-mini <https://github.com/flux-framework/flux-core/blob/master/src/cmd/flux-mini.py>`_
  command itself is a python program that can be a useful reference.
- If jobs produce a significant amount of standard I/O, use the
  :core:man1:`flux-mini` ``--output`` option to redirect it to files.  By
  default, standard I/O is captured in the Flux key value store, which holds
  other job metadata and may become a bottleneck if jobs generate a large
  amount of output.
- When handling many fast-cycling jobs, the rank 0 Flux broker may require
  significant memory and cpu.  Consider excluding that node from scheduling
  with ``flux resource drain 0``.

Since Flux can be launched as a parallel job within foreign resource managers
like SLURM and LSF, your efforts to develop an efficient batch or workflow
management script that runs within a Flux instance can be portable to those
systems.

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

How do I prevent Flux from filling up /tmp?
===========================================

Flux's key value store is backed by an `SQLite <https://www.sqlite.org>`_
database file, located by default in *rundir*, typically ``/tmp``.  On some
systems, ``/tmp`` is a RAM-backed file system with limited space, and in
some situations such as long running, high throughput workflows, Flux may
use a lot of it.

Flux may be launched with the database file redirected to another location
by setting the *statedir* broker attribute.  For example:

.. code-block:: sh

    $ mkdir -p /home/myuser/jobstate
    $ rm -f /home/myuser/jobstate/content.sqlite
    $ flux mini batch --broker-opts=-Sstatedir=/home/myuser/jobdir -N16 ...

Or if launching via :core:man1:`flux-start` use:

.. code-block:: sh

    $ flux start -o,-Sstatedir=/home/myuser/jobdir

Note the following:

* The database is only accessed by rank 0 so *statedir* need not be shared
  with the other ranks.
* *statedir* must exist before starting Flux.
* If *statedir* contains ``content.sqlite`` it will be reused.  Unless you are
  intentionally restarting on the same nodes, remove it before starting Flux.
* Unlike *rundir*, *statedir* and the ``content.sqlite`` file within it
  are not cleaned up when Flux exits.

See also: :core:man7:`flux-broker-attributes`.

.. _mimic_slurm_jobstep:

How do I run job steps?
=======================

A Flux batch job or allocation started with ``flux mini batch`` or
``flux mini alloc`` is actually a full featured Flux instance run as a job
within the enclosing Flux instance.  Unlike SLURM, Flux does not have a
separate concept like *steps* for work run in a Flux sub-instance--we just have
*jobs*.  That said, a batch script in Flux may contain multiple
``flux mini run`` commands just as a SLURM batch script may contain multiple
``srun`` commands.

Despite there being only one type of *job* in Flux, running a series of jobs
within a Flux sub-instance confers several advantages over running them
directly in the Flux system instance:

- System prolog and epilog scripts typically run before and after each job
  in the system instance, but are skipped between jobs within a sub-instance.
- The Flux system instance services all users and active jobs running at that
  level, but the sub-instance operates independently and is yours alone.
- Flux accounting may enforce a maximum job count at the system instance level,
  but the sub-instance counts as a single job no matter how many jobs are run
  within it.
- The user has full administrative control over the Flux sub-instance, whereas
  "guests" have limited access to the system instance.

Flux's nesting design makes it possible to be quite sophisticated in how
jobs running in a Flux sub-instance are scheduled and managed, since all
Flux tools and APIs work the same in any Flux instance.

See also: :ref:`batch`.

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

*************
MPI Questions
*************

.. _mpi_bootstrap_fails:

How do I set MPI-specific options?
==================================

The environment that Flux presents to MPI is via the :core:man1:`flux-shell`,
which is the parent process of all MPI processes.  There is typically one
flux shell per node launched for each job.  A Flux shell plugin offers a
`PMI <https://flux-framework.readthedocs.io/projects/flux-rfc/en/latest/spec_13.html>`_
server that MPI uses to bootstrap itself within the application's call to
``MPI_Init()``.  Several shell options affect the shell's PMI server:

verbose=2
   If the shell verbosity level is set to 2 or greater, a trace of the
   PMI server operations is emitted to stderr, which can help debug an
   MPI application that is failing within ``MPI_Init()``.

pmi.kvs=NAME
   Change the implementation of the PMI key-value store.  The default value
   is ``exchange``, which gathers data to the first shell in the job, and
   then broadcasts it to the other shells after a barrier.  The other option
   is ``native`` which uses the Flux KVS.

pmi.exchange.k=N
   Alter the fanout of the virtual tree based overlay network used in the
   ``exchange`` kvs method.  The default fanout is 2.  Other values may
   affect performance for different job sizes.

pmi.clique=TYPE
   Affect how the ``PMI_process_mapping`` key is generated, which tells MPI
   which ranks are expected to be co-located on nodes.  The default value is
   ``pershell`` (one "clique" per shell).  Other possible values are ``single``
   (all ranks on the same node), or ``none`` (skip generating
   ``PMI_process_mapping``).

In addition to the PMI server, the shell implements "MPI personalities" as
lua scripts that are sourced by the shell.  Scripts for generic installs of
openmpi, mvapich, and Intel MPI are loaded by default from
``/etc/flux/shell/lua.d``.  Other personalities are optionally loaded from
``/etc/flux/shell/lua.d/mpi``:

mpi=spectrum
   IBM Spectrum MPI is an OpenMPI derivative.  See also
   :ref:`coral_spectrum_mpi`.

MPI personality options may be added by site administrators, or by other
packages.

Example: launch a Spectrum MPI job with PMI tracing enabled:

.. code-block:: console

 $ flux mini run -ompi=spectrum -overbose=2 -n4 ./hello

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

How should I configure OpenMPI to work with Flux?
=================================================

There are many ways to configure OpenMPI, but a few configure options
deserve special mention if MPI programs are to be run by Flux:

enable-static
   One of the Flux MCA plugins uses ``dlopen()`` internally to access Flux's
   ``libpmi.so`` library, since unlike the MPICH-derivatives, OpenMPI does
   not have a built-in simple PMI client. This option prevents OpenMPI from
   using ``dlopen()`` so that MCA plugin will not be built.  Do not use.

with-flux-pmi
   Although the Flux MCA plugins are built by default, this is required to
   ensure configure fails if they cannot be built for some reason.

How do I make OpenMPI print debugging output?
=============================================

This is not a Flux question but it comes up often enough to mention here.
You may set OpenMPI MCA parameters via the environment by prefixing the
parameter with ``OMPI_MCA_``.  For example, to get verbose output from the
Block Transfer Layer (BTL), set the ``btl_base_verbose`` parameter to an
integer verbosity level, e.g.

.. code-block:: console

 $ flux mini run --env=OMPI_MCA_btl_base_verbose=99 -N2 -n4 ./hello

To list available MCA parameters containing the string ``_verbose`` use:

.. code-block:: console

 $ ompi_info -a | grep _verbose

How should I configure MVAPICH2 to work with Flux?
==================================================

These configuration options are pertinent if MPI programs are to be run
by Flux:

with-pm=hydra
   Select the built-in PMI-1 "simple" wire protocol client which matches
   the default PMI environment provided by Flux.

with-pm=slurm
   This disables the aforementioned PMI-1 client, even if hydra is also
   specified.  Do not use.

.. note::
   It appears that ``--with-pm=slurm`` is not required to run MPI programs
   under SLURM, although it is unclear whether there is a performance impact
   under SLURM when this option is omitted.
