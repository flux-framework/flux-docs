.. _admin-guide:

##########################
Flux Administrator's Guide
##########################

The *Flux Administrator's Guide* documents relevant information for
installation, configuration, and management of Flux as the native
resource manager on a cluster.

.. note::
    Flux is still beta software and many of the interfaces documented
    in this guide may change with regularity.

    This document is in DRAFT form and currently applies to flux-core
    version 0.30.0.

.. warning::
    0.30.0 limitation: the flux system instance is primarily tested on
    a 128 node cluster.

    0.30.0 limitation: Avoid powering off nodes that are running Flux
    without following the recommended shutdown procedure below.  Cluster
    nodes that may require service or have connectivity issues should be
    omitted from the Flux configuration for now.

************
Installation
************

Prerequisites
=============

`MUNGE <https://github.com/dun/munge>`_ is used to sign job requests
submitted to Flux, so the MUNGE daemon should be installed on all
nodes running Flux with the same MUNGE key used across the cluster.

Flux assumes a shared UID namespace across the cluster.

A system user named ``flux`` is required, with the following characteristics:

- same UID across the cluster
- valid home directory (either shared or unique per node are fine)
- logins may be disabled

Package installation
====================

A Flux system install requires ``flux-security`` and ``flux-core``
packages to be installed at a minimum. For real workloads it is highly
recommended that ``flux-sched`` (a.k.a the *Fluxion* graph-based scheduler)
be installed as well. For managing user accounts, banks, and utilizing job
priority calculation and fairshare, the ``flux-accounting`` package should also
be installed.

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

System instance CURVE Keys
==========================

The system instance shares a CURVE certificate that must be distributed to
all nodes.  It should be readable only by the ``flux`` user.  To create a
new keypair run the ``flux keygen`` utility as the ``flux`` user:

.. code-block:: console

 $ sudo -u flux flux keygen /etc/flux/system/curve.cert

Do this once and then copy the certificate to the same location on
the other nodes, preserving owner and mode.

*****************************
System Instance Configuration
*****************************

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


flux-security config
====================

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


Then configure ``flux-imp`` by creating ``/etc/flux/imp/conf.d/imp.toml``
with the following contents:

.. code-block:: toml

 [exec]
 allowed-users = [ "flux" ]
 allowed-shells = [ "/usr/libexec/flux/flux-shell" ]


This ensures that only the ``flux`` user may run the ``flux-imp`` executable,
and the only allowed job shell is the system installed ``flux-shell``.

Execution system configuration
==============================

A system Flux instance must be configured to use a ``flux-imp`` process
as a privileged helper for multi-user execution. This configuration should
be made in ``/etc/flux/system/conf.d/exec.toml``. This configuration table
is read by the ``job-exec`` module.

.. code-block:: toml

 [exec]
 imp = "/usr/libexec/flux/flux-imp"


Access configuration
====================

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

Network configuration
=====================

Flux brokers on each node communicate over a tree based overlay network.
Each broker is assigned a ranked integer address, starting with zero.
The overlay network may be configured to use any IP network that remains
available the whole time Flux is running.

.. warning::
    0.30.0 limitation: the system instance tree based overlay network
    is forced by the systemd unit file to be *flat* (no interior router
    nodes), trading scalability for reliability.

The Flux system instance overlay is currently configured via a cluster
specific ``bootstrap.toml`` file. The example here is for a 16 node
cluster named ``fluke`` with hostnames ``fluke1`` through ``fluke16``,
and a management network interface of ``enp0s25``:

``/etc/flux/system/conf.d/bootstrap.toml``

.. code-block:: toml

 [bootstrap]
 curve_cert = "/etc/flux/system/curve.cert"
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
    0.30.0 limitation: Flux should be completely shut down when the
    overlay network configuration is modified.

Resource configuration
======================

The system resource configuration may be generated in RFC 20 (R version 1)
form using ``flux R encode``.  At minimum, a hostlist and core idset must
be specified on the command line, e.g.

.. code-block:: console

 $ flux R encode --hosts=fluke[3,108,6-103] --cores=0-3 >/etc/flux/system/R

To use the Fluxion scheduler, ``flux ion-R encode`` may additionally be used, e.g.,

.. code-block:: console

 $ flux R encode --hosts=fluke[3,108,6-103] --cores=0-3 | flux ion-R encode >/etc/flux/system/R

``flux ion-R encode`` simply adds the optional ``scheduling`` key of RFC 20
to the resource configuration generated by ``flux R encode``.
Our Fluxion scheduler relies on the existence of this key containing
resource graph data in the JSON Graph Format (JGF) for
system instance scheduling.

The resource configuration is then referenced from the ``resource`` table,
``path`` key.

.. note::
    The rank to hostname mapping represented in R is ignored, and is
    replaced at runtime by the rank to hostname mapping from the bootstrap
    hosts array (see above).

