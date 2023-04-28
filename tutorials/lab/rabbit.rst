.. _rabbit:

=================
Flux with Rabbits
=================


How to Allocate Rabbit Storage
------------------------------

Request rabbit storage allocations for a job
by setting the ``.attributes.system.dw`` field in a jobspec to
a string containing one or more DW directives, or to a list of
singleton DW directives.

DW directives are strings that start with ``#DW``. Directives
that begin with ``#DW jobdw`` are for requesting storage that
lasts the lifetime of the associated flux job. Directives that
begin with ``#DW copy_in`` and ``#DW copy_out`` are for
describing data movement to and from the rabbits, respectively.

The usage is most easily understood by example.


Examples of jobdw directives
----------------------------

Requesting a 10 gigabyte XFS file system per compute node on the
command line:

.. code-block:: console

	$ flux alloc -N2 --setattr=dw="#DW jobdw type=xfs capacity=10GiB name=project1"

Requesting both XFS and lustre file systems in a batch script:

.. code-block:: bash

	#!/bin/bash

	#FLUX: -N 2
	#FLUX: -q pdebug
	#FLUX: --setattr=dw="""
	#FLUX: #DW jobdw type=xfs capacity=1TiB name=xfsproject
	#FLUX: #DW jobdw type=lustre capacity=10GiB name=lustreproject
	#FLUX: """

	echo "Hello World!" > $DW_JOB_lustreproject/world.txt

	flux submit -N2 -n2 /bin/bash -c "echo 'Hello World!' > $DW_JOB_xfsproject/world.txt"


jobdw directive fields
----------------------

The **type** field can be one of ``xfs``, ``lustre``, ``gfs2``, or ``raw``.
``lustre`` storage is shared by all nodes in the job. By contrast, the other types
are for node-local storage. Processes on one node will not be able to read
data written on other nodes. Currently only ``xfs`` and ``lustre`` are known
to work properly.

The **capacity** field describes how much storage to be allocated. For ``lustre``
the capacity refers to the overall capacity. For all other types, the capacity refers
to the capacity per node. See
`this Wikipedia article <https://en.wikipedia.org/wiki/Byte#Multiple-byte_units>`_
for the meaning of the suffixes.

The **name** field determines the suffix to the ``DW_JOB_`` environment variable.
See below for more detail.


Using Rabbit Storage
--------------------

For each ``jobdw`` directive associated with your job, your job will have
an environment variable ``DW_JOB_[name]`` where ``[name]`` is the value
of the ``name`` field in the directive. The value of the environment variable
will be the path to the associated file system.

For instance, for a directive ``#DW jobdw type=xfs capacity=10GiB name=project1``,
the associated job will have an environment variable ``DW_JOB_project1``.


Data Movement Directives
------------------------

To request that files be moved to or from the rabbits, additional DW
directives must be added to the job in addition to jobdw directives.
The ``copy_in`` directive is for moving data to the rabbits before the job
starts, and the ``copy_out`` directive is for moving data from the rabbits
after the job completes.

Both ``copy_in`` and ``copy_out`` directives have ``source`` and ``destination``
fields which indicate where data is to be taken from and where it is to be moved to.
The source must exist.


Data Movement Examples
----------------------

.. warning::

	When writing ``copy_in`` and ``copy_out`` directives *on the command line*,
	be careful to always escape the ``$`` character when writing ``DW_JOB_[name]``
	variables. Otherwise your shell will expand them. This warning does not apply
	to batch scripts.

Requesting a 10 gigabyte XFS file system per compute node on the command
line with data movement both to and from the rabbits (the source directory
is assumed to exist):

.. code-block:: console

	$ flux alloc -N2 --setattr=dw="#DW jobdw type=xfs capacity=10GiB name=project1
	#DW copy_in source=/p/lustre1/$USER/dir_in destination=\$DW_JOB_project1/
	#DW copy_out source=\$DW_JOB_project1/ destination=/p/lustre1/$USER/dir_out/"

Requesting a lustre file system, with data movement out from the rabbits,
in a batch script:

.. code-block:: bash

	#!/bin/bash

	#FLUX: -N 2
	#FLUX: -q pdebug
	#FLUX: --setattr=dw="""
	#FLUX: #DW jobdw type=lustre capacity=10GiB name=lustreproject
	#FLUX: #DW copy_out source=$DW_JOB_lustreproject destination=/p/lustre1/$USER/lustreproject_results
	#FLUX: """

	echo "Hello World!" > $DW_JOB_lustreproject/world.txt

