.. _flux-jobs:

================================================================
How to List Flux jobs, Filter Them, and Output Extra Information
================================================================

Inevitably you will want to list your current jobs.  Many users will know that
to list jobs you use the ``flux jobs`` command.  However, there are many
advanced job listing and filtering options available.  This tutorial will go
through some of the most popular ones so you know how to list the jobs you are
looking for more easily and to get the information you are looking for.

--------------------
Job Submission Setup
--------------------

Before beginning the tutorial, let's run some jobs to set things up.  I have a small Flux instance of
one node with only four processors, which we can see with ``flux resource list``.

.. code-block:: console

    $ flux resource list
         STATE NNODES   NCORES NODELIST
          free      1        4 catalyst160
     allocated      0        0 
          down      0        0 

Let's submit some jobs to the Flux instance.

.. code-block:: console

    $ flux submit --cc=0-1 --wait /bin/true
    f2RYAVwjM
    f2RYByw1h
    $ flux submit --cc=0-1 --wait /bin/false
    f2SLdmS4F
    f2SLfFRLb
    $ flux submit --cc=0-7 sleep inf
    f2TR77Ao1
    f2TR8bA5M
    f2TR8bA5N
    f2TRBZ8e3
    f2TRD37vP
    f2TREX7Cj
    f2TRG16V5
    f2TRHV5mR
    $ flux job cancel f2TRHV5mR

In the above we have submitted a number of jobs.  First we submit two jobs that
run ``/bin/true``, then we run two jobs that run ``/bin/false``.  If you are
unfamiliar with the ``--cc`` (i.e. carbon copy) option, it will simply create
duplicates of the job you just submitted.  We also specify the ``--wait`` command
to wait for those jobs to finish before moving on.

Next we submit 8 ``sleep`` commands of infinite length.  Then for fun, we cancel
one of those jobs via ``flux job cancel``.

-----------------
Basic Job Listing
-----------------

Let's run ``flux jobs`` and see what we get.

.. code-block:: console

    $ flux jobs
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
       f2TRD37vP achu     sleep       S      1      -        - 
       f2TREX7Cj achu     sleep       S      1      -        - 
       f2TRG16V5 achu     sleep       S      1      -        - 
       f2TRBZ8e3 achu     sleep       R      1      1   1.765m catalyst160
       f2TR8bA5N achu     sleep       R      1      1   1.765m catalyst160
       f2TR8bA5M achu     sleep       R      1      1   1.765m catalyst160
       f2TR77Ao1 achu     sleep       R      1      1   1.765m catalyst160

The default output lists the jobs that are currently running or pending.  You'll notice this via
the job state listed under ``ST``.  The ``S`` indicates the job state ``SCHED`` and the ``R`` indicates
the job state ``RUN``.  As mentioned above, this instance only has 4 CPUs, therefore only 4 sleep jobs are running.

You'll notice that there are only 7 sleep jobs listed and not 8.  As you recall above, we canceled one sleep job, therefore there should be only 7 jobs listed here.  In addition, the ``/bin/true`` and ``/bin/false`` jobs are not listed.

By default ``flux jobs`` only listed "pending" and "running" jobs.  Inactive jobs are not listed.  In order to list
inactive jobs we can specify a different filter via the ``--filter`` option.  For example we could tell ``flux jobs``
to only list the inactive jobs via ``flux jobs --filter=inactive``.

.. code-block:: console

    $ flux jobs --filter=inactive
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
       f2TRHV5mR achu     sleep      CA      1      -        - 
       f2SLdmS4F achu     false       F      1      1   0.057s catalyst160
       f2SLfFRLb achu     false       F      1      1   0.056s catalyst160
       f2RYByw1h achu     true       CD      1      1   0.560s catalyst160
       f2RYAVwjM achu     true       CD      1      1   0.453s catalyst160

In the above we see the five INACTIVE jobs we expect.  There are the two
``/bin/true`` jobs, two ``/bin/false`` jobs, and our canceled job.  As you can
see via the job state, they are lited with ``CD`` (completed), ``F`` (failed),
and ``CA`` (canceled) respectively.

.. note::

   In this tutorial there is no color highlighting of ``flux jobs`` output, but
   depending on your terminal there may be color highlighting different job
   states and results.

While you can use the ``--filter`` option to list inactive jobs, most users prefer to use the
``-a`` option.  The ``-a`` is shorthand for ``--filter=pending,running,inactive``.  In other words,
it lists all of your jobs.  Which we can see below.