Some sites may choose to exclude login and service nodes from scheduling.
This is accomplished using the optional ``exclude`` key, whose value is
a hostlist, or alternatively, idset of broker ranks to exclude.

An example resource configuration:

``/etc/flux/system/conf.d/resource.toml``

.. code-block:: toml

 [resource]
 path = "/etc/flux/system/R"
 exclude = "fluke[3,108]"

Storage configuration
=====================

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
    0.30.0 limitation: tools for shrinking the content.sqlite file or
    purging old job data while retaining other content are not yet available.

    0.30.0 limitation: Flux must be completely stopped to relocate or remove
    the content.sqlite file.

    0.30.0 limitation: Running out of space is not handled gracefully.
    If this happens it is best to stop Flux, remove the content.sqlite file,
    and restart.

flux-accounting configuration
=============================

If ``flux-accounting`` was installed on the management node, its database should
be initialized (its default location is ``/var/lib/flux/FluxAccounting.db``),
and the job manager configured to automatically load the multi-factor priority
plugin provided by flux-accounting. All commands presented in the following
subsections should be run as the flux user.

Database Creation and Initialization
------------------------------------

The first thing to configure when first setting up the flux-accounting database
is to set the **PriorityUsageResetPeriod** and **PriorityDecayHalfLife**
parameters. Both of these parameters represent a number of weeks by which to
hold usage factors up to the time period where jobs no longer play a factor in
calculating a usage factor. If these parameters are not passed when creating the
DB, **PriorityDecayHalfLife** is set to 1 week and **PriorityUsageResetPeriod**
is set to 4 weeks, i.e the flux-accounting database will store up to a month's
worth of jobs broken up into one week chunks:

.. code-block:: console

 $ flux account create-db --priority-decay-half-life=2 --priority-usage-reset-period=8

Now that the database is created, as the admin who has permission to write to
the database, we can initialize it with some banks by specifying a name and the
number of shares:

.. code-block:: console

 $ flux account add-bank root 1
 $ flux account add-bank --parent-bank=root sub_bank_A 1

We can then add some users to those banks so those users can run jobs on the
system:

.. code-block:: console

 $ flux account add-user --username=user1234 --bank=sub_bank_A

Loading the multi-factor priority plugin
----------------------------------------

The other component to load is the multi-factor priority plugin, which can be
loaded by specifying it in the ``job-manager.plugins`` section of the Flux TOML
configuration file. Below is an example configuration file:

``/etc/flux/system/conf.d/plugins.toml``

.. code-block:: toml

 [job-manager]
 plugins = [
   { load = "/usr/lib64/flux/job-manager/plugins/mf_priority.so" },
 ]

Setting up the automatic update scripts
---------------------------------------

There are three update commands and scripts that require setup in order for the
database to be periodically updated with new job usage and fairshare
information. These commands and scripts should be run as the flux user and they
should be run in order and with the same frequency to ensure accurate updates.
A suggested frequency for running these automatic updates would be to run these
once every 30 minutes, but can be tuned to run more or less frequently.

The first automatic cron job that should run is the ``update-usage`` subcommand.
This subcommand fetches the most recent job records from the job-archive
database for every user in the flux-accounting database and calculates a new job
usage value. This subcommand takes one optional argument,
``--priority-decay-half-life`` which should be set to the same value as the
``--priority-decay-half-life`` parameter mentioned above when first creating the
database; it represents the number of weeks to hold one job usage "chunk."
If not specified, this optional argument also defaults to 1 week.

.. code-block:: console

 $ flux account update-usage

After the job usage values are re-calculated and updated, the fairshare values
for each user also need to be updated. This can be accomplished by configuring
the ``flux-update-fshare`` command to also run as the second cron job. This
fetches user account data from the flux-accounting DB and recalculates and
writes the updated fairshare values back to the DB.

.. code-block:: console

 $ flux account-update-fshare

Once the fairshare values for all of the users in the flux-accounting DB get
updated, this information will be sent to the priority plugin. The
``flux account-priority-update`` command can also be configured to run as the
third cron job to send the updated values to the plugin:

.. code-block:: console

 $ flux account-priority-update

Together, the three automatic update scripts can be combined to run as the flux
user in succession of one another via ``cron`` using a shell script like the
following example:

``flux-accounting-update.sh``

.. code-block:: sh

 #!/bin/bash

 flux account update-usage
 flux account-update-fshare
 flux account-priority-update

Job prolog/epilog configuration
===============================

As of version 0.31.0, Flux does not support a traditional job prolog and
epilog that runs on each node before and after job tasks are executed.
However, Flux does support a "job-manager" prolog and epilog, which
are run on rank 0 at the same points in a job life cycle. A convenience
command ``flux perilog-run`` is provided which can simulate a job
prolog and epilog by executing a command across the broker ranks assigned
to a job from the job-manager prolog and epilog.

