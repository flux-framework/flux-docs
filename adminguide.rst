.. _admin-guide:

==========================
Flux Administrator's Guide
==========================

The *Flux Administrator's Guide* documents relevant information for
installation, configuration, and management of Flux as the native
resource manager on a cluster.

.. note::
    Flux is still beta software and many of the interfaces documented
    in this guide may change with regularity.

    This document is in DRAFT form and currently applies to flux-core
    version 0.21.0.

.. warning::
    0.21.0 limitation: system instance size should not exceed 256 nodes.

    0.21.0 limitation: node failure detection is minimal in this release.
    Avoid powering off nodes that are running Flux without following the
    recommended shutdown procedure below.  Cluster nodes that may require
    service or have connectivity issues should be omitted from the Flux
    configuration for now.

.. _installation:

------------
Installation
------------

^^^^^^^^^^^^^
Prerequisites
^^^^^^^^^^^^^

`MUNGE <https://github.com/dun/munge>`_ is used to sign job requests
submitted to Flux, so the MUNGE daemon should be installed on all
nodes running Flux with the same MUNGE key used across the cluster.

Flux assumes a shared UID namespace across the cluster.

A system user named ``flux`` is required, with the following characteristics:

- same UID across the cluster
- valid home directory (either shared or unique per node are fine)
- logins may be disabled

^^^^^^^^^^^^^^^^^^^^
Package installation
^^^^^^^^^^^^^^^^^^^^

A Flux system install requires ``flux-security`` and ``flux-core``
packages to be installed at a minimum. For real workloads it is highly
recommended that ``flux-sched`` (a.k.a the *Fluxion* graph-based scheduler)
be installed as well.

If installing from your Linux distribution package manager (preferred),
e.g. RPM or dpkg, you may skip this section.

If installing from a git repo, follow the instructions in
:ref:`manual_installation` .

This section assumes you are installing from a source distribution tarball.

In this guide the paths to configuration
files and executables will assume that Flux software was configured the
same as standard system packages, e.g. with the following arguments to
``configure``:

.. code-block:: console

 $ ./configure --prefix=/usr --sysconfdir=/etc --with-systemdsystemunitdir=/etc/systemd/system --localstatedir=/var

When configuring ``flux-core`` be sure to compile against ``flux-security``
by adding ``--with-flux-security`` to the ``configure`` arguments.

After installation of ``flux-security``, ensure the ``flux-imp`` executable
is installed setuid root. This is the one component of Flux that must run
with privilege:

.. code-block:: console

 $ sudo chown root:root /usr/libexec/flux/flux-imp
 $ sudo chmod 4755 /usr/libexec/flux/flux-imp

Ensure this is replicated across all nodes.

 .. _curve-keys:

^^^^^^^^^^^^^^^^^^^^^^^^^^
System instance CURVE Keys
^^^^^^^^^^^^^^^^^^^^^^^^^^

The system instance shares a CURVE public/private keypair that must be
distributed to all nodes. At this time it must be stored in the ``flux``
user's home directory. To create a new keypair run the ``flux keygen``
utility as the ``flux`` user:

.. code-block:: console

 $ sudo -u flux flux keygen
 Saving /home/flux/.flux/curve/client
 Saving /home/flux/.flux/curve/client_private
 Saving /home/flux/.flux/curve/server
 Saving /home/flux/.flux/curve/server_private


.. _configuration:

-----------------------------
System Instance Configuration
-----------------------------

