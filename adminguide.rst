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
    version 0.35.0.

.. warning::
    0.35.0 limitation: the flux system instance is primarily tested on
    a 128 node cluster.

    0.35.0 limitation: Avoid powering off nodes that are running Flux
    without following the recommended shutdown procedure below.  Cluster
    nodes that may require service or have connectivity issues should be
    omitted from the Flux configuration for now.

********
Overview
********

The base component of Flux is the ``flux-broker`` executable.  Most of
Flux's distributed systems and services that aren't directly associated
with a running job are embedded in that executable or its dynamically loaded
plugins.

Flux is often used in *single-user mode*, where a Flux instance (a ranked
set of brokers) is launched as a parallel job, and the *instance owner*
(the user that submitted the parallel job) has control of, and exclusive
access to, the resources assigned to the instance.  In fact, this user
has complete administrative control over the single user instance, including
the ability to alter Flux software.

When Flux is deployed as the native resource manager on a cluster, its brokers
still execute with the credentials of a non-privileged instance owner, but the
Flux instance operates somewhat differently:

- The Flux broker is started directly by systemd on each node instead of
  being launched as a process in a parallel job.
- The systemd unit file passes arguments to the broker that tell it to use
  system paths for various files, and to ingest TOML files from a system
  configuration directory.
- A single security certificate is used for the entire cluster instead of
  each broker generating one on the fly and exchanging public keys with PMI.
- The Flux overlay network endpoints are statically configured from files
  instead of being generated on on the fly and exchanged via PMI.
- The instance owner is a system account that does not correspond to an
  actual user.
- Users other than the instance owner (*guests*) are permitted to connect
  to the Flux broker, and are granted limited access to Flux services.
- Users connect to the Flux broker's AF_UNIX socket via a well known system URI
  if FLUX_URI is not set in the environment.
- Job processes (including the Flux job shell) are launched as the submitting
  user with the assistance of a setuid root helper on each node called the IMP.
- Job requests are signed with MUNGE, and this signature is verified by the IMP.
- The content of the Flux KVS, containing system state such as the set of
  drained nodes and the job queue, is preserved across a full Flux restart.
- The system instance functions with some nodes offline.
- The system instance has no *initial program*.

The same Flux executables are used in both single user and system modes,
with operation differentiated only by configuration.

Although a Flux single user instance can be launched by any resource manager
or process launcher, a single user Flux instance has access to a richer
environment when it is launched by a Flux system instance.  For example,
the Fluxion graph scheduler can hierarchically schedule advanced resource types
when its resources are statically configured at the system level;  otherwise,
Fluxion is limited to resource types and relationships that can be dynamically
probed.

.. figure:: images/adminarch.png
   :alt: Flux system instance architecture
   :align: center

   Fox prevents Frog from submitting jobs on a cluster with Flux
   as the system resource manager.

Some aspects of Flux have matured in the single user environment, however Flux
has a ways to go to reach feature parity with system level resource managers
like SLURM.  Flux limitations are documented in warning boxes throughout this
text.  Most are expected to be short term obstacles as Flux system capability
is expanded to meet deployment goals in 2022.  During this period of
development and testing, we appreciate your design feedback, bug reports,
and patience.

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

Software
========

The following Flux framework packages are needed for a Flux system instance
and should be installed from your Linux distribution package manager.

flux-core
  All of the core components of Flux, including the Flux broker.
  flux-core is functional on its own, but cannot run jobs as multiple users,
  has a simple FIFO scheduler, and does not implement accounting-based job
  prioritization. Install on all nodes (required).

flux-security
  APIs for job signing, and the IMP, a privileged program for starting
  processes as multiple users. Install on all nodes (required).

flux-sched
  The Fluxion graph-based scheduler.  Install on management node
  (optional, but recommended).

flux-accounting
  Accounting database of user/bank usage information, and a priority plugin.
  Install on management node (optional, early preview users only).

.. note::
    Flux packages are currently maintained only for the
    `TOSS <https://computing.llnl.gov/projects/toss-speeding-commodity-cluster-computing>`_
    Red Hat Enterprise Linux based Linux distribution, which is not publicly
    distributed.  Open an issue in `flux-core <https://github.com/flux-framework/flux-core>`_
    if you would like to become a maintainer of Flux packages for another Linux
    distribution so we can share packaging tips and avoid duplicating effort.


*******************
Configuration files
*******************

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

See also: :core:man5:`flux-config` and :security:man5:`flux-config-security`.

