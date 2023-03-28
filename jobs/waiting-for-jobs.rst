.. _waiting-for-jobs-to-finish:

==========================
Waiting For Jobs To Finish
==========================

There are several ways to wait for submitted jobs to complete, each with a unique set of pros and cons associated with them.  This covers the following techniques.

- ``--wait``
- ``flux job status``
- ``flux job wait``
- ``flux queue drain``

-----------------
The --wait option
-----------------

The most basic way to wait for a job to complete on a submitted job is the ``--wait`` option on ``flux job submit``.  Simply put, if the ``--wait`` option is passed to ``flux job submit``, the command will not return until the job has completed.

.. code-block:: console

    $ flux submit --wait -n1 bash -c "sleep 30; /bin/false"
    ƒEMds3VemM
    <wait for command to finish>
    $ echo $?
    1

The above command submits a job that simply sleeps for 30 seconds on one processor (``-n1``) and then runs ``/bin/false``.  The :ref:`jobid <fluid>` is immediately output, but the command won't return until the 30 second job has completed.

After the command has finished we print the exit code from ``flux submit``, which is ``1``, because we ran ``/bin/false``.

---------------
Flux Job Status
---------------

In most cases, you do not want to sit and wait for the current job submission to complete.  You would like to do other things, such as submit more jobs, and then wait for specific jobs to complete.

The ``flux job status`` command is the most basic way to wait for a specific job, based on jobid, to complete.  After submitting all the jobs you want, pass ``flux job status`` one or more jobids to wait on.  ``flux job status`` will return after all of the jobs have completed and exit with largest exit code from the jobids specified.  If the job(s) have already completed, ``flux job status`` returns immediately.  It can be run as many times as the user would like against the same jobid(s).

Here are several examples.  In this first one, we submit a simple job that sleeps for 30 seconds then runs ``/bin/true``.  Afterwards, we pass the jobid to ``flux job status`` and wait for it to return when the job has finished.  After it has completed we can see that the exit code from ``flux job status`` is ``0``, as we expect from ``/bin/true``.

.. code-block:: console

    $ flux submit -n1 bash -c "sleep 30; /bin/true"
    ƒLUebmCK
    $ flux job status ƒLUebmCK
    <we wait a little bit waiting for the job to finish>
    $ echo $?
    0

If we run the above job with ``/bin/false`` instead of ``/bin/true``.

.. code-block:: console

    $ flux submit -n1 bash -c "sleep 30; /bin/false"
    ƒeGz9fYs
    $ flux job status ƒeGz9fYs
    <we wait a little bit waiting for the job to finish>
    $ echo $?
    1

The result is identical to the first example except the exit code from ``flux job status`` is ``1``, which is what we expect from running ``/bin/flase``.

Finally, let's pass both jobids from above to ``flux job status``.

.. code-block:: console

    $ flux job status ƒLUebmCK ƒeGz9fYs
    $ echo $?
    1

You'll notice two things about this example.  First, the command returns immediately.  This is because the two jobs have already completed.  Second, the exit code is ``1``, which is the largest exit code of the two jobs passed to ``flux job status`` (one ran ``/bin/true`` and the other ran ``/bin/false``).

-------------
Flux Job Wait
-------------

``flux job wait`` implements semantics similar to the ``wait`` POSIX shell command.  So similarly to how ``wait`` does not require you to know a process ID to wait on, ``flux job wait`` does not require jobids for it to wait for your jobs.  Similarly, unlike ``flux job status``, it can be can only be called once per waitable job since the wait status is "reaped".

The primary advantages of ``flux job wait`` are that it is far more efficient than ``flux job status`` when waiting for many jobs (i.e. thousands).   In addition, it is extremely useful for waiting for single jobs as they complete, similarly to the ``wait`` shell command.

Let's illustrate these differences and advantages with some examples.

