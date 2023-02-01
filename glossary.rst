.. _glossary:

========
Glossary
========

This page contains definitions for Flux-specific terms and concepts mentioned
throughout the various guides and docs on our sites.

------------------------------------------------------------------------------

.. _eventlog:

**Eventlog**
  An ordered log of timestamped events, stored in the Flux KVS and defined by
  `RFC 18 <https://flux-framework.readthedocs.io/projects/flux-rfc/en/latest/spec_18.html>`_.
  Eventlogs are used to record job events, capture standard I/O streams,
  and record resource status changes.

.. _flux-broker:

**Flux Broker**
  A distributed message broker that provides communications services
  within a Flux instance. It is the main controller of the Flux instance and
  loads all the important job, scheduling, and resource related services for
  Flux.

.. _flux-imp:

**Flux IMP (Independent Minister of Privilege)**
  A system service that allows instance owners to run work on behalf of a guest.
  In other words, it allows multiple users to use / run jobs on a :ref:`Flux
  instance<flux-instance>` instead of just the owner.  More of the nitty gritty
  details can be found in
  `RFC 15 <https://flux-framework.readthedocs.io/projects/flux-rfc/en/latest/spec_15.html>`_.

.. _flux-instance:

**Flux Instance**
  A group of flux-broker processes which are launched via any parallel launch
  utility that supports PMI (Process Manager Interface).

.. _flux-shell:

**Flux Shell**
  A component of Flux that manages the startup and execution of user jobs.  You
  can read more in the :core:man1:`flux-shell` manpage.

.. _fluid:

**FLUID (Flux Locally Unique ID)**
  IDs used to represent Flux jobs, defined by
  `RFC 19 <https://flux-framework.readthedocs.io/projects/flux-rfc/en/latest/spec_19.html>`_.

.. _fractal-scheduling:

**Fractal Scheduling**
  A term that is sometimes used to describe a tree of
  :ref:`Flux instances<flux-instance>` that are greater than 2 in depth.  In
  other words, a Flux :ref:`subinstance<subinstance>` that has launched
  additional Flux subinstances.

.. _fsd:
.. _flux_standard_duration:

**FSD (Flux Standard Duration)**
  A Flux standard for human readable time durations.  Generally speaking, the
  suffixes of 'ms', 's', 'm', 'h', 'd' are used to indicate time in
  milliseconds, seconds, minutes, hours, or days respectively.  The specifics
  can be found in
  `RFC 23 <https://flux-framework.readthedocs.io/projects/flux-rfc/en/latest/spec_23.html>`_.

.. _hostlist:

**Hostlist**
  A format supported by many HPC tools to create a compact list of hosts by
  name, consisting of a common prefix, a number, and an optional suffix. For
  example, the hosts ``cow1``, ``cow2``, and ``cow3`` could be represented by
  the hostlist ``cow[1-3]``. 🐮

.. _idset:

**IDSet**
  A compact way of representing an unordered set of integers, defined by
  `RFC 22 <https://flux-framework.readthedocs.io/projects/flux-rfc/en/latest/spec_22.html>`_.

.. _jobspec:

**Jobspec**
  A file which defines the resources, tasks, and other attributes of a single
  program, defined by `RFC 25 <https://flux-framework.readthedocs.io/projects/flux-rfc/en/latest/spec_25.html>`_
  and `RFC 14 <https://flux-framework.readthedocs.io/projects/flux-rfc/en/latest/spec_14.html>`_.
  An example can be found in the `Example Jobspec
  <https://flux-framework.readthedocs.io/projects/flux-rfc/en/latest/spec_25.html#example-jobspec>`_
  section of RFC 25.

.. _jobtap-plugin:

**Jobtap Plugin**
  A built-in or external plugin that can be loaded into the job manager broker
  module. They are an extension of the job manager, arranging for callbacks at
  different points in a job's life cycle. Additional information on jobtap plugins
  can be found in :core:man7:`flux-jobtap-plugins`.

.. _kvs:

**KVS (Key-Value Store)**
  A component of a Flux instance where information pertaining to the instance
  is stored in a key-value format. It is used by Flux internally to store data
  such as resource information, jobspec, logs, and checkpoints. Each job is
  assigned a KVS namespace, which may also be used by users to store small
  amounts of data.

.. _limits:

**Limits**
  Maximum values that are enforced across jobs, queues, and users, such as time
  and/or resource limits.

.. _queue:
.. _job_queue:

**Queue**
  A job management data structure that contains sets of jobs in priority order.
  Multiple queues may be configured for a :ref:`Flux instance<flux-instance>`.
  Queues may differ in what resources are assigned to them, which users are
  allowed to submit to them, and what defaults/limits may exist for them.  Often
  may be called a "job queue."

