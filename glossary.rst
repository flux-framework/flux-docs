.. _glossary:

========
Glossary
========

This page contains definitions for Flux-specific terms and concepts mentioned
throughout the various guides and docs on our sites.

------------------------------------------------------------------------------

.. _flux-broker:

**Flux Broker**
  A distributed message broker that provides communications services
  within a Flux instance. It is the main controller of the Flux instance and
  loads all the important job, scheduling, and resource related services for
  Flux.

.. _flux-instance:

**Flux Instance**
  A group of flux-broker processes which are launched via any parallel launch
  utility that supports PMI (Process Manager Interface).

.. _eventlog:

**Eventlog**
  An ordered log of timestamped events, stored in the Flux KVS and defined by
  `RFC 18 <https://flux-framework.readthedocs.io/projects/flux-rfc/en/latest/spec_18.html>`_.
  Eventlogs are used to record job events, capture standard I/O streams,
  and record resource status changes.

.. _fluid:

**FLUID (Flux Locally Unique ID)**
  IDs used to represent Flux jobs, defined by
  `RFC 19 <https://flux-framework.readthedocs.io/projects/flux-rfc/en/latest/spec_19.html>`_.

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