The most notable difference for ``flux job wait`` compared to ``flux job status`` is that jobs must be passed the ``waitable`` flag.  Any job that is not passed the ``waitable`` flag will not work with ``flux job wait``.  In addition, the ``waitable`` flag can only be used in user Flux instances (i.e. non-system instances).  User Flux instances are usually started via ``flux alloc`` or ``flux batch``.

Here's a simple example that's very similar to the example from before, where we run sleep for 30 seconds then run ``/bin/true``.

.. code-block:: console

    $ flux submit --flags waitable -n1 bash -c "sleep 30; /bin/true"
    ƒ4btMovw
    $ flux job wait ƒ4btMovw
    <we wait a little bit waiting for the job to finish>

Note that when submitting the job, we submitted it with the ``waitable`` flag via ``--flags waitable``.

This doesn't really show us anything special, it seems to be the same as ``flux job status``.  But unlike ``flux job status``, we cannot wait on the job a second time.

.. code-block:: console

    $ flux job wait ƒ4btMovw
    flux-job: invalid job id, or job may be inactive and not waitable

As you can see, by passing the jobid to ``flux job wait`` a second time, we get an error.

In addition, unlike ``flux job status``, ``flux job wait`` does not return the exit code of the job being waited on.  It returns 0 for a successfull job and 1 for an job that exited with an error.  As we can see in the following example.

.. code-block:: console

    $ flux submit --flags waitable bash -c "exit 0"
    f23oYLdZ9
    $ flux job wait f23oYLdZ9
    $ echo $?
    0
    $ flux submit --flags waitable bash -c "exit 3"
    f26USZbJo
    $ flux job wait f26USZbJo
    flux-job: task(s) exited with exit code 3
    $ echo $?
    1

The reason for this will discussed below.

The most powerful aspect of ``flux job wait`` is that you can call it without and jobids.  When no jobids are specified, it will wait for the first job that completes amongst all of the jobs you have submitted via the ``waitable`` flag.

.. code-block:: console

    $ flux submit --flags waitable -n1 bash -c "sleep 60; /bin/true"
    ƒ2WxyXSUF
    $ flux submit --flags waitable -n1 bash -c "sleep 45; /bin/true"
    ƒ2XRcLY7Z
    $ flux submit --flags waitable -n1 bash -c "sleep 30; /bin/true"
    ƒ2Zjt9VSw
    $ flux job wait
    ƒ2Zjt9VSw
    $ flux job wait
    ƒ2XRcLY7Z
    $ flux job wait
    ƒ2WxyXSUF
    $ flux job wait
    flux-job: there are no more waitable jobs

In this above example, we submit three jobs, sleeping for 60, 45, and 30 seconds respectively before running ``/bin/true``.  We then run ``flux job wait`` without any inputs.  You'll notice the jobids for the ``sleep 30`` job, then ``sleep 45`` job, then ``sleep 60`` job are returned in that order.  Finally, without any jobs left running with the ``waitable`` flag, ``flux job wait`` indicates there are no more waitable jobs.

Using ``flux job wait`` in this way can be useful to post-process jobs as they complete and you don't necessarily care about the order in which jobs complete.  For example, a loop similar to the one below could be used to wait for each job to complete, and post-process them in the order they complete.

.. code-block:: sh

    # Submti jobs with the waitable flag however you want
    while jobid=`flux job wait 2> /dev/null`; ec=$?; test $ec -ne 2
    do
        echo "$jobid finished"
        if [ $ec -eq 0 ]
        then
            echo "job successful"
            # do some post processing on successful jobs
        else
            echo "job failed"
            # do some post processing on failed jobs
        fi
    done
    echo "no more jobs to wait on"

In the above script we simply call ``flux job wait`` and get the jobid of every job that has completed.  We save and check the exit code to determine if the job is successful or not, so we know how to proceed with post processing.  We check for the exit code of 2 to indicate that no more jobs are waitable.  This is why all general job failures have an exit code of 1, so we can reserve 2 for this specific use case.