.. code-block:: console

    $ flux jobs -a
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
       f2TRD37vP achu     sleep       S      1      -        - 
       f2TREX7Cj achu     sleep       S      1      -        - 
       f2TRG16V5 achu     sleep       S      1      -        - 
       f2TRBZ8e3 achu     sleep       R      1      1   39.93m catalyst160
       f2TR8bA5N achu     sleep       R      1      1   39.93m catalyst160
       f2TR8bA5M achu     sleep       R      1      1   39.93m catalyst160
       f2TR77Ao1 achu     sleep       R      1      1   39.93m catalyst160
       f2TRHV5mR achu     sleep      CA      1      -        - 
       f2SLdmS4F achu     false       F      1      1   0.057s catalyst160
       f2SLfFRLb achu     false       F      1      1   0.056s catalyst160
       f2RYByw1h achu     true       CD      1      1   0.560s catalyst160
       f2RYAVwjM achu     true       CD      1      1   0.453s catalyst160

------------------
Advanced Filtering
------------------

In this particular example, it's not too annoying to run ``flux jobs -a`` because we only have
12 jobs total.  However, over time, you may have hundreds, if not thousands, of jobs to list.  It can
become difficult to filter and find your jobs.

There are many ways to filter the job listing to limit the output to the jobs you are interested in.
Here are some of the most common options.

The simplest way to limit job output is to specify the jobid of the jobs you wish to list.  This is typically
done because you want to monitor the status of some finite number of your jobs.

.. code-block:: console

    $ flux jobs f2RYAVwjM f2RYByw1h f2SLfFRLb f2SLdmS4F
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
       f2RYAVwjM achu     true       CD      1      1   0.453s catalyst160
       f2RYByw1h achu     true       CD      1      1   0.560s catalyst160
       f2SLfFRLb achu     false       F      1      1   0.056s catalyst160
       f2SLdmS4F achu     false       F      1      1   0.057s catalyst160

Here we list the jobids of the ``/bin/true`` and ``/bin/false`` jobs to get the results of just those jobids.

By default ``flux jobs`` will limit output to 1000 jobs.  If the number of jobs is getting too large (or you want to show even more jobs) you can adjust this via the ``--count`` option.

.. code-block:: console

    $ flux jobs --count=4
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
       f2TRD37vP achu     sleep       S      1      -        - 
       f2TREX7Cj achu     sleep       S      1      -        - 
       f2TRG16V5 achu     sleep       S      1      -        - 
       f2TRBZ8e3 achu     sleep       R      1      1   47.88m catalyst160

    $ flux jobs --count=4 --filter=inactive
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
       f2TRHV5mR achu     sleep      CA      1      -        - 
       f2SLdmS4F achu     false       F      1      1   0.057s catalyst160
       f2SLfFRLb achu     false       F      1      1   0.056s catalyst160
       f2RYByw1h achu     true       CD      1      1   0.560s catalyst160

Here we pass ``--count=4`` to limit the of jobs output from ``flux jobs`` default output and when we
specify that we should only list inactive jobs.

We already saw above that ``--filter`` can be used to filter jobs on "pending", "running", or "inactive"
state.  But we can also filter on the result of a job.  In the following example, we show that you can
list "completed", "failed", or "canceled" jobs respectively.

.. code-block:: console

    $ flux jobs --filter=completed
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
       f2RYByw1h achu     true       CD      1      1   0.560s catalyst160
       f2RYAVwjM achu     true       CD      1      1   0.453s catalyst160

    $ flux jobs --filter=failed
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
       f2SLdmS4F achu     false       F      1      1   0.057s catalyst160
       f2SLfFRLb achu     false       F      1      1   0.056s catalyst160

    $ flux jobs --filter=canceled
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
       f2TRHV5mR achu     sleep      CA      1      -        - 

Jobs can also be filtered by their job name via the ``--name`` option.

.. code-block:: console

    $ flux jobs --name=sleep
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
       f2TRD37vP achu     sleep       S      1      -        - 
       f2TREX7Cj achu     sleep       S      1      -        - 
       f2TRG16V5 achu     sleep       S      1      -        - 
       f2TRBZ8e3 achu     sleep       R      1      1   50.04m catalyst160
       f2TR8bA5N achu     sleep       R      1      1   50.04m catalyst160
       f2TR8bA5M achu     sleep       R      1      1   50.04m catalyst160
       f2TR77Ao1 achu     sleep       R      1      1   50.04m catalyst160

Remember that the ``--filter`` option only lists "pending" and "running" jobs by default, so you
may get unexpected results if the ``--name`` option is used without an appropriate setting to ``--filter``.

.. code-block:: console

    $ flux jobs --name=true
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO

    $ flux jobs --name=true -a
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
       f2RYByw1h achu     true       CD      1      1   0.560s catalyst160
       f2RYAVwjM achu     true       CD      1      1   0.453s catalyst160

