.. _coral2:

===========================
CORAL2: Flux on Cray Shasta
===========================

The LLNL, LBNL, and ORNL systems like Tioga, Perlmutter,
El Capitan, and Frontier are similar in that they all use the
HPE Cray Shasta platform, which requires
an additional component to integrate completely with Flux.

.. note::
  Flux on CORAL2 is under active development.  This document assumes
  flux-core >= 0.49.0, flux-sched >= 0.27.0, and flux-coral2 >= 0.4.1.

------------
Getting Flux
------------

At LLNL, Flux is part of the operating system and runs as the native resource
manager on Cray Shasta systems.  At other sites, Flux can be launched as
a parallel job by the native resource manager, if desired.

If the minimum versions of the flux components are not already available at
your site, you may consider
:ref:`building flux-core and flux-sched manually <manual_installation>`
then building `flux-coral2 <https://github.com/flux-framework/flux-coral2>`_
with the same prefix.

----------
Cray MPICH
----------

Cray ships a variant of MPICH as the supported MPI library for the slingshot
interconnect.  There are two options for running parallel programs compiled
with Cray MPICH under Flux.

One is to set LD_LIBRARY_PATH so that the MPI executable finds Flux's
``libpmi2.so`` before any other, e.g.

.. code-block:: console

  $ flux run --env=LD_LIBRARY_PATH=/usr/lib64/flux:$LD_LIBRARY_PATH -n2 -opmi=simple ./hello
  foWQCPHAu6f: completed MPI_Init in 1.050s.  There are 2 tasks
  foWQCPHAu6f: completed first barrier in 0.005s
  foWQCPHAu6f: completed MPI_Finalize in 0.001s

The other is to use Cray PMI, which requires a the ``cray-pals`` plugin from
the flux-coral2 package, e.g.

.. code-block:: console

  $ flux run -n2 -opmi=cray-pals ./hello
  foP9Jyw5kjq: completed MPI_Init in 0.051s.  There are 2 tasks
  foP9Jyw5kjq: completed first barrier in 0.006s
  foP9Jyw5kjq: completed MPI_Finalize in 0.002s

Cray PMI comes with additional complications - see below.

Sites that want to make ``cray-pals`` available by default, so users don't
have to specify ``-opmi=cray-pals`` may add the following lines near the top
of the flux-shell's ``initrc.lua``, before any call to load plugins:

.. code-block:: lua

  if shell.options['pmi'] == nil then
      shell.options['pmi'] = 'cray-pals,simple'
  end

This alters the system default of ``pmi=simple``, applies to all Flux
instances, and has no effect if the user specifies ``-opmi=`` on the command
line.  Note that ``simple`` is still the preferred way to bootstrap Flux
itself, so it is advised for it to be retained in the default.

--------------------------------
Cray PMI Complications with Flux
--------------------------------

Cray PMI requires Flux to allocate two unique network port numbers to each
multi-node job and communicate them via ``PMI_CONTROL_PORT`` in the job
environment.  The Cray PMI library uses these ports to establish temporary
network connections to exchange interconnect endpoints.  Two jobs sharing
a node must not be allocated overlapping port numbers, or the jobs may fail.

flux-coral2 supplies the ``cray_pals_port_distributor`` plugin to allocate
a unique pair of ports per job.  However, each Flux instance has an
independent allocator for the same port range, so a complication arises
when multiple Flux instances are sharing a node's port space.  Therefore,
when Cray PMI is in use, Flux instances *must not share nodes*.

To minimize the possibility of batch jobs, which are fully independent Flux
instances, handing out duplicate ports, it is recommended to configure
node-exclusive scheduling for the top level resource manager on these
systems.  This leaves no opportunity for conflicting port numbers to be
assigned among the top-level batch jobs.  It doesn't protect against batch
jobs scheduling Flux sub-instances that conflict, however.

The port allocator defaults to using a pool of 1000 ports.  This places an
upper limit of 500 on the number of concurrently executing multi-node jobs
per Flux instance.  The system limit is much higher since each batch job
is an independent Flux instance that can run many jobs.  Also, single node
jobs do not consume a port pair and are not subject to this limit.

--------------------------
Troubleshooting Cray MPICH
--------------------------

If Flux jobs that use Cray MPICH end up as a collection of singletons,
or fail in ``MPI_Init()``, that is usually a sign that something is wrong
in the PMI bootstrapping environment.  When this happens it may be useful to:

- Add ``-o pmi=NAME[,NAME,...]`` to control which PMI implementations
  are offered by the flux shell to jobs, e.g. ``simple``, ``cray-pals``,
  ``pmix``).

- Add ``-o verbose=2`` to request the shell to print tracing info
  from the PMI implementations.

- Launch ``flux-pmi`` as a parallel program to test PMI in isolation.

.. code-block:: console

  $ flux run -n2 --label-io flux pmi -v --method=libpmi2 barrier
  1: libpmi2: using /opt/cray/pe/lib64/libpmi2.so (cray quirks enabled)
  0: libpmi2: using /opt/cray/pe/lib64/libpmi2.so (cray quirks enabled)
  1: libpmi2: initialize: rank=1 size=2 name=kvs_348520130306638848: success
  0: libpmi2: initialize: rank=0 size=2 name=kvs_348520130306638848: success
  0: fovUPqZ5dwM: completed pmi barrier on 2 tasks in 0.000s.
  1: libpmi2: barrier: success
  0: libpmi2: barrier: success
  1: libpmi2: barrier: success
  0: libpmi2: barrier: success
  1: libpmi2: finalize: success
  0: libpmi2: finalize: success

-----------------------------
Configuring Flux with Rabbits
-----------------------------

In order for a Flux system instance to be able to allocate
rabbit storage, the ``dws_jobtap.so`` plugin must be loaded.
The plugin can be loaded in a  config file like so:

.. code-block::

    [job-manager]
    plugins = [
      { load = "dws-jobtap.so" }
    ]

Also, the ``flux-coral2-dws`` systemd service must be started
on the same node as the rank 0 broker of the system instance
(i.e. the management node). The ``flux`` user must have
a kubeconfig file in its home directory granting it read
and write access to, at a minimum, ``Storages``, ``Workflows``,
``Servers``, and ``Computes`` resources (all of which are defined by
dataworkflowservices).

Lastly, the Fluxion scheduler must be configured to recognize rabbit
resources. This can be done by taking ``R`` for the cluster (see the
"Configuring Resources" section of the Flux Administrator's guide)
and piping it to ``flux dws2jgf`` like so:

.. code-block:: bash

    cat /etc/flux/system/R | flux dws2jgf [--no-validate] [--cluster-name=CLUSTER_NAME] > new_R

The output (which may be large) must replace the old ``R`` for the cluster.

In order to facilitate Fluxion restart when using this new JGF
(as it is called), Fluxion must be configured to use a ``match-format``
of ``rv1`` instead of the otherwise recommended default of ``rv1_nosched``.

For example, in a config file:

.. code-block:: toml

    [sched-fluxion-resource]
    match-format = "rv1"