.. note::

   If you need to get the "real" exit code of the job after ``flux job wait`` you can parse the output from the failure message,
   use ``flux jobs``, or even use ``flux job status``.

Another option is that all jobs can be waited on via the ``--all`` option to ``flux job wait``.  Let's try that in the below example.

.. code-block:: console

    $ flux submit --flags waitable -n1 bash -c "sleep 60; /bin/true"
    ƒ4YNPpFmAf
    $ flux submit --flags waitable -n1 bash -c "sleep 45; /bin/true"
    ƒ4YPufmCjq
    $ flux submit --flags waitable -n1 bash -c "sleep 30; /bin/false"
    ƒ4YSVQWfZq
    $ flux job wait --all --verbose
    ƒ4YSVQWfZq: task(s) exited with exit code 1
    ƒ4YPufmCjq: job completed successfully
    ƒ4YNPpFmAf: job completed successfully

This example is similar to the above, except one of the jobs runs ``/bin/false`` instead of ``/bin/true``.  When ``flux job wait --all`` is executed, you'll notice a message output indicating that one job has failed (the one that ran ``/bin/false``).  The additional ``--verbose`` option is used here to see that the other jobs completed successfully.

As summary conclusion, here are a list of the pros and cons of using ``flux job status`` vs ``flux job wait``.

Pros:

- ``flux job wait`` more efficient, especially with thousands of jobs or the ``--all`` option
- Jobids do not need to be specified to ``flux job wait``

Cons:

- Jobs must be submitted with the ``waitable`` flag, which can only be used in user instances.

----------------
Flux Queue Drain
----------------

The final technique for waiting for jobs is a bit of a special case.

The command ``flux queue drain`` is commonly used by system administrators to wait for a system to become empty of jobs before performing system maintenance.  However, users may use it as well to indicate that all their jobs have completed.  The nuance is that all jobs in the queue must be done, including other user's jobs.  Therefore, is commonly used in user instances of Flux and not system instances.

Let's run a simple example on the command line.

.. code-block:: console

    $ flux jobs -A
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
    $ flux submit -n1 bash -c "sleep 30; /bin/true"
    ƒCSeWdUNb1
    $ flux submit -n1 bash -c "sleep 30; /bin/true"
    ƒCSesPJKR1
    $ flux queue drain

First, this example runs ``flux jobs -A``, which shows the jobs of all users on the system.  There are none, so we don't see any output other than the output header.

Next we submit several sleep jobs and wait for those jobs to complete by running ``flux queue drain``.   It's not so different than our use of ``flux job wait --all`` above, except we don't need the ``waitable`` flag to be set.  Also, the exit code from ``flux queue drain`` will not reflect the exit status of the jobs.

Typically, user instances have only a single job queue, since it belongs only to the user.  So it is common to create batch submission scripts like the following for ``flux batch``.

.. code-block:: sh

   flux submit -n1 job1.sh
   flux submit -n1 job2.sh
   flux submit -n1 job3.sh
   ...
   flux submit -n1 jobN.sh
   flux queue drain

In this example script, we are submitting a number of jobs, numbered ``job1.sh`` to ``jobN.sh``.  We would like the script to complete after all of the jobs have completed, so we simply add ``flux queue drain`` at the very end.

One might wonder why use this technique vs. ``flux job wait --all``.  There are several potential reasons.

- It is the most efficient way to wait for "all" your jobs to finish, since it does not involve any "processing" of any sort within Flux.  It simply waits for the queue to be empty and that's it.

- ``flux job wait`` only works for a single user.  In special circumstances, you may wish for multiple user's jobs to complete.  In those cases it would be beneficial to use ``flux queue drain``.

As summary conclusion, here are a list of the pros and cons of using ``flux queue drain``.

Pros:

- The most efficient way to wait for "all" your jobs to finish
- No need for the ``waitable`` flag

Cons:

- Cannot know jobs that finished as they complete
- Cannot get exit status of completed jobs
