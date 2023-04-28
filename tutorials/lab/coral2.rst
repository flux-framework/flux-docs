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

---------------
Things to Know
---------------

#.  Every multi-node running job on Shasta systems consumes two port numbers
    out of a global pool that Flux reserves. So if Flux has 1,000
    reserved ports, only 500 multi-node jobs may be active at any time.
    Attempting to run further multi-node jobs will cause the excess jobs
    to fail. There is no limit on *submitted* multi-node jobs, and
    single-node jobs do not count towards the limit.
#.  All Flux instances should meet one of the following criteria:

    - Occupy a single node
    - Have exclusive access to the nodes they are running on (e.g. they
      do not share their resources with sibling instances).

    Instances that do not meet one of the above criteria will not work properly.

By default Flux reserves ports 11000-11999 for itself. At any given
level of the Flux hierarchy, this can be changed by configuring Flux
to load the `cray_pals_port_distributor` jobtap plugin with a different
range of ports, like so:

.. code-block:: toml

    [job-manager]
    plugins = [
      { load = "cray_pals_port_distributor.so", conf = { port-min = 11000, port-max = 13000 } }
    ]

------------------
Flux with Cray PMI
------------------

Applications linked to Cray MPICH will work natively with Flux
provided the Cray MPICH library uses the PMI2 protocol instead of
the homespun Cray PMI and libPALS. For Flux to support libPALS,
flux-coral2 must be built (see above) and Flux must be configured
to offer libPALS support. This is done by setting the "pmi" shell
option to include "cray-pals" on a per-job basis like so:

.. code-block:: console

    $ flux submit -n2 -opmi=cray-pals ./mpi_hello

or by configuring Flux to offer such support by default, by adding
the following lines to the shell's ``initrc.lua`` file:

.. code-block:: lua

    if shell.options['pmi'] == nil then
        shell.options['pmi'] = 'cray-pals,simple'
    end


The lines should come before any call to load plugins.

If Flux jobs that use Cray MPICH end up as a collection of singletons,
that is usually a sign that Cray MPICH is trying to use libPALS.

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
and write access.