To configure a per-node job prolog and epilog, run with root privileges,
currently requires three steps

 1. Configure the IMP such that it will allow the system instance user
    to execute a prolog and epilog script or command as root, e.g.
    in ``/etc/flux/imp/imp.toml``:

    .. code-block:: toml

       [run.prolog]
       allowed-users = [ "flux" ]
       path = "/etc/flux/system/prolog"

       [run.epilog]
       allowed-users = [ "flux" ]
       path = "/etc/flux/system/epilog"

    By default, the IMP will set the environment variables
    ``FLUX_OWNER_USERID``, ``FLUX_JOB_USERID``, ``FLUX_JOB_ID``, ``HOME``
    and ``USER`` for the prolog and epilog processes. ``PATH`` will
    be set explicitly to ``/usr/sbin:/usr/bin:/sbin:/bin``. To allow extra
    environment variables to be passed from the enclosing environment,
    use the ``allowed-environment`` key, which is an array of ``glob(7)``
    patterns for acceptable environment variables, e.g.

    .. code-block:: toml

       [run.prolog]
       allowed-environment = [ "FLUX_*" ]

    will pass all ``FLUX_`` environment variables to the IMP ``run``
    commands.


 2. Configure the system instance to load the job-manager ``perilog.so``
    plugin, which is not active by default:

    .. code-block:: toml

       [job-manager]
       plugins = [
         { load = "perilog.so" }
       ]

 3. Configure ``[job-manager.prolog]`` and ``[job-manager.epilog]`` to
    execute ``flux perilog-run`` with appropriate arguments:

    .. code-block:: toml

       [job-manager.prolog]
       command = [
          "flux", "perilog-run", "prolog",
          "-e", "/usr/libexec/flux/flux-imp,run,prolog"
       ]
       [job-manager.epilog]
       command = [
          "flux", "perilog-run", "epilog",
          "-e", "/usr/libexec/flux/flux-imp,run,epilog"
       ]

Note that the ``flux perilog-run`` command will additionally execute any
scripts in ``/etc/flux/system/{prolog,epilog}.d`` on rank 0 by default.
To run scripts from a different directory, use the ``-d, --exec-directory``
option in the configured ``command``.

******************************
System Instance Administration
******************************

Starting Flux
=============

Systemd may be configured to start Flux automatically at boot time,
as long as the network that carries its overlay network will be
available at that time.  Alternatively, Flux may be started manually, e.g.

.. code-block:: console

 $ sudo pdsh -w fluke[3,108,6-103] sudo systemctl start flux

Flux brokers may be started in any order, but they won't come online
until their parent in the tree based overlay network is available.


Stopping Flux
=============

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
    0.30.0 limitation: jobs using a node are not automatically canceled
    when the individual node is shut down.  On an active system, first drain
    the node as described below, then ensure no jobs are using it before
    shutting it down.

Changing the Flux configuration
===============================

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
    0.30.0 limitation: all configuration changes except resource exclusion
    and instance access have no effect until the Flux broker restarts.

Viewing Resource Status
=======================

Flux offers two different utilities to query the current resource state.

``flux resource status`` is an administrative command which lists ranks
which are available, online, offline, excluded, or drained along with
their corresponding node names. By default, sets which have 0 members
are not displayed, e.g.

.. code-block:: console

 $ flux resource status
    STATUS NNODES RANKS           NODELIST
     avail     15 1-15            fluke[26-40]
     drain      1 0               fluke25

To list a set of states explicitly, use the ``--states`` option:
(Run ``--states=help`` to get a list of valid states)

.. code-block:: console

 $ flux resource status --states=offline,exclude
    STATUS NNODES RANKS           NODELIST
   offline      0
   exclude      0

This option is useful to get a list of ranks or hostnames in a given
state. For example, the following command fetches the hostlist
for all resources configured in a Flux instance:

.. code-block:: console

 $ flux resource status -s all -no {nodelist}
 fluke[25-40]


In contrast to ``flux resource status``, the ``flux resource list``
command lists the *scheduler*'s view of available resources. This
command shows the free, allocated, and unavailable (down) resources,
and includes nodes, cores, and gpus at this time:

.. code-block:: console

 $ flux resource list
     STATE NNODES   NCORES    NGPUS NODELIST
      free     15       60        0 fluke[26-40]
 allocated      0        0        0
      down      1        4        0 fluke25


With ``-v``, ``flux resource list`` will show a finer grained list
of resources in each state, instead of a nodelist:

.. code-block:: console

 $ flux resource list -v
      STATE NNODES   NCORES    NGPUS LIST
       free     15       60        0 rank[1-15]/core[0-3]
  allocated      0        0        0
       down      1        4        0 rank0/core[0-3]


