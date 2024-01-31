.. _flux-accounting-guide:

#####################
Flux Accounting Guide
#####################

*key terms: association, bank*

.. note::
    flux-accounting is still beta software and many of the interfaces
    documented in this guide may change with regularity.

    This document is in DRAFT form and currently applies to flux-accounting
    version 0.18.1.

********
Overview
********

By default, a Flux system instance treats users equally and schedules work
based on demand, without consideration of a user's history of resource
consumption, or what share of available resources their organization considers
they should be entitled to use relative to other competing users.

Flux-accounting adds a database which stores site policy, *banks* with
with user/project associations, and metrics representing historical usage.
It also adds a Flux jobtap plugin that sets the priority on each job that
enters the system based on multiple factors including *fair share* values.
The priority determines the order in which jobs are considered by the scheduler
for resource allocation.  In addition, the jobtap plugin holds or rejects job
requests that exceed user/project specific limits or have exhausted their
bank allocations.

The database is populated and queried with command line tools prefixed with
``flux account``.  Accounting scripts are run regularly by
:core:man1:`flux-cron` to pull historical job information from the Flux
``job-archive`` database to the accounting database, and to push bank and limit
data to the jobtap plugin.

At this time, the database is expected to be installed on a cluster management
node, co-located with the rank 0 Flux broker, managing accounts for that
cluster only.  Sites would typically populate the database and keep it up to
date automatically using information regularly pulled or pushed from an
external source like an identity management system.

******************************
Installation and Configuration
******************************

System Prerequisites
====================

The `Flux Administrator's Guide <https://flux-framework.readthedocs.io/projects/flux-core/en/latest/guide/admin.html>`_ documents relevant information for
the administration and management of a Flux system instance.

The following instructions assume that Flux is configured and working, that
the Flux *statedir* (``/var/lib/flux``) is writable by the ``flux`` user,
and that the ``flux`` user is the system instance owner.

Installing Software Packages
============================

The ``flux-accounting`` package should be installed on the management node
from your Linux distribution package manager.

Accounting Database Creation
============================

The accounting database is created with the command below.  Default
parameters are assumed, including the accounting database path of
``/var/lib/flux/FluxAccounting.db``.

.. code-block:: console

 $ sudo -u flux flux account create-db

.. note::
    The flux accounting commands should always be run as the flux user. If they
    are run as root, some commands that rewrite the database could change the
    owner to root, causing flux-accounting scripts run from flux cron to fail.

Banks must be added to the system, for example:

.. code-block:: console

 $ sudo -u flux flux account add-bank root 1
 $ sudo -u flux flux account add-bank --parent-bank=root sub_bank_A 1

Users that are permitted to run on the system must be assigned banks,
for example:

.. code-block:: console

 $ sudo -u flux flux account add-user --username=user1234 --bank=sub_bank_A

Enabling Multi-factor Priority
==============================

When flux-accounting is installed, the job manager uses a multi-factor
priority plugin to calculate job priorities.  The Flux system instance must
configure the ``job-manager`` to load this plugin.

.. code-block:: toml

 [job-manager]
 plugins = [
   { load = "mf_priority.so" },
 ]

See also: :core:man5:`flux-config-job-manager`.

Automatic Accounting Database Updates
=====================================

If updating flux-accounting to a newer version on a system where a
flux-accounting DB is already configured and set up, it is important to update
the database schema, as tables and columns may have been added or removed in
the newer version. The flux-accounting database schema can be updated with the
following command:

.. code-block:: console

 $ sudo -u flux flux account-update-db

A series of actions should run periodically to keep the accounting
system in sync with Flux:

- The job-archive module scans inactive jobs and dumps them to a sqlite
  database.
- A script reads the archive database and updates the job usage data in the
  accounting database.
- A script updates the per-user fair share factors in the accounting database.
- A script pushes updated factors to the multi-factor priority plugin.

The Flux system instance must configure the ``job-archive`` module to run
periodically:

.. code-block:: toml

 [archive]
 period = "1m"

See also: :core:man5:`flux-config-archive`.

The scripts should be run by :core:man1:`flux-cron`:

.. code-block:: console

 # /etc/flux/system/cron.d/accounting

 30 * * * * bash -c "flux account update-usage --job-archive_db_path=/var/lib/flux/job-archive.sqlite; flux account-update-fshare; flux account-priority-update"

***********************
Database Administration
***********************

The flux-accounting database is a SQLite database which stores user account
information and bank information. Administrators can add, disable, edit, and
view user and bank information by interfacing with the database through
front-end commands provided by flux-accounting. The information in this
database works with flux-core to calculate job priorities submitted by users,
enforce basic job accounting limits, and calculate fair-share values for
users based on previous job usage.

Each user belongs to at least one bank. This user/bank combination is known
as an *association*, and henceforth will be referred to as an *association*
throughout the rest of this document.

.. note::
    In order to interact with the flux-accounting database, you must have read
    and write permissions to the directory that the database resides in. The
    SQLite documentation_ states that since "SQLite reads and writes an ordinary
    disk file, the only access permissions that can be applied are the normal
    file access permissions of the underlying operating system."

The front-end commands provided by flux-accounting allow an administrator to
interact with association or bank information.  ``flux account -h`` will list
all possible commands that interface with the information stored in their
respective tables in the flux-accounting database. The current database
consists of the following tables:

+--------------------------+--------------------------------------------------+
| table name               | description                                      |
+==========================+==================================================+
| association_table        | stores associations                              |
+--------------------------+--------------------------------------------------+
| bank_table               | stores banks                                     |
+--------------------------+--------------------------------------------------+
| job_usage_factor_table   | stores past job usage factors for associations   |
+--------------------------+--------------------------------------------------+
| t_half_life_period_table | keeps track of the current half-life period for  |
|                          | calculating job usage factors                    |
+--------------------------+--------------------------------------------------+
| queue_table              | stores queues, their limits properties, as well  |
|                          | as their associated priorities                   |
+--------------------------+--------------------------------------------------+
| project_table            | stores projects for associations to charge their |
|                          | jobs against                                     |
+--------------------------+--------------------------------------------------+

To view all associations in a flux-accounting database, the ``flux
account-shares`` command will print this DB information in a hierarchical
format. An example is shown below:

.. code-block:: console

 $ flux account-shares

 Account                         Username           RawShares            RawUsage           Fairshare
 root                                                       1                   0
  bank_A                                                    1                   0
   bank_A                          user_1                   1                   0                 0.5
  bank_B                                                    1                   0
   bank_B                          user_2                   1                   0                 0.5
   bank_B                          user_3                   1                   0                 0.5
  bank_C                                                    1                   0
   bank_C_a                                                 1                   0
    bank_C_a                       user_4                   1                   0                 0.5
   bank_C_b                                                 1                   0
    bank_C_b                       user_5                   1                   0                 0.5
    bank_C_b                       user_6                   1                   0                 0.5


****************************
Job Usage Factor Calculation
****************************

An association's job usage represents their usage on a cluster in relation to
the size of their jobs and how long they ran. The raw job usage value is
defined as the sum of products of the number of nodes used (``nnodes``) and
time elapsed (``t_elapsed``):

.. code-block:: console

  RawUsage = sum(nnodes * t_elapsed)

This job usage factor per association has a half-life decay applied to it as
time passes. By default, this half-life decay is applied to jobs every week
for four weeks; jobs older than four weeks no longer play a role in determining
an association's job usage factor. The configuration parameters that determine
how to represent a half-life for jobs and how long to consider jobs as part of
an association's overall job usage are represented by **PriorityDecayHalfLife**
and  **PriorityUsageResetPeriod**, respectively. These parameters are
configured when the flux-accounting database is first created.

Example Job Usage Calculation
=============================

Below is an example of how flux-accounting calculates an association's current
job usage. Let's say a user has the following job records from the most
recent half-life period (by default, jobs that have completed in the
last week):

