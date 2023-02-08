.. _fast-job-submission-tutorial:

===================
Fast Job Submission
===================

One of the biggest value adds for Flux are for those who are dealing with many many jobs, minimally hundreds, but into millions of jobs.

This tutorial will try to go over some of the basics of how to submit a large number of jobs.

--------------------
Basic Job Submission
--------------------

Let's assume you need to submit a number of scripts to run.  The way this might traditionally be done via a script is like so:

.. code-block:: sh

    #!/bin/sh

    for myjob in `ls my_job_scripts/myjob*.sh`
    do
        flux submit ${myjob}
    done

    flux queue drain

In this example, I have a directory (``my_job_scripts``) with a number a job scripts prefixed with ``myjob``.  We iterate through all the job scripts in the directory one by one, submitting them via a job submission command (in this case ``flux submit``).  Then I wait for all the jobs to finish with ``flux queue drain``.

Let's run this really quick under a local flux instance.  In my example directory, I have 1000 scripts suffixed with a number (i.e. ``myjob1.sh`` through ``myjob1000.sh``).  Each script just runs ``sleep 0``.  I also added some simple timings to see how long job submissions take.

.. code-block:: sh

    #!/bin/sh
    # filename: job_submit_loop.sh

    start=`date +%s`
    for myjob in `ls my_job_scripts/myjob*.sh`
    do
        flux submit ${myjob}
    done
    end=`date +%s`
    runtime=$((end-start))
    echo "Job submissions took $runtime seconds"

    flux queue drain
    end=`date +%s`
    runtime=$((end-start))
    echo "Job submissions and runtime took $runtime seconds"

.. code-block:: console

    > ./job_submit_loop.sh
    <snip, many job ids printed out>
    Job submissions took 351 seconds
    Job submission and runtime took 352 seconds

As you can see, it took 351 seconds to submit all of these jobs.

This can be slow for several reasons:

* If you have a lot of job scripts, this is a slow `O(n)` process.  Each call to ``flux submit`` will involve another round of messages being sent/received to/from Flux.

* You are competing with other users that are also submitting jobs and doing other things with the Flux system instance.

---------------------------
Asynchronous Job Submission
---------------------------

Jobs can be asynchronously submitted via several mechanisms.  This will allow us to significantly reduce the slow iterative process of submitting jobs one by one.

The first mechanism is the ``--cc`` (carbon copy) option in ``flux submit``.  It will allow the user to replicate every id specified in an :ref:`IDSET<idset>`.  Along with the ``{cc}`` substitution string, we can submit all 1000 scripts on the command line like so:

.. code-block:: console

    > flux submit --cc="1-1000" "my_job_scripts/myjob{cc}.sh"

This substitution is convenient and largely replaces the loop from the above script.

The real benefit is what will go on behind the scenes.  Instead of iterating through job submissions one by one, internally job submissions will be sent asynchronously, so we no longer have call and wait after every ``flux job submit`` call.  This will allow job submissions to go a lot faster.  How much faster?

.. code-block:: console

    > time flux submit --cc="1-1000" "my_job_scripts/myjob{cc}.sh"
    <snip, many job ids printed out>
    real   0m3.281s
    user   0m1.426s
    sys    0m0.140s

We're looking at a wallclock speedup of about 99% here (351 seconds vs 3 seconds).  And just to show that the submission time was the bottleneck before and not runtime, let's use the ``--wait`` option with ``flux submit``.  This will inform ``flux submit`` to return after all the jobs have run to completion.

.. code-block:: console

    > time flux submit --wait --cc="1-1000" "my_job_scripts/myjob{cc}.sh"
    <snip, many job ids printed out>
    real       0m50.428s
    user       0m3.235s
    sys        0m0.384s

Now that the job submission is so fast, the bottleneck becomes the actual running of the jobs, not the job submission time.  The total submission and runtime of the jobs fell from 352 seconds to 50 seconds.

Another way to submit jobs asynchronously is with ``flux bulksubmit``.  The interface may be familiar to those who know the `GNU parallel command <https://www.gnu.org/software/parallel/>`_.  The following example is the bulksubmit equivalent to our original loop script.

.. code-block:: console

    > time flux bulksubmit my_job_scripts/myjob{}.sh ::: $(seq 1 1000)
    <snip, many job ids printed out>
    real   0m3.133s
    user   0m1.445s
    sys    0m0.145s

--------------------------
Subinstance Job Submission
--------------------------

To solve competition with other users, we can launch a :ref:`subinstance<subinstance>` of Flux.

