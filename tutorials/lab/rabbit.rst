.. _rabbit:

=================
Flux with Rabbits
=================


How to Allocate Rabbit Storage
------------------------------

Request rabbit storage allocations for a job
by setting the ``.attributes.system.dw`` field in a jobspec to
a string containing one or more DW directives. A JSON list of DW directives
is also accepted, but cannot be provided on the command line (it is more
useful when constructing jobspecs by another means, for instance in Python).

DW directives are strings that start with ``#DW``. Directives
that begin with ``#DW jobdw`` are for requesting storage that
lasts the lifetime of the associated flux job. Directives that
begin with ``#DW copy_in`` and ``#DW copy_out`` are for
describing data movement to and from the rabbits, respectively.

Full documentation of the DW directives and their arguments is available
`here <https://nearnodeflash.github.io/dev/guides/user-interactions/readme/>`_.

The usage with Flux is most easily understood by example.


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
	#FLUX: #DW jobdw type=lustre capacity=100GiB name=lustreproject
	#FLUX: #DW copy_out source=$DW_JOB_lustreproject destination=/p/lustre1/$USER/lustreproject_results
	#FLUX: """

	echo "Hello World!" > $DW_JOB_lustreproject/world.txt