Much of Flux configuration occurs via
`TOML <https://github.com/toml-lang/toml>`_ configuration files found
in a hierarchy under ``/etc/flux``.  For the most part, Flux
components will read all TOML files from a given directory in a glob,
e.g. ``/etc/flux/component/*.toml``, which allows TOML tables to be
combined in a single file or split across multiple files. For example,
a typical Flux system instance will read all configuration from
``/etc/flux/system/conf.d/*.toml``.

In this guide, separate files will typically be used for clarity, instead
of adding all configuration tables to a single TOML file.


.. _configuration-security:

^^^^^^^^^^^^^^^^^^^^
flux-security config
^^^^^^^^^^^^^^^^^^^^

In order to run multi-user workloads ``flux-security`` components such
as the signing library and ``flux-imp`` need proper configuration.

First, a valid signing method should be configured. In
``/etc/flux/security/conf.d/sign.toml``, add the following to configure
job requests be signed using MUNGE:

.. code-block:: toml

 [sign]
 max-ttl = 1209600  # 2 weeks
 default-type = "munge"
 allowed-types = [ "munge" ]


Then configure ``flux-imp`` by creating ``/etc/flux/imp/exec.toml``
with the following contents:

.. code-block:: toml

 [exec]
 allowed-users = [ "flux" ]
 allowed-shells = [ "/usr/libexec/flux/flux-shell" ]


This ensures that only the ``flux`` user may run the ``flux-imp`` executable,
and the only allowed job shell is the system installed ``flux-shell``.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Execution system configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A system Flux instance must be configured to use a ``flux-imp`` process
as a privileged helper for multi-user execution. This configuration should
be made in ``/etc/flux/system/conf.d/exec/toml``. This configuration table
is read by the ``job-exec`` module.

.. code-block:: toml

 [exec]
 imp = "/usr/libexec/flux/flux-imp"


^^^^^^^^^^^^^^^^^^^^
Access configuration
^^^^^^^^^^^^^^^^^^^^

By default, a Flux instance does not allow access to any user other than
the instance *owner*, in this case the ``flux`` user.  This is not
suitable for a system instance, so *guest user* access should be enabled
in ``/etc/flux/system/conf.d/access.toml``.  In addition, it may be convenient
to allow the ``root`` user to act as the instance owner, to give system
administrators privileged Flux access to cancel or list jobs:

.. code-block:: toml

 [access]
 allow-guest-user = true
 allow-root-owner = true

.. _configuration-overlay:

^^^^^^^^^^^^^^^^^^^^^
Network configuration
^^^^^^^^^^^^^^^^^^^^^

Flux brokers on each node communicate over a tree based overlay network.
Each broker is assigned a ranked integer address, starting with zero.
The overlay network may be configured to use any IP network that remains
available the whole time Flux is running.

.. warning::
    0.21.0 limitation: the system instance tree based overlay network
    is forced by the systemd unit file to be *flat* (no interior router
    nodes), trading scalability for reliability.

The Flux system instance overlay is currently configured via a cluster
specific ``bootstrap.toml`` file. The example here is for a 16 node
cluster named ``fluke`` with hostnames ``fluke1`` through ``fluke16``,
and a management network interface of ``enp0s25``:

``/etc/flux/system/conf.d/bootstrap.toml``

.. code-block:: toml

 [bootstrap]
 default_port = 8050
 default_bind = "tcp://eno1:%p"
 default_connect = "tcp://e%h:%p"

 hosts = [
    { host = "fluke[3,108,6-103]" },
 ]

The file format more flexible than this example would indicate. For
more info, refer to the `flux-config-bootstrap(5) <https://flux-framework.readthedocs.io/projects/flux-core/en/latest/man5/flux-config-bootstrap.html>`_
man page.

Hosts will be assigned ranks in the overlay based on their position in the
host array. In the above example ``fluke3`` is rank 0, ``fluke108`` is rank
1, etc.

The Flux rank 0 broker hosts the majority of Flux's services, has a critical
role in overlay network routing, and requires access to persistent storage,
preferably local.  Therefore, rank 0 ideally will be placed on a non-compute
node along with other critical cluster services.

.. warning::
    0.21.0 limitation: Flux should be completely shut down when the
    overlay network configuration is modified.

.. _configuration-resource-exclusion:

^^^^^^^^^^^^^^^^^^
Resource exclusion
^^^^^^^^^^^^^^^^^^

It may be desirable to prevent resources on management and login nodes from
being scheduled to jobs.

Resources may be excluded by broker rank via the ``exclude`` key in the
``resource`` table. It will be common to exclude rank 0 from running jobs,
since it runs critical Flux services. This can be accomplished by creating
the following TOML config:

``/etc/flux/system/conf.d/resource.toml``

.. code-block:: toml

 [resource]
 exclude = "0-1"

The ``exclude`` keyword specifies an idset of ranks to exclude.

.. warning::
    0.21.0 limitation: Flux configuration, tooling, and logs often use broker
    ranks where hostnames would be more convenient.

.. _configuration-storage:

^^^^^^^^^^^^^^^^^^^^^
Storage configuration
^^^^^^^^^^^^^^^^^^^^^

Flux is currently prolific in its use of disk space to back up its key
value store, proportional to the number of jobs run and the quantity
of standard I/O. On your rank 0 node, ensure that the directory for the
content.sqlite file exists with plenty of space:

.. code-block:: console

 $ sudo mkdir -p /var/lib/flux
 $ chown flux /var/lib/flux
 $ chomd 700 /var/lib/flux

This space should be preserved across a reboot as it contains the Flux
job queue and record of past jobs.

.. warning::
    0.21.0 limitation: tools for shrinking the content.sqlite file or
    purging old job data while retaining other content are not yet available.

    0.21.0 limitation: Flux must be completely stopped to relocate or remove
    the content.sqlite file.

    0.21.0 limitation: Running out of space is not handled gracefully.
    If this happens it is best to stop Flux, remove the content.sqlite file,
    and restart.

------------------------------
System Instance Administration
------------------------------

.. _starting-system-instance:

^^^^^^^^^^^^^
Starting Flux
^^^^^^^^^^^^^

Systemd may be configured to start Flux automatically at boot time,
as long as the network that carries its overlay network will be
available at that time.  Alternatively, Flux may be started manually, e.g.

.. code-block:: console

 $ sudo pdsh -w fluke[3,108,6-103] sudo systemctl start flux

Flux brokers may be started in any order, but they won't come online
until their parent in the tree based overlay network is available.


^^^^^^^^^^^^^
Stopping Flux
^^^^^^^^^^^^^

The full Flux system instance may be temporarily stopped by running
the following on the rank 0 node:

.. code-block:: console

 $ sudo systemctl stop flux

This kills any running jobs, but preserves job history and the queue of
jobs that have been submitted but have not yet allocated resources.
This state is held in the `content.sqlite` that was configured above.

The brokers on other nodes will automatically shut down in response,
then respawn, awaiting the return of the rank 0 broker.

To shut down a single node running Flux, simply run the above command
on that node.

.. warning::
    0.21.0 limitation: jobs using a node are not automatically canceled
    when the individual node is shut down.  On an active system, first drain
    the node as described below, then ensure no jobs are using it before
    shutting it down.

.. _configuration-change:

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Changing the Flux configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After changing flux broker or module specific configuration in the TOML
files under ``/etc/flux``, the configuration may be reloaded with

.. code-block:: console

 $ sudo systemctl reload flux

on each rank where the configuration needs to be updated. The broker will
reread all configuration files and notify modules that configuration has
been updated.

Configuration which applies to the ``flux-imp`` or job shell will be reread
at the time of the next job execution, since these components are executed
at job launch.

.. warning::
    0.21.0 limitation: all configuration changes except resource exclusion
    and instance access have no effect until the Flux broker restarts.

.. _draining-resources:

^^^^^^^^^^^^^^^^^^
Draining Resources
^^^^^^^^^^^^^^^^^^

Resources may be temporarily removed from scheduling via the
``flux resource drain`` command. Currently, resources may only be drained
at the granularity of a node, represented by its broker rank, for example:

.. code-block:: console

 $ sudo flux resource drain 4
 $ sudo flux resource list
      STATE NNODES   NCORES    NGPUS
       free     15       30        0
  allocated      0        0        0
       down      1        2        0


Any work running on the drained node is allowed to complete normally.

To return drained resources use ``flux resource undrain``:

.. code-block:: console

 $ sudo flux resource undrain 4
 $ sudo flux resource list
      STATE NNODES   NCORES    NGPUS
       free     16       32        0
  allocated      0        0        0
       down      0        0        0


.. _queue-admin:

^^^^^^^^^^^^^^^^^^^^^^^
Managing the Flux Queue
^^^^^^^^^^^^^^^^^^^^^^^

The queue of jobs is managed by the flux job-manager, which in turn
makes allocation requests for jobs in priority order to the scheduler.
This queue can be managed using the ``flux-queue`` command.

.. code-block:: console

 Usage: flux-queue [OPTIONS] COMMAND ARGS
   -h, --help             Display this message.

 Common commands from flux-queue:
    enable          Enable job submission
    disable         Disable job submission
    start           Start scheduling
    stop            Stop scheduling
    status          Get queue status
    drain           Wait for queue to become empty.
    idle            Wait for queue to become idle.


The queue may be listed with the `flux jobs` command.  Refer to `flux-jobs(1) <https://flux-framework.readthedocs.io/projects/flux-core/en/latest/man1/flux-jobs.html>`_

~~~~~~~~~~~~~~~~~~~~~~~~
Disabling job submission
~~~~~~~~~~~~~~~~~~~~~~~~

By default, the queue is *enabled*, meaning that jobs can be submitted
into the system. To disable job submission, e..g to prepare the system
for a shutdown, use ``flux queue disable``. To restore queue access
use ``flux queue enable``.

~~~~~~~~~~~~~~~~~~~~~~~
Stopping job allocation
~~~~~~~~~~~~~~~~~~~~~~~

The queue may also be stopped with ``flux queue stop``, which disables
further allocation requests from the job-manager to the scheduler. This
allows jobs to be submitted, but stops new jobs from being scheduled.
To restore scheduling use ``flux queue start``.

~~~~~~~~~~~~~~~~~~~~~~~~~
Flux queue idle and drain
~~~~~~~~~~~~~~~~~~~~~~~~~

The ``flux queue drain`` and ``flux queue idle`` commands can be used
to wait for the queue to enter a given state. This may be useful when
preparing the system for a downtime.

The queue is considered *drained* when there are no more active jobs.
That is, all jobs have completed and there are no pending jobs.
``flux queue drain`` is most useful when the queue is *disabled* .

The queue is "idle" when there are no jobs in the RUN or CLEANUP state.
In the *idle* state, jobs may still be pending. ``flux queue idle``
is most useful when the queue is *stopped*.

To query the current status of the queue use the ``flux queue status``
command:

.. code-block:: console

 $ flux queue status -v
 flux-queue: Job submission is enabled
 flux-queue: Scheduling is enabled
 flux-queue: 2 alloc requests queued
 flux-queue: 1 alloc requests pending to scheduler
 flux-queue: 0 free requests pending to scheduler
 flux-queue: 4 running jobs


.. _managing-jobs:

^^^^^^^^^^^^^^^^^^
Managing Flux Jobs
^^^^^^^^^^^^^^^^^^

.. _expedite-jobs:

~~~~~~~~~~~~~~~
Expediting Jobs
~~~~~~~~~~~~~~~
Expediting and holding jobs is planned, but not currently supported.

.. _canceling-jobs:

~~~~~~~~~~~~~~
Canceling Jobs
~~~~~~~~~~~~~~

An active job may be canceled via the ``flux job cancel`` command. An
instance owner may cancel any job, while a guest may only cancel their
own jobs.

All active jobs may be canceled with ``flux job cancelall``. By default
this command will only print the number of jobs that would be canceled.
To force cancellation of all matched jobs, the ``-f, --force`` option must
be used:

.. code-block:: console

 $ flux job cancelall
 flux-job: Command matched 5 jobs (-f to confirm)
 $ flux job cancelall -f
 flux-job: Canceled 5 jobs (0 errors)

The set of jobs matched by the ``cancelall`` command may also be restricted
via the ``-s, --states=STATES`` and ``-u, --user=USER`` options.


.. _dedicated-application-time:

^^^^^^^^^^^^^^^^^^^^^^^^^^
Dedicated Application Time
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _updating-flux:

^^^^^^^^^^^^^^^^^^^^^^
Updating Flux Software
^^^^^^^^^^^^^^^^^^^^^^

Flux will eventually support rolling software upgrades, but prior to
major release 1, Flux software release versions should not be assumed
to inter-operate.  Furthermore, at this early stage, Flux software
components (e.g. ``flux-core``, ``flux-sched``, ``flux-security``,
and ``flux-accounting``)  should only only be installed in recommended
combinations.

.. warning::
    0.21.0 limitation: mismatched versions are not detected, thus
    the effect of accidentally mixing versions of flux-core within
    a Flux instance is unpredictable.

.. warning::
    0.21.0 limitation: job data should be purged when updating to the
    next release of flux-core, as internal representations of data written
    out to the Flux KVS and stored in the content.sqlite file are not yet
    stable.

.. _troubleshooting:

---------------
Troubleshooting
---------------


.. _flux-logs:

^^^^
Logs
^^^^

.. _systemd-journal:

~~~~~~~~~~~~~~~
Systemd journal
~~~~~~~~~~~~~~~

Flux brokers log information to standard error, which is normally captured
by the systemd journal.  It may be useful to look at this log when diagnosing
a problem on a particular node:

.. code-block:: console

 $ journalctl -u flux
 Sep 14 09:53:12 sun1 systemd[1]: Starting Flux message broker...
 Sep 14 09:53:12 sun1 systemd[1]: Started Flux message broker.
 Sep 14 09:53:12 sun1 flux[23182]: broker.info[2]: start: none->join 0.0162958s
 Sep 14 09:53:54 sun1 flux[23182]: broker.info[2]: parent-ready: join->init 41.8603s
 Sep 14 09:53:54 sun1 flux[23182]: broker.info[2]: rc1.0: running /etc/flux/rc1.d/01-enclosing-instance
 Sep 14 09:53:54 sun1 flux[23182]: broker.info[2]: rc1.0: /bin/sh -c /etc/flux/rc1 Exited (rc=0) 0.4s
 Sep 14 09:53:54 sun1 flux[23182]: broker.info[2]: rc1-success: init->quorum 0.414207s
 Sep 14 09:53:54 sun1 flux[23182]: broker.info[2]: quorum-full: quorum->run 9.3847e-05s

.. _flux-dmesg:

~~~~~~~~~~~~~~~~~~~~~
Flux logs: flux-dmesg
~~~~~~~~~~~~~~~~~~~~~

The rank 0 broker accumulates log information for the full instance in a
circular buffer.  For some problems, it may be useful to view this log:

.. code-block:: console

 $ sudo flux dmesg |tail
 2020-09-14T19:38:38.047025Z sched-simple.debug[0]: free: rank1/core0
 2020-09-14T19:38:41.600670Z sched-simple.debug[0]: req: 6115337007267840: spec={0,1,1} duration=0.0
 2020-09-14T19:38:41.600791Z sched-simple.debug[0]: alloc: 6115337007267840: rank1/core0
 2020-09-14T19:38:41.703252Z sched-simple.debug[0]: free: rank1/core0
 2020-09-14T19:38:46.588157Z job-ingest.debug[0]: validate-jobspec.py: inactivity timeout

.. _kvs-eventlogs:

~~~~~~~~~~~~~
KVS Eventlogs
~~~~~~~~~~~~~

