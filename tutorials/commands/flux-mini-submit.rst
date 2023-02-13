.. _flux-mini-submit:
.. _flux-mini-run:

==========================
How to Submit Jobs in Flux
==========================

Do you want to submit a job to Flux? Here's a short tutorial on how to do so!

----------------------------
Submit Jobs Using Flux's CLI
----------------------------

From within a Flux instance, you can submit your job on the command line with
optional arguments, resource options, per task options, and per resource
options:

.. code-block:: console

    $ flux mini submit --nodes=2 --ntasks=4 --cores-per-task=2 ./my_compute_script.py 120
    ƒM5k8m7m
    $ flux mini submit --nodes=1 --ntasks=1 --cores-per-task=2 ./my_other_script.py 120
    ƒSUEFPDH

In the above example, we are submitting two jobs with two different sets of
options to describe how we want our jobs to run. In the first submission, we
are asking for our job to start 4 tasks across 2 nodes, with 2 cores allocated
for each task. In the second submission, we are asking for our job to start 1
task on just one node with 2 cores allocated for the task.

There are many different options to customize your job submission. For further
details, please see :core:man1:`flux-mini`.

A :ref:`jobid<fluid>` (e.g., ``ƒSUEFPDH``) is returned for every job submitted. You can view
the status of your running jobs with ``flux jobs``:

.. code-block:: console

    $ flux jobs
       JOBID  USER     NAME       ST NTASKS NNODES     TIME INFO
    ƒSUEFPDH  fluxuser my_other_s  R      1      1   1.842s
    ƒM5k8m7m  fluxuser my_compute  R      4      2   3.255s

-----------------------
Interactively Run a Job
-----------------------

If you wish to run a job interactively, e.g. see standard output as it runs, you can
use the ``flux mini run`` command.  It is identical to ``flux mini submit`` except it
will handle stdio and it will block until the job has finished.  For example:

.. code-block:: console

    $ flux mini run bash -c "echo start; sleep 5; echo done"
    start
    done

In the above example, we run a small bash script that will output "start", sleep for 5 seconds,
and then echo "done".  Unlike ``flux mini submit``, you'll notice it does not output a jobid.
If we check for the status of this job with ``flux jobs`` after it has run, you will not find the
job listed because it is no longer running.  Instead run ``flux jobs -a`` which will list all jobs,
including completed jobs.

.. code-block:: console

    $ flux jobs -a
       JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
    f2HnvmZy achu     bash       CD      1      1   5.119s catalyst159


You will see that job is in the "CD" state or "Completed" state.

And that's it! If you have any questions, please
`let us know <https://github.com/flux-framework/flux-docs/issues>`_.

-------------------------------------
More Examples of Submitting Flux Jobs
-------------------------------------

.. code-block:: console

    $ flux mini submit --nodes=2 --queue=foo --name=my_special_job ./my_job.py

This submits a job to the `foo` queue across two nodes, and sets a custom name
to the job.

.. code-block:: console

    $ flux mini submit --dry-run ./my_cool_job.py

If you don't want your job to actually run, but you are interested in looking
at the :ref:`jobspec<jobspec>` for your job, include the ``--dry-run`` option
when you submit your job.

.. code-block:: console

    $ flux mini submit --output=job-{{id}}.out ./my_super_cool_job.py
    ƒ3D78hc3q

If you want to bypass the :ref:`KVS<kvs>` and specify a filename for STDOUT redirection,
include the ``--output`` option when submitting your job. You can format the
name of your output file using the jobID via mustache template. In the example
above, any output to STDOUT will be redirected to a file named
``job-ƒ3D78hc3q.out``.
