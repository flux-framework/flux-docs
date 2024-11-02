.. _rabbitconfig:

=============================
Configuring Flux with Rabbits
=============================

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
dataworkflowservices). There are instructions for how to grant Flux
the minimum permissions necessary by setting up role-based access control
`here <https://nearnodeflash.github.io/latest/guides/rbac-for-users/readme/#rbac-for-workload-manager-wlm>`__.

Lastly, the Fluxion scheduler must be configured to recognize rabbit
resources. This can be done by generating a file describing the rabbit layout
for the cluster and then running ``flux dws2jgf`` like so:

.. code-block:: bash

    flux rabbitmapping > /tmp/rabbitmapping.json
    flux dws2jgf [--no-validate] --from-config /etc/flux/system/conf.d/resource.toml --only-sched /tmp/rabbitmapping.json

The output (which may be large) must be saved to a file and pointed to with the
``resource.scheduling`` config key (see
`here <https://flux-framework.readthedocs.io/projects/flux-core/en/latest/man5/flux-config-resource.html#keys>`__).

In order to facilitate Fluxion restart when using this new JGF
(as it is called), Fluxion must be configured to use a ``match-format``
of ``rv1`` instead of the otherwise recommended default of ``rv1_nosched``.

For example, in a config file:

.. code-block:: toml

    [sched-fluxion-resource]
    match-format = "rv1"