As you can see in the above, ``flux jobs --name=true` does not output anything.  That's because no "active"
jobs have the job name ``true``.  However, when specifying ``--name=true`` along with ``-a`` we see
our expected jobs that have already completed.

---------------
Advanced Output
---------------

While the default output of ``flux jobs`` is generally useful, it may not have all the information you wish.

Additional information can be output from ``flux jobs`` via the ``--format`` option, which will inform ``flux jobs`` to adjust the output format to what you wish to use.  Here's a simple example.  Let's get all of the exit codes for all of the jobs that have so far completed.  We'll get the completed jobs via ``--filter=inactive`` like before.  We'll adjust the output to simply be the format ``{id} {returncode}``.  The ``{id}`` field outputs the jobid and ``{returncode}`` outputs the exit code of the job.

.. code-block:: console

    $ flux jobs --filter=inactive --format="{id} {returncode}"
    JOBID RC
    f2TRHV5mR -128
    f2SLdmS4F 1
    f2SLfFRLb 1
    f2RYByw1h 0
    f2RYAVwjM 0

There are many additional fields that are available for output in ``flux-jobs``.  This tutorial will not go through them but you can find information on them via the :core:man1:`flux-jobs` manpage as well as ways to format the output in pretty ways.

For most users, instead of formatting your own output, you may wish to use one of the additional "common" formats available in ``flux-jobs``.  They can be listed with ``flux jobs --format=help``.

.. code-block:: console

    $ flux jobs --format=help

    Configured flux-jobs output formats:

      default      Default flux-jobs format string
      cute         Cute flux-jobs format string (default with emojis)
      long         Extended flux-jobs format string
      deps         Show job urgency, priority, and dependencies

For example, lets take a look at the ``long`` output.

.. code-block:: console

    $ flux jobs --format=long
           JOBID USER     NAME          STATUS NTASKS NNODES     T_SUBMIT  T_REMAINING     TIME INFO
       f2TRD37vP achu     sleep          SCHED      1      -  Mar29 17:28            -        - 
       f2TREX7Cj achu     sleep          SCHED      1      -  Mar29 17:28            -        - 
       f2TRG16V5 achu     sleep          SCHED      1      -  Mar29 17:28            -        - 
       f2TRBZ8e3 achu     sleep            RUN      1      1  Mar29 17:28            -   53.01m catalyst160
       f2TR8bA5N achu     sleep            RUN      1      1  Mar29 17:28            -   53.01m catalyst160
       f2TR8bA5M achu     sleep            RUN      1      1  Mar29 17:28            -   53.01m catalyst160
       f2TR77Ao1 achu     sleep            RUN      1      1  Mar29 17:28            -   53.01m catalyst160

Compared to the default output, we have ``STATUS`` being output with full names instead of abbreviations, we have the time
that the job was submitted via ``T_SUBMIT`` and the time remaining for the job in ``T_REMAINING`` (in this particular example, there is no time limit, thus no time remaining listed).

.. note::

    You can set the default output of ``flux jobs`` through the
    environment variable FLUX_JOBS_FORMAT_DEFAULT.  For example, by
    setting FLUX_JOBS_FORMAT_DEFAULT=long, the long output will be
    output as the default output.

.. note::

    Within a script, it is very common to use the following pattern to get information about a specific job.

    .. code-block:: sh

        nnodes=$(flux jobs -no "{nnodes}" $FLUX_JOB_ID)

In order to get the number of nodes for the job we are running, we set the output format to exactly ``{nnodes}`` and nothing else.  The ``-n`` option ensures that the header from ``flux jobs`` will not be output.  So the only thing output from this call to ``flux jobs`` is just the number of nodes for the specified jobid, which we then store in the ``nnodes`` variable.

---------------------
Recursive Job Listing
---------------------

.. note::

   This section is independent on the previous one.  To continue on with this example from the previous one,
   you may wish to cancel your jobs from before via ``flux cancel --all``.

By default, ``flux jobs`` will not list jobs that are running under subinstances within Flux.  Lets illustrate
this with an example.  Lets submit the following script to ``flux batch``.

.. code-block:: sh
    #!/bin/sh
    # filename: batchjob.sh

    flux submit sleep inf
    flux submit sleep inf
    flux queue drain

All we're doing is running two ``sleep`` jobs for infinity, and then calling ``flux queue drain`` to wait for those
jobs to complete.  (See :ref:`Waiting for jobs<waiting-for-jobs>` tutorial for info on using ``flux queue drain`` to wait for jobs to complete.)

Lets run this via ``flux batch``

.. code-block:: console

    $ flux batch -N1 ./batchjob.sh
    fUdmwwisR
    $ flux jobs
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
       fUdmwwisR achu     ./batchjo+  R      1      1   14.12s catalyst160

After submitting the batch job, you'll notice that ``flux jobs`` only lists the jobid of the batch job.  It does not list
the jobids of the sleep jobs running within that instance.

In order to see those additional jobs, you'll have to specify the ``--recursive`` option.

.. code-block:: console

    $ flux jobs --recursive
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
       fUdmwwisR achu     ./batchjo+  R      1      1   42.99s catalyst160

    fUdmwwisR:
        f3sv29Cj achu     sleep       R      1      1   30.23s catalyst160
        f3Xfqx1d achu     sleep       R      1      1   31.02s catalyst160