Multi-user
==========

In order to run multi-user workloads ``flux-security`` components such
as the signing library and ``flux-imp`` need proper configuration.
First, configure MUNGE as the method used to sign job requests:

.. code-block:: toml

 # /etc/flux/security/conf.d/sign.toml

 [sign]
 max-ttl = 1209600  # 2 weeks
 default-type = "munge"
 allowed-types = [ "munge" ]

See also: :security:man5:`flux-config-security-sign`.

Then configure the IMP to ensure that only the ``flux`` user may run
the ``flux-imp`` executable, and the only allowed job shell is the system
installed ``flux-shell``.

.. code-block:: toml

 # /etc/flux/imp/conf.d/imp.toml

 [exec]
 allowed-users = [ "flux" ]
 allowed-shells = [ "/usr/libexec/flux/flux-shell" ]

See also: :security:man5:`flux-config-security-imp`.

The ``job-exec`` module must be configured to use the ``flux-imp`` process
as its privileged helper for multi-user execution:

.. code-block:: toml

 # /etc/flux/system/conf.d/exec.toml

 [exec]
 imp = "/usr/libexec/flux/flux-imp"

See also: :core:man5:`flux-config-exec`.

By default, a Flux instance does not allow access to any user other than
the instance *owner*, in this case the ``flux`` user.  This is not
suitable for a system instance, so *guest user* access should be enabled.
In addition, for convenience, the ``root`` user should be allowed to act
in the role of instance owner:

.. code-block:: toml

 # /etc/flux/system/conf.d/access.toml

 [access]
 allow-guest-user = true
 allow-root-owner = true

See also: :core:man5:`flux-config-access`.

Network
=======

Flux brokers on each node communicate over a tree based overlay network.
Each broker is assigned a ranked integer address, starting with zero.
The overlay network may be configured to use any IP network that remains
available the whole time Flux is running.

Overlay network security requires a certificate to be distributed to all nodes.
It should be readable only by the ``flux`` user.  To create a new certificate,
run :core:man1:`flux-keygen` as the ``flux`` user:

.. code-block:: console

 $ sudo -u flux flux keygen /etc/flux/system/curve.cert

Do this once and then copy the certificate to the same location on
the other nodes, preserving owner and mode.

.. warning::
    0.35.0 limitation: the system instance tree based overlay network
    is forced by the systemd unit file to be *flat* (no interior router
    nodes), trading scalability for reliability.

The Flux system instance overlay is currently configured via a cluster
specific config file. The example here is for a 16 node cluster with
hostnames ``test1`` through ``test16``.

.. code-block:: toml

 # /etc/flux/system/conf.d/bootstrap.toml

 [bootstrap]
 curve_cert = "/etc/flux/system/curve.cert"

 default_port = 8050
 default_bind = "tcp://eth0:%p"
 default_connect = "tcp://%h:%p"

 hosts = [
    { host = "test[1-16]" },
 ]

See also: :core:man5:`flux-config-bootstrap`.

Hosts are assigned ranks in the overlay network based on their position in the
host array. In the above example ``test1`` is rank 0, ``test2`` is rank 1, etc.

The Flux rank 0 broker hosts the majority of Flux's services, has a critical
role in overlay network routing, and requires access to persistent storage,
preferably local.  Therefore, rank 0 ideally will be placed on a non-compute
node along with other critical cluster services.

.. warning::
    0.35.0 limitation: Flux should be completely shut down when the
    overlay network configuration is modified.

Flux enables TCP keepalives to detect compute nodes that are abruptly turned
off.  If system-wide TCP keepalive parameters are not already tuned to values
appropriate for cluster software, Flux should configure values for its overlay
sockets.  The following configures keepalive probes to begin after 30s of
inactivity, to re-transmit every 10s, and to disconnect after 12 probes are sent
with no response.  Thus a powered off node is detected after 2.5m.

.. code-block:: toml

 # /etc/flux/system/conf.d/tbon.toml

 [tbon]
 keepalive_count = 12
 keepalive_interval = 10
 keepalive_idle = 30

See also: :core:man5:`flux-config-tbon`.

Resources
=========

The system resource configuration may be generated in RFC 20 (R version 1)
form using ``flux R encode``.  At minimum, a hostlist and core idset must
be specified on the command line, e.g.

.. code-block:: console

 $ flux R encode --hosts=fluke[3,108,6-103] --cores=0-3 >/etc/flux/system/R