.. _queue_enable:
.. _queue_disable:
.. _queue_start:
.. _queue_stop:

**Queue Enable/Disable/Start/Stop**
  In Flux, the terms "enable"/"disable" are used to describe if jobs can be
  submitted to a queue.  The terms "start"/"stop" are used to describe if jobs
  can be executed.  Under normal operations, a queue is "enabled"/"started,"
  which allows users to submit jobs and jobs can run.  If a queue is
  "enabled"/"stopped," it means jobs can be submitted but not allowed to run.
  This situation is common if resources are temporarily down for maintenance.
  If a queue is "disabled"/"started," previously submitted jobs can run, but no
  more jobs can be submitted going forward.  This situation is common if
  administrators want to take down resources in the future and want currently
  running jobs to finish.

.. _queue_drain:
.. _queue_idle:

**Queue Drain/Idle**
  In Flux, the term "drain" is used for waiting for a queue to be empty.  It is
  common to wait for a queue to drain after a queue is
  :ref:`disabled<queue_disable>`.  The term "idle" Is used for waiting for all
  running jobs to finish.  It is common to wait for a queue to idle after a
  queue is :ref:`stopped<queue_stop>`.

.. _pmi:

**PMI (Process Manager Interface)**
  A standard API and wire protocol for communication between MPI runtimes and
  resource managers.

  PMI traditionally provides a key-value store with all-to-all style synchronization
  to support the bootstrap of parallel programs such as MPI. During wire up, each
  parallel task can bind to a network endpoint, put its network address into the PMI
  KVS, synchronize, and then get the addresses of its network peers. All without
  requiring the process manager (e.g. Flux) to know anything about the network
  interconnect hardware. Brilliant!

  Although there are several variations of PMI, Flux implements the original one
  from Argonne National Lab which is documented in
  `RFC 13 <https://flux-framework.readthedocs.io/projects/flux-rfc/en/latest/spec_13.html>`_.
  In addition to providing PMI service to the programs it launches, Flux also uses
  PMI for its own wire-up when it is launched by Flux or a foreign launcher.

  PMI was an unfortunate three letter acronym choice, given that MPI was already a
  thing. This is known - no whining.

.. _policy:

**Policy**
  Attributes of a Flux queue that define behavior of the queue, such as time or
  resource limits.

.. _r:

**R**
  A resource set defined in JSON (`Javascript Object Notation <https://json-spec.readthedocs.io/reference.html>`_)
  format, defined by `RFC 20 <https://flux-framework.readthedocs.io/projects/flux-rfc/en/latest/spec_20.html>`_.

.. _shell-plugin:

**Shell Plugins**
  Extensions of a job's environment that can be configured on a per-job basis
  using the ``--setopt`` option of the :core:man1:`flux-mini` commands.

.. _single-user-mode:

**Single User Mode**
  A :ref:`Flux instance<flux-instance>` that is used by only one user.  This is
  a common use case when a user runs a :ref:`subinstance<subinstance>` only
  for themselves.

.. _subinstance:

**Subinstance**
  A :ref:`Flux instance<flux-instance>` that is run as a job within another Flux
  instance.  This is commonly done if a user wants to schedule / control a set
  of resources themselves outside of the parent instance.  It is commonly done
  in :ref:`single user mode<single-user-mode>`.

.. _system-instance:

**System Instance**
  A :ref:`Flux instance<flux-instance>` that is available to all users on a set
  of resources.  Most users will think of this as the "installed" or "default"
  resource manager/scheduler on a system.

.. _TBON:

**TBON (Tree Based Overlay Network)**
  The overlay network that :ref:`Flux brokers<flux-broker>` wire up amongst
  themselves in a :ref:`Flux instance<flux-instance>`.

.. _URI:

**URI (Universal Resource Identifier)**
  Common resource identifier used by many technologies.  Used in Flux for
  identification of :ref:`Flux brokers<flux-broker>`.  See
  `Wikipedia page <https://en.wikipedia.org/wiki/Uniform_Resource_Identifier>`_
  for general overview.

.. _workflow:

**workflow**
  The
  `Webster's dictionary <https://www.merriam-webster.com/dictionary/workflow>`_
  definition is "the sequence of steps involved in moving from the beginning to
  the end of a working process."  In the context of Flux, this is usually a
  series or collection of jobs that users execute to accomplish some task.
  Although not required, typically jobs will be run in a certain order.  A
  number of jobs in the workflow have dependencies and cannot run until prior
  jobs in the workflow complete.