.. code-block:: console

     UserID Username  JobID         T_Submit            T_Run       T_Inactive  Nodes                                                                               R
  0    1002     1002    102 1605633403.22141 1605635403.22141 1605637403.22141      2  {"version":1,"execution": {"R_lite":[{"rank":"0","children": {"core": "0"}}]}}
  1    1002     1002    103 1605633403.22206 1605635403.22206 1605637403.22206      2  {"version":1,"execution": {"R_lite":[{"rank":"0","children": {"core": "0"}}]}}
  2    1002     1002    104 1605633403.22285 1605635403.22286 1605637403.22286      2  {"version":1,"execution": {"R_lite":[{"rank":"0","children": {"core": "0"}}]}}
  3    1002     1002    105 1605633403.22347 1605635403.22348 1605637403.22348      1  {"version":1,"execution": {"R_lite":[{"rank":"0","children": {"core": "0"}}]}}
  4    1002     1002    106 1605633403.22416 1605635403.22416 1605637403.22416      1  {"version":1,"execution": {"R_lite":[{"rank":"0","children": {"core": "0"}}]}}

From these job records, we can gather the following information:

* total nodes used (``nnodes``): 8
* total time elapsed (``t_elapsed``): 10000.0

So, the usage of the association from this current half life is:

.. code-block:: console

  sum(nnodes * t_elapsed) = (2 * 2000) + (2 * 2000) + (2 * 2000) + (1 * 2000) + (1 * 2000)
                          = 4000 + 4000 + 4000 + 2000 + 2000
                          = 16000

This current job usage is then added to the association's previous job usage
stored in the flux-accounting database. This sum then represents the
association's overall job usage.

****************************
Multi-Factor Priority Plugin
****************************

The multi-factor priority plugin is a jobtap_ plugin that generates
an integer job priority for incoming jobs in a Flux system instance. It uses
a number of factors to calculate a priority and, in the future, can add more
factors. Each factor has an associated integer weight that determines its
importance in the overall priority calculation. The current factors present in
the multi-factor priority plugin are:

* **fair-share**: the ratio between the amount of resources allocated vs. resources
  consumed. See the :ref:`Glossary definition <glossary-section>` for a more
  detailed explanation of how fair-share is utilized within flux-accounting.

* **urgency**: a user-controlled factor to prioritize their own jobs.

In addition to generating an integer priority for submitted jobs in a Flux
system instance, the multi-factor priority plugin also enforces per-association
job limits to regulate use of the system. The two per-association limits
enforced by this plugin are:

* **max_active_jobs**: a limit on how many *active* jobs an association can have at
  any given time. Jobs submitted after this limit has been hit will be rejected
  with a message saying that the association has hit their active jobs limit.

* **max_running_jobs**: a limit on how many *running* jobs an association can have
  at any given time. Jobs submitted after this limit has been hit will be held
  by adding a ``max-running-jobs-user-limit`` dependency until one of the
  association's currently running jobs finishes running.

Both "types" of jobs, *running* and *active*, are based on Flux's definitions
of job states_. *Active* jobs can be in any state but INACTIVE. *Running* jobs
are jobs in both RUN and CLEANUP states.

.. _glossary-section:

********
Glossary
********

association
  A 2-tuple combination of a username and bank name.

bank
  An account that contains associations.

fair-share
  A metric used to ensure equitable resource allocation among associations
  within a shared system. It represents the ratio between the amount of
  resources an association is allocated versus the amount actually consumed.
  The fair-share value influences an association's priority when submitting
  jobs to the system, adjusting dynamically to reflect current usage compared
  to allocated quotas. High consumption relative to allocation can decrease an
  association's fair-share value, reducing their priority for future resource
  allocation, thereby promoting balanced usage across all associations to
  maintain system fairness and efficiency.

.. note::

 The design of flux-accounting was driven by LLNL site requirements. Years ago,
 the design of `Slurm accounting`_ and its `multi-factor priority
 plugin`_ were driven by similar LLNL site requirements. We chose to
 reuse terminology and concepts from Slurm to facilitate a smooth transition to
 Flux. The flux-accounting code base is all completely new, however.

.. _documentation: https://sqlite.org/omitted.html

.. _Slurm accounting: https://slurm.schedmd.com/accounting.html

.. _multi-factor priority plugin: https://slurm.schedmd.com/priority_multifactor.html

.. _jobtap: https://flux-framework.readthedocs.io/projects/flux-core/en/latest/man7/flux-jobtap-plugins.html#flux-jobtap-plugins-7

.. _states: https://flux-framework.readthedocs.io/projects/flux-rfc/en/latest/spec_21.html
