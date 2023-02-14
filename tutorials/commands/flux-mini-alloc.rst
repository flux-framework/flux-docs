.. _flux-mini-alloc:
.. _flux-mini-batch:

===============================
How to Create Flux Subinstances
===============================

One of the most powerful features in Flux is the ability create Flux
:ref:`subinstances<subinstance>`.  They are complete Flux instances of a subset
of resources.  In other words, a new scheduler, job queue, and all Flux services
are recreated just for those subset of resources.

Why are subinstances useful?

* A subinstance is largely independent of the parent Flux instance.  This allows for more
  work to be distributed across the system and leads to better performance overall.  For example,
  see :ref:`Fast Job Scheduling<fast-job-scheduling>` for information on how subinstances
  can improve the performance of job submissions.

* Subinstances can be customized per user needs.  For example, perhaps the user would like
  a different scheduling policy than the system instance.

* Subinstances can create additional subinstances, which may be useful for performance as well as
  division of resources for scheduling.

This tutorial will cover the basics of creating subinstances on the command line.

-------------------------------
Subinstance via Flux Mini Alloc
-------------------------------

This tutorial assumes you are beginning on a cluster with a Flux system instance.  I'm on a cluster that is 125
nodes in size, which we can see with ``flux resource list``.

.. code-block:: console

    corona-login-node:~$ flux resource list
         STATE NNODES   NCORES    NGPUS NODELIST
          free     50     2400      400 corona[226-247,250-259,262-267,285-296]
     allocated     63     3024      504 corona[171,173-194,196-201,203-207,213-225,268-283]
          down      8      384       64 corona[172,195,202,248-249,260-261,284]

The default "depth" or "instance level" of the system instance is level 0.

.. code-block:: console

    corona-login-node:~$ flux getattr instance-level
    0

One way to create a subinstance is through ``flux mini alloc``.  Lets launch a 4 node subinstance on a cluster
using the ``-N`` option.

.. code-block:: console

   corona-login-node:~$ flux mini alloc -N4

   corona171:~$ flux resource list
        STATE NNODES   NCORES    NGPUS NODELIST
         free      4      192       32 corona[171,173-175]
    allocated      0        0        0
         down      0        0        0

   corona171:~$ flux getattr instance-level
   1

Notice that we were previously on the node "corona-login-node" and now we are on "corona171".
The ``flux mini alloc`` command has dropped us into a shell within our own Flux subinstance.

We can see with ``flux resource list`` that our Flux subinstance contains 4 nodes, a subset of
the resources of the parent instance.  In addition, we can see that we are now at an instance level of 1.

We can submit a job to our subinstance via ``flux mini submit``.  Lets name the job "Level1" using
the ``--job-name`` option and request one node via the ``-N`` option.

.. code-block:: console

   corona171:~$ flux mini submit --job-name=Level1 -N1 sleep inf
   ƒLU5z2zj

   corona171:~$ flux jobs
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
        ƒLU5z2zj achu     Level1      R      1      1   14.58s corona175

   corona171:~$ flux resource list
         STATE NNODES   NCORES    NGPUS NODELIST
          free      3      144       24 corona[171,173-174]
     allocated      1       48        8 corona175
          down      0        0        0

As you can see, we've submitted a job, it has the job name "Level1" and one of
the nodes in our subinstance is now allocated.

Lets create yet another Flux subinstance via ``flux mini alloc`` but lets launch it
with two nodes instead of four.

.. code-block:: console

   corona171:~$ flux mini alloc -N2

   corona173:~$ flux resource list
        STATE NNODES   NCORES    NGPUS NODELIST
         free      2       96       16 corona[173-174]
    allocated      0        0        0
         down      0        0        0

   corona173:~$ flux getattr instance-level
   2

As you can see, we've successfully created another subinstance with two nodes
and we're now at level 2.  You'll notice that we're now on the node "corona173"
instead of "corona171".

Just like above, lets submit a job to this subinstance, but we'll name the job "Level2".

.. code-block:: console

   corona173:~$ flux mini submit --job-name=Level2 -N1 sleep inf

   corona173:~$ flux jobs
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
        ƒb63wFg3 achu     Level2      R      1      1   10.68s corona174

   corona173:~$ flux resource list
         STATE NNODES   NCORES    NGPUS NODELIST
          free      1       48        8 corona173
     allocated      1       48        8 corona174
          down      0        0        0