Draining Resources
==================

Resources may be temporarily removed from scheduling via the
``flux resource drain`` command. Currently, resources may only be drained
at the granularity of a node, represented by its hostname or broker rank,
for example:

.. code-block:: console

 $ sudo flux resource drain fluke7 node is fubar
 $ sudo flux resource drain
 TIMESTAMP            RANK     REASON                         NODELIST
 2020-12-16T09:00:25  4        node is fubar                  fluke7

Any work running on the drained node is allowed to complete normally.

To return drained resources use ``flux resource undrain``:

.. code-block:: console

 $ sudo flux resource undrain fluke7
 $ sudo flux resource drain
 TIMESTAMP            RANK     REASON                         NODELIST

Managing the Flux Queue
=======================

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

Disabling job submission
------------------------

By default, the queue is *enabled*, meaning that jobs can be submitted
into the system. To disable job submission, e..g to prepare the system
for a shutdown, use ``flux queue disable``. To restore queue access
use ``flux queue enable``.

Stopping job allocation
-----------------------

The queue may also be stopped with ``flux queue stop``, which disables
further allocation requests from the job-manager to the scheduler. This
allows jobs to be submitted, but stops new jobs from being scheduled.
To restore scheduling use ``flux queue start``.

Flux queue idle and drain
-------------------------

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


Managing Flux Jobs
==================

Expediting Jobs
---------------

Expediting and holding jobs is planned, but not currently supported.

Canceling Jobs
--------------

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

Updating Flux Software
======================

Flux will eventually support rolling software upgrades, but prior to
major release 1, Flux software release versions should not be assumed
to inter-operate.  Furthermore, at this early stage, Flux software
components (e.g. ``flux-core``, ``flux-sched``, ``flux-security``,
and ``flux-accounting``)  should only only be installed in recommended
combinations.

.. note::
    Mismatched broker versions are detected as brokers attempt to join
    the instance.  The version is currently required to match exactly.

.. warning::
    0.30.0 limitation: job data should be purged when updating to the
    next release of flux-core, as internal representations of data written
    out to the Flux KVS and stored in the content.sqlite file are not yet
    stable.

***************
Troubleshooting
***************

Overlay Network
===============

The tree-based overlay network interconnects brokers of the system instance.
The current status of the overlay subtree at any rank can be shown with:

.. code-block:: console

 $ flux overlay status -r RANK

The possible status values are:

**Full**
  Node is online and no children are in partial, offline, degraded, or lost
  state.

**Partial**
  Node is online, and some children are in partial or offline state; no
  children are in degraded or lost state.

**Degraded**
  Node is online, and some children are in degraded or lost state.

**Lost**
  Node has gone missing, from the parent perspective.

**Offline**
  Node has not yet joined the instance, or has been cleanly shut down.

Note that the RANK argument is where the request will be sent, not necessarily
the rank whose status is of interest.  Parents track the status of their
children, so a good approach when something is wrong to start with rank 0
(the default).  The following options can be used to ask rank 0 for a detailed
listing:

.. code-block:: console

 $ flux overlay status -vvv --ghost --pretty --color
 0: degraded
 └1: partial
  └3: offline
   └7: offline
   └8: offline
  └4: full
   └9: full
   └10: full
 └2: degraded
  └5: full
   └11: full
   └12: full
  └6: degraded
   └13: full
   └14: lost

To determine if a broker is reachable from the current rank, use:

.. code-block:: console

 $ flux ping RANK

A broker that is not responding but is not shown as lost or offline
by ``flux overlay status`` may be forcibly detached from the overlay
network with:

.. code-block:: console

 $ flux overlay disconnect RANK

However, before doing that, it may be useful to see if a broker acting
as a router to that node is actually the problem.  The overlay parent
of RANK may be listed with

.. code-block:: console

 $ flux overlay parentof RANK

Using ``flux ping`` and ``flux overlay parentof`` iteratively, one should
be able to isolate the problem rank.

Systemd journal
===============

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

Flux logs: flux-dmesg
=====================

The rank 0 broker accumulates log information for the full instance in a
circular buffer.  For some problems, it may be useful to view this log:

.. code-block:: console

 $ sudo flux dmesg |tail
 2020-09-14T19:38:38.047025Z sched-simple.debug[0]: free: rank1/core0
 2020-09-14T19:38:41.600670Z sched-simple.debug[0]: req: 6115337007267840: spec={0,1,1} duration=0.0
 2020-09-14T19:38:41.600791Z sched-simple.debug[0]: alloc: 6115337007267840: rank1/core0
 2020-09-14T19:38:41.703252Z sched-simple.debug[0]: free: rank1/core0
 2020-09-14T19:38:46.588157Z job-ingest.debug[0]: validate-jobspec.py: inactivity timeout