Alternatively, if the Fluxion scheduler is installed, run the following command:

.. code-block:: console

 $ flux R encode --hosts=fluke[3,108,6-103] --cores=0-3 | flux ion-R encode >/etc/flux/system/R

The ``flux ion-R encode`` filter simply adds the optional ``scheduling`` key
of RFC 20 to the resource configuration generated by ``flux R encode``.
Our Fluxion scheduler relies on the existence of this key containing resource
graph data in the JSON Graph Format (JGF) for system instance scheduling.

The resource configuration ``R`` is then referenced from the configuration
file below.

.. note::
    The rank to hostname mapping represented in R is ignored, and is
    replaced at runtime by the rank to hostname mapping from the bootstrap
    hosts array (see above).

Some sites may choose to exclude login and service nodes from scheduling.
This is accomplished using the optional ``exclude`` key, whose value is
a hostlist, or alternatively, idset of broker ranks to exclude.

An example resource configuration:

.. code-block:: toml

 # /etc/flux/system/conf.d/resource.toml

 [resource]
 path = "/etc/flux/system/R"
 exclude = "fluke[3,108]"

See also: :core:man5:`flux-config-resource`.

KVS backing store
=================

Flux is prolific in its use of disk space to back up its key value store,
proportional to the number of jobs run and the quantity of standard I/O.
On your rank 0 node, ensure that the directory for the ``content.sqlite``
file exists with plenty of space:

.. code-block:: console

 $ sudo mkdir -p /var/lib/flux
 $ chown flux /var/lib/flux
 $ chomd 700 /var/lib/flux

This space should be preserved across a reboot as it contains the Flux
job queue and record of past jobs.

.. warning::
    0.35.0 limitation: tools for shrinking the content.sqlite file or
    purging old job data while retaining other content are not yet available.

    0.35.0 limitation: Flux must be completely stopped to relocate or remove
    the content.sqlite file.

    0.35.0 limitation: Running out of space is not handled gracefully.
    If this happens it is best to stop Flux, remove the content.sqlite file,
    and restart.

Accounting
==========

If ``flux-accounting`` was installed, some additional setup on the management
node is needed.  All commands shown below should be run as the ``flux`` user.

.. note::
    The flux-accounting database must contain user bank assignments for
    all users allowed to run on the system.  If a site has an identity
    management system that adds and removes user access, the accounting
    database should be included in its update process so it remains in sync
    with access controls.

Database creation
-----------------

The accounting database is created with the command below.  Default
parameters are assumed, including the accounting database path of
``/var/lib/flux/FluxAccounting.db``.

.. code-block:: console

 $ flux account create-db

Banks must be added to the system, for example:

.. code-block:: console

 $ flux account add-bank root 1
 $ flux account add-bank --parent-bank=root sub_bank_A 1

Users that are permitted to run on the system must be assigned banks,
for example:

.. code-block:: console

 $ flux account add-user --username=user1234 --bank=sub_bank_A

Multi-factor priority plugin
----------------------------

When flux-accounting is installed, the job manager uses a multi-factor
priority plugin to calculate job priorities.  The plugin must be listed in
the job manager config file:

.. code-block:: toml

 # /etc/flux/system/conf.d/job-manager.toml

 [job-manager]
 plugins = [
   { load = "mf_priority.so" },
 ]

See also: :core:man5:`flux-config-job-manager`.

Automatic updates
-----------------

A series of actions should run periodically to keep the accounting
system in sync with Flux:

- The job-archive module scans inactive jobs and dumps them to a sqlite
  database.
- A script reads the archive database and updates the job usage data in the
  accounting database.
- A script updates the per-user fair share factors in the accounting database.
- A script pushes updated factors to the multi-factor priority plugin.

The ``job-archive`` module must be configured to run periodically:

.. code-block:: toml

 # /etc/flux/system/conf.d/archive.toml``

 [archive]
 dbpath = "/var/lib/flux/job-archive.sqlite"
 period = "1m"
 busytimeout = "50s"

The scripts should be run by :core:man1:`flux-cron`:

See also: :core:man5:`flux-config-archive`.

.. code-block:: console

 # /etc/flux/system/cron.d/accounting

 30 * * * * bash -c "flux account update-usage --job-archive_db_path=/var/lib/flux/job-archive.sqlite; flux account-update-fshare; flux account-priority-update"

Job prolog/epilog
=================