As you can see, another job has been submitted and has taken up a resource of one node.  You'll also notice
that the "Level1" sleep job is not listed.  The reason is because that job is not a part of this Flux instance,
it is in this subinstance's parent.

Lets take a look at this at a global level.  Lets go back to the login node and run ``flux jobs``.

.. code-block:: console

    corona-login-node:~$ flux jobs
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
     ƒgpD9HY9BsM achu     flux        R      4      4   3.997m corona[171,173-175]

We ony see one job, which is our subinstance.  Where is our other subinstance?  Where are our two sleep jobs?

.. note::

   Depending on your terminal settings, the subinstance may be colored blue in ``flux jobs``, indicating it is a subinstance.

We can see them by specifying the ``--recursive`` option to ``flux-jobs.

.. code-block:: console

    corona-login-node:~$ flux jobs --recursive
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
     ƒgpD9HY9BsM achu     flux        R      4      4    4.74m corona[171,173-175]

    ƒgpD9HY9BsM:
        ƒge9VDjD achu     flux        R      2      2   3.199m corona[173-174]
        ƒLU5z2zj achu     Level1      R      1      1   3.961m corona175

    ƒgpD9HY9BsM/ƒge9VDjD:
        ƒb63wFg3 achu     Level2      R      1      1   1.903m corona174

From this output we can see that our first subinstance has two jobs, our
"Level1" sleep job and a subinstance in it.  Our second subinstance has one job
in it, our "Level2" sleep job.

Another way to view this hierarchy of subinstances is via the ``flux-pstree`` command.

.. code-block:: console

    corona-login-node:~$ flux pstree
    .
    └── flux
        ├── flux
        │   └── Level2
        └── Level1

-------------------------------
Subinstance via Flux Mini Batch
-------------------------------

``flux mini alloc`` is great for when you need to drop into a shell to interact
with your subinstance.  This is often used by users to drop into a "main"
subinstance and to interact with that subinstance.

However, the majority of the time you wouldn't want this.  Most often, you want
to launch a subinstance, perhaps launch a number of jobs within those
subinstances, and just wait for them to complete.  The most common way to do
this is with ``flux mini batch``.

``flux mini batch`` takes a script instead of a command, so lets write two
scripts that will do the exact same thing as we did above with ``flux mini
alloc``.

.. code-block:: sh

    #!/bin/sh
    # filename: subinstance_level1.sh
    id1=`flux mini submit --job-name=Level1 -N1 sleep 60`
    id2=`flux mini batch -N2 ./subinstance_level2.sh`
    flux job status ${id1} ${id2}

In this first script we are doing exactly what we did in the first
example when we were our level 1 instance.  We first launch a sleep
job with the name ``Level1``, with only the minor difference that I
set the sleep time to 60 seconds instead of infinity.  We then launch
a two node subinstance via ``flux mini batch`` and the ``-N`` option.
This ``flux mini batch`` takes a second script as input.  We then call
``flux job status`` to wait for the job and subinstance to finish
before exiting the script.

.. code-block:: sh

    #!/bin/sh
    # filename: subinstance_level2.sh
    id=`flux mini submit --job-name=Level2 -N1 sleep 60`
    flux job status ${id}

In the second script (which we ran via ``flux mini batch`` in the first script),
we are doing what we did before in our second level subinstance.  We launch a
sleep job named ``Level2``.  We then similarly wait for it to finish with ``flux
job status``.

The only thing left to do is launch the initial 4 node subinstance.  We can do
it like below with ``flux mini batch`` and the ``-N`` option.

.. code-block:: console

    corona-login-node:~$ flux mini batch -N4 ./subinstance_level1.sh
    ƒgzLyJ6ZTuZ

You'll notice that ``flux mini batch`` outputs a jobid instead of dropping us into a shell.

If we run ``flux pstree`` you'll notice that we have an identical subinstance
layout as with the first example, only the name of the scripts are listed
instead of the name ``flux``.

.. code-block:: console

    corona-login-node:~$ flux pstree
    .
    └── subinstance_level1.sh
        ├── subinstance_level2.sh
        │   └── Level2
        └── Level1

And that's it! If you have any questions, please
`let us know <https://github.com/flux-framework/flux-docs/issues>`_.

For additional information about managing hierarchies of Flux instances,
see :ref:`Working with Flux Job Hierarchies<hierarchies>`

