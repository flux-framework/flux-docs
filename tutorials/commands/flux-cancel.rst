.. _flux-cancel:
.. _flux-pkill:

========================
How to Cancel a Flux Job
========================

Inevitably submitted jobs will have to be canceled for one reason or another.  This tutorial
will show you how.

----------------------------
How to Cancel a Job by Jobid
----------------------------

The basic way to cancel a job is through ``flux cancel``.  All you have to do is specify
the jobid on the command line.  Here is a simple example after submitting a job.

.. code-block:: console

    $ flux submit sleep 100
    ƒh35Dh5qRyq

    $ flux jobs ƒh35Dh5qRyq
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
     ƒh35Dh5qRyq achu     sleep       R      1      1   13.33s corona174

    $ flux cancel ƒh35Dh5qRyq

    <snip wait a little bit>

    $ flux jobs ƒh35Dh5qRyq
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
     ƒh35Dh5qRyq achu     sleep      CA      1      1   20.18s corona174

In the above example we submitted a simple job via ``flux submit`` that simply
runs ``sleep``.  Passing the resulting jobid to ``flux jobs`` shows that it is
running (state is ``R``).

We cancel the job simply by passing the jobid to ``flux cancel``.  After waiting
a little bit, we see that the job is now canceled in ``flux jobs`` (state is ``CA``).

While we only passed one jobid to ``flux cancel`` in this example, multiple jobids can be
passed on the commandline to cancel many jobs.

Note that in this particular example we happened to know the jobid of our job.  If you do
not know the the jobid of your job, you can always use ``flux jobs`` to see a list of all
your currently active jobs.

.. note::

    Optionally a message can be added to the cancellation through the ``-m`` option.  For example:

    .. code-block:: console

        $ flux cancel -m "I ran the wrong command" f3vnSzaaB

    This may be useful for later knowing why a job was canceled.  You can see the message using
    ``flux jobs`` and the ``endreason`` format.  For example:

    .. code-block:: console

        $ flux jobs --format=endreason f3vnSzaaB
               JOBID USER     NAME       ST   T_INACTIVE INACTIVE-REASON
           f3vnSzaaB achu     sleep      CA  May11 08:52 Canceled: I ran the wrong command

---------------------------
Canceling Many of Your Jobs
---------------------------

When you need to cancel many or all of your jobs, you can use either the ``--all`` option with ``flux cancel``
or the ``flux pkill`` command.  Let's run through several examples with the ``--all`` option first.

``flux cancel --all``  allows you to cancel jobs without specifying jobids.  By default it cancels all of your active
jobs, but several options allow you to target a subset of the jobs.

To start off, let's create 100 jobs that will sleep infinitely.  We will use the special ``--cc`` (carbon copy)
option to ``flux submit`` that will submit 100 duplicate copies of the ``sleep`` job.

.. code-block:: console

    $ flux submit --cc=1-100 sleep inf
    <snip - many job ids printed out>

    $ flux jobs
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
        ƒjTWS5m3 achu     sleep       S      1      -        -
        ƒjTWS5m4 achu     sleep       S      1      -        -
        ƒjTWS5m5 achu     sleep       S      1      -        -
        ƒjTWS5m6 achu     sleep       S      1      -        -
	<snip - there are many jobs waiting to be run>
        ƒjTWS5m2 achu     sleep       R      1      1   8.858s corona212
        ƒjTWS5m1 achu     sleep       R      1      1   8.860s corona212
        ƒjTUx6Um achu     sleep       R      1      1   8.870s corona212
        ƒjTUx6Uk achu     sleep       R      1      1   8.870s corona212
        ƒjTUx6Uj achu     sleep       R      1      1   8.870s corona212
        ƒjTUx6Ui achu     sleep       R      1      1   8.871s corona212
	<snip - there are many jobs running>

As you can see, we have a lot of jobs waiting to run (state ``S``) and a lot of running jobs (state ``R``).

Let's first ``flux cancel --all`` without any options.

.. code-block:: console

    $ flux cancel --all
    flux-cancel: Canceled 100 jobs (0 errors)

    $ flux jobs
               JOBID USER     NAME       ST NTASKS NNODES     TIME INFO

As you can see, all the jobs are now canceled.  ``flux jobs``
confirms there are no longer any of our jobs running or waiting to run.

There are several options to filter the jobs to cancel when using the ``--all`` option.  Perhaps the most commonly used
option is the ``-S`` or ``--states`` option.  The ``--states`` option specifies the state(s) of a job to cancel.  The most
common states to target are ``pending`` and ``running``.  Let's resubmit our 100 jobs and see the result
of trying to cancel ``pending`` vs ``running`` jobs.