What are we doing by launching a subinstance?  We're basically launching another Flux instance as a job.  And once we do that, we have our own Flux resource manager and scheduler that is independent of other users.

We can launch a subinstance of Flux via ``flux batch`` and run our job submission loop from earlier.

.. code-block:: console

    > flux batch -n24 ./job_submit_loop.sh

Because I'm writing this tutorial against my own Flux instance, and the node I'm on isn't that busy, this isn't really going to gain us much in terms of performance.

But we can think about how this can be done if we scale it up.  We could divide up our resources and launch multiple Flux instances and divide up the job submissions amongst them.

I'm going to go back to the first looping iteration example from before.  Using ``--cc`` or ``bulksubmit`` are so fast with 1000 jobs, that we wouldn't really see any performance difference using subinstances.

I'll also use a slightly altered loop script I call `job_submit_loop_range.sh`.  It will take two numbers on the command line and iterate only between those numbers.

.. code-block:: sh

    #!/bin/sh
    # filename: job_submit_loop_range.sh

    for i in `seq $1 $2`
    do
        flux submit my_job_scripts/myjob${i}.sh
    done

Let's launch two subinstances in the following script.

.. code-block:: sh

    #!/bin/sh
    # filename: subinstance_2.sh

    start=`date +%s`
    flux batch -n12 ./job_submit_loop_range.sh 1 500
    flux batch -n12 ./job_submit_loop_range.sh 501 1000
    flux queue drain
    end=`date +%s`
    runtime=$((end-start))
    echo "Job submissions and runtime took $runtime seconds"

My node happens to have 24 cores, so I divide those cores up evenly between these two subinstances (12 cores each), and each of them handling the submission of 500 jobs (1-500 in one, 501-1000 in the other).  Because it is difficult to test ONLY job submissions amongst multiple subinstances, I'm only outputting the combined submission and runtime length vs. just the submission time length.

.. code-block:: console

    > ./subinstance_2.sh
    fXE52ptMd
    fXEFWfou1
    Job submissions and runtime took 177 seconds

The result is about what we expected, it was about half the time from before (352 seconds vs 177 seconds).

What if we launched 4 subinstances instead of two?  Let's do the same experiment, dividing up the cores (6 for each subinstance) and jobs (250 for each subinstance) evenly.

.. code-block:: sh

    #!/bin/sh
    # filename: subinstance_4.sh

    start=`date +%s`
    flux batch -n6 ./job_submit_loop_range.sh 1 250
    flux batch -n6 ./job_submit_loop_range.sh 251 500
    flux batch -n6 ./job_submit_loop_range.sh 501 750
    flux batch -n6 ./job_submit_loop_range.sh 751 1000
    flux queue drain
    end=`date +%s`
    runtime=$((end-start))
    echo "Job submissions and runtime took $runtime seconds"

.. code-block:: console

    > ./subinstance_4.sh
    fYYku2CNj
    fYYvQXbD1
    fYZ6DpqRR
    fYZFonC6j
    Job submissions and runtime took 93 seconds

Not surprsingly, we've cut our job submission and runtime time down even more to 93 seconds.

Although I haven't gone into it within the example, one could also launch a subinstance, within a subinstance.

-------------------------
Combining Things Together
-------------------------

Let's try to put this all together and have subinstances use ``flux jobs submit`` with the ``--cc`` option.  We'll run the experiment with 10000 jobs.  Based on our original loop taking 352 seconds on 1000 jobs, we could estimate this would normally take 3520 seconds, or about 58 minutes.

.. code-block:: sh

    #!/bin/sh
    # filename: job_submit_async_range.sh

    flux submit --wait --cc="$1-$2" "my_job_scripts/myjob{cc}.sh"

.. code-block:: sh

    #!/bin/sh
    # filename: subinstance_4_async.sh

    start=`date +%s`
    flux batch -n6 ./job_submit_async_range.sh 1 2500
    flux batch -n6 ./job_submit_async_range.sh 2501 5000
    flux batch -n6 ./job_submit_async_range.sh 5001 7500
    flux batch -n6 ./job_submit_async_range.sh 7501 10000
    flux queue drain
    end=`date +%s`
    runtime=$((end-start))
    echo "Job submissions and runtime took $runtime seconds"

.. code-block:: console

    > ./subinstance_4_async.sh
    fRnvTBcsq
    fRo6q6bHq
    fRoG5n7Jf
    fRoQvjpoy
    Job submissions and runtime took 106 seconds

Given our original loop for 1000 jobs took 352 seconds, 106 seconds for 10000 jobs is pretty good improvement :-)