As of 0.35.0, Flux does not support a traditional job prolog/epilog
which runs as root on the nodes assigned to a job before/after job
execution. Flux does, however, support a job-manager prolog/epilog,
which is run at the same point on rank 0 as the instance
owner (typically user ``flux``), instead of user root.

As a temporary solution, a convenience command ``flux perilog-run``
is provided which can simulate a job prolog and epilog by executing a
command across the broker ranks assigned to a job from the job-manager
prolog and epilog.

When using ``flux perilog-run`` to execute job prolog and epilog, the
job-manager prolog/epilog feature is being used to execute a privileged
prolog/epilog across the nodes/ranks assigned to a job, via the
flux-security IMP "run" command support. Therefore, each of these
components need to be configured, which is explained in the steps below.

To configure a per-node job prolog and epilog, run with root privileges,
currently requires three steps

 1. Configure the IMP such that it will allow the system instance user
    to execute a prolog and epilog script or command as root:

    .. code-block:: toml

       # /etc/flux/imp/conf.d/imp.toml

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
    plugin, which is not active by default. This plugin enables job-manager
    prolog/epilog support in the instance:

    .. code-block:: toml

       # /etc/flux/system/conf.d/job-manager.toml

       [job-manager]
       plugins = [
         { load = "perilog.so" }
       ]

 3. Configure ``[job-manager.prolog]`` and ``[job-manager.epilog]`` to
    execute ``flux perilog-run`` with appropriate arguments to execute
    ``flux-imp run prolog`` and ``flux-imp run epilog`` across the ranks
    assigned to a job:

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
scripts in ``/etc/flux/system/{prolog,epilog}.d`` on rank 0 by default as
part of the job-manager prolog/epilog. Only place scripts here if there is
a need to execute scripts as the instance owner (user `flux`) on a single
rank for each job. If only traditional prolog/epilog support is required,
these directories can be ignored and should be empty or nonexistent.
To run scripts from a different directory, use the ``-d, --exec-directory``
option in the configured ``command``.

See also: :core:man5:`flux-config-job-manager`,
:security:man5:`flux-config-security-imp`.


*************************
Day to day administration
*************************

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

Configuration update
====================

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
    0.35.0 limitation: all configuration changes except resource exclusion
    and instance access have no effect until the Flux broker restarts.

Viewing resource status
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

Draining resources
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

Managing the Flux queue
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

The queue may be listed with the :core:man1:`flux-jobs` command.

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

Managing Flux jobs
==================

Expediting/Holding jobs
-----------------------

To expedite or hold a job, set its *urgency* to the special values
EXPEDITE or HOLD.

.. code-block:: console

 $ flux job urgency ƒAiVi2Sj EXPEDITE

.. code-block:: console

 $ flux job urgency ƒAiVi2Sj HOLD

Canceling jobs
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

Software update
===============

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
    0.35.0 limitation: job data should be purged when updating to the
    next release of flux-core, as internal representations of data written
    out to the Flux KVS and stored in the content.sqlite file are not yet
    stable.

***************
Troubleshooting
***************

Overlay network
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

 $ flux overlay status
 0 fluke62: degraded
 ├─ 1 fluke63: full
 │  ├─ 3 fluke65: full
 │  │  ├─ 7 fluke70: full
 │  │  └─ 8 fluke71: full
 │  └─ 4 fluke67: full
 │     ├─ 9 fluke72: full
 │     └─ 10 fluke73: full
 └─ 2 fluke64: degraded
    ├─ 5 fluke68: full
    │  ├─ 11 fluke74: full
    │  └─ 12 fluke75: full
    └─ 6 fluke69: degraded
       ├─ 13 fluke76: full
       └─ 14 fluke77: lost

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

Broker log buffer
=================

The rank 0 broker accumulates log information for the full instance in a
circular buffer.  For some problems, it may be useful to view this log:

.. code-block:: console

 $ sudo flux dmesg |tail
 2020-09-14T19:38:38.047025Z sched-simple.debug[0]: free: rank1/core0
 2020-09-14T19:38:41.600670Z sched-simple.debug[0]: req: 6115337007267840: spec={0,1,1} duration=0.0
 2020-09-14T19:38:41.600791Z sched-simple.debug[0]: alloc: 6115337007267840: rank1/core0
 2020-09-14T19:38:41.703252Z sched-simple.debug[0]: free: rank1/core0
 2020-09-14T19:38:46.588157Z job-ingest.debug[0]: validate-jobspec.py: inactivity timeout

