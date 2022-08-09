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


********
Glossary
********

association
  A 2-tuple combination of a username and bank name.

bank
  An account that contains associations.

.. _documentation: https://sqlite.org/omitted.html
