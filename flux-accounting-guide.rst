.. _flux-accounting-guide:

#####################
Flux-Accounting Guide
#####################

*key terms: association, bank*

The *Flux Accounting Administrator's Guide* documents relevant information for
the administration and management of flux-accounting components alongside a
system instance install of Flux.

.. note::
    flux-accounting is still beta software and many of the interfaces 
    documented in this guide may change with regularity.

    This document is in DRAFT form and currently applies to flux-accounting
    version 0.18.1.

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

********
Glossary
********

association
  A 2-tuple combination of a username and bank name.

bank
  An account that contains associations.

.. _documentation: https://sqlite.org/omitted.html