.. code-block:: console

    $ flux submit --cc=1-100 sleep inf
    <snip - many job ids printed out>

    $ flux cancel --all --states=pending
    flux-cancel: Canceled 52 jobs (0 errors)

    $ flux cancel --all --states=running
    flux-cancel: Canceled 48 jobs (0 errors)

As you can see ``flux cancel --all --states=pending`` targeted the 52 pending jobs for cancellation and
``flux cancel --all --states=running`` targeted the current 48 running jobs for cancellation.

--------------------------
Cancelling with Flux Pkill
--------------------------

The final way to cancel a job is via ``flux pkill``.  There are a number of search and filtering options available in
``flux pkill`` which can be seen in the :core:man1:`flux-pkill` manpage.

However, there are two common ways ``flux pkill`` is used.  The first is to cancel a range of jobids.  The jobid range can be specified
via the format ``jobid1..jobidN``.

It is best shown with an example.

.. code-block:: console

    $ flux submit --cc=1-5 sleep inf
    ƒ3vEobuhH
    ƒ3vEobuhJ
    ƒ3vEobuhK
    ƒ3vEq5tyd
    ƒ3vEq5tye

    $ flux jobs
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
       ƒ3vEq5tye achu     sleep       R      1      1   14.23s corona212
       ƒ3vEq5tyd achu     sleep       R      1      1   14.23s corona212
       ƒ3vEobuhK achu     sleep       R      1      1   14.23s corona212
       ƒ3vEobuhJ achu     sleep       R      1      1   14.23s corona212
       ƒ3vEobuhH achu     sleep       R      1      1   14.23s corona212

Similar to before, we've submitted some sleep jobs.  We see all five of the sleep jobs are
running (state ``R``) in the ``flux jobs`` output.

We can inform ``flux pkill`` to cancel the set of 5 jobs by specifying the first and last jobid of this range.

.. code-block:: console

    $ flux pkill ƒ3vEobuhH..ƒ3vEq5tye
    flux-pkill: INFO: Canceled 5 jobs

    $ flux jobs
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO

As you can see ``flux pkill`` canceled the five jobs in the range.

The other common way to ``flux pkill`` is used is to cancel jobs with matching job names.  For example, you may
submit several different types of jobs and give them different types of names to describe their function.  ``flux pkill``
can be used to match on the job names and cancel only the ones that match.

Let's submit several jobs and give them specific names using the ``--job-name`` option.

.. code-block:: console

    $ flux submit --job-name=foo sleep inf
    ƒ6KjHNcxP

    $ flux submit --job-name=foobar sleep inf
    ƒ6Limcmju

    $ flux submit --job-name=boo sleep inf
    ƒ6NCaXCmV

    $ flux submit --job-name=baz sleep inf
    ƒ6PjZG6jq

    $ flux jobs
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
       ƒ6PjZG6jq achu     baz         R      1      1   38.06s corona212
       ƒ6NCaXCmV achu     boo         R      1      1   41.54s corona212
       ƒ6Limcmju achu     foobar      R      1      1    44.9s corona212
       ƒ6KjHNcxP achu     foo         R      1      1   47.15s corona212


We've submitted four jobs, giving them the job names "foo", "foobar", "boo", and "baz".

Let's cancel the job "boo" via ``flux pkill``

.. code-block:: console

    $ flux pkill boo
    flux-pkill: INFO: Canceled 1 job

    $ flux jobs
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
       ƒ6PjZG6jq achu     baz         R      1      1   2.856m corona212
       ƒ6Limcmju achu     foobar      R      1      1    2.97m corona212
       ƒ6KjHNcxP achu     foo         R      1      1   3.008m corona212

As you can see, ``flux pkill`` canceled just one job, the one assigned the name "boo".

``flux pkill`` will actually search for all jobs matching the supplied name, so what would happen if we asked ``flux pkill``
to cancel jobs with the matching name "foo".

.. code-block:: console

    $ flux pkill foo
    flux-pkill: INFO: Canceled 2 jobs

    $ flux jobs
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
       ƒ6PjZG6jq achu     baz         R      1      1   4.626m corona212

As you can see it didn't cancel 1 job, it canceled 2 jobs, the job "foo" and the job "foobar".

And that's it! If you have any questions, please
`let us know <https://github.com/flux-framework/flux-docs/issues>`_.
