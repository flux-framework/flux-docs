.. _flux-sched-container:

====================================
Quick Start with Flux in a Container
====================================

Do you want to submit a job to Flux? Here's a short tutorial on how to do so via a container!
The reason this works is because a Flux instance can be run anywhere...

    | You can run it on a cluster... 🥜️
    | You can run it alongside Lustre! 📁️
    | You can run it on a share... 🤗️
    | You can run it anywhere! 🏔️
    | You can run it in a container... 📦️
    | Using Flux? Total no-brainer! 🧠️

Flux has a regularly updated Docker image on `Docker Hub <https://hub.docker.com/u/fluxrm>`_. 
You will need to `install docker <https://docs.docker.com/engine/install/>`_ first.

----------------------
Starting the Container
----------------------

Run the container as follows:

.. code-block:: bash

  # This says "run an interactive terminal"
  $ docker run -it fluxrm/flux-sched:latest

There is a bit of a trick going on with the entrypoint so that when you run the container as shown above,
you will shell into a Flux instance of size 1. 


.. raw:: html
    :file: include/entrypoint-details.html

.. code-block:: shell

  # What is the size of the current Flux instance (i.e. number of flux-broker processes)
  $ flux getattr size
  1

  # What resources do we have, and what are their states?
  $ flux resource list
       STATE NNODES   NCORES    NGPUS NODELIST
        free      1        4        0 f9004106893d
   allocated      0        0        0 
        down      0        0        0 


In the above, because we are running in a single container, we only see one node with
four cores. Note that you could also imagine an example with docker compose (and we will
be adding this example shortly). Let's look at more Flux interactions, first to see Flux 
environment variables:

.. code-block:: shell

  # Where are different Flux things located (the environment)
  $ flux env

------------
Running Jobs
------------

``flux submit`` submits a job which will be scheduled and run in the background. 
It prints the jobid to standard output upon successful submission. To run a job interactively,
use ``flux run`` which submits and then attaches to the job, displays job output in real time,
and does not exit until the job finishes.

.. code-block:: shell

    $ flux submit hostname
    ƒM5k8m7m
    $ flux run hostname
    f9004106893d

You can inspect ``--help`` for each of the commands above to see it's possible
to customize the number of nodes, tasks, cores, and other variables.
There are many different options to customize your job submission. For further
details, please see :core:man1:`flux-submit` or run ``flux help submit``.

The identifier shown above is a :ref:`jobid<fluid>` (e.g., ``ƒM5k8m7m``). This kind of identifer
(or similar) is returned for every job submitted, and will be how you interact with your job moving forward. 
Let's throw in a few more sleep jobs, and immediately ask to see them with ``flux jobs``:

.. code-block:: shell

    $ flux submit sleep 360
    $ flux submit sleep 360


.. code-block:: shell

    $ flux jobs
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
        ƒq3d755R fluxuser sleep       R      1      1   2.811s 848fc387afd7
        ƒpcByPgK fluxuser sleep       R      1      1   3.805s 848fc387afd7


But wait, what happened to our first two jobs? ``flux jobs`` only shows "active" jobs by default,
add an ``-a`` for "all" to see all the jobs.

.. code-block:: shell

    $ flux jobs -a
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
        ƒq3d755R fluxuser sleep       R      1      1   39.98s 848fc387afd7
        ƒpcByPgK fluxuser sleep       R      1      1   40.97s 848fc387afd7
        ƒDi2hxdm fluxuser hostname   CD      1      1   0.019s 848fc387afd7
        ƒBmTaVZ9 fluxuser hostname   CD      1      1   0.025s 848fc387afd7

.. note::

   See if you can figure out how to list jobs by a particular status, e.g., ``R`` in the output 
   above means "running." Try ``flux jobs --help`` or ``flux help jobs``.



Did you figure it out? It would be ``flux jobs --filter=RUNNING``. What if you were running a long 
process, and you wanted to check on output? Let's do that. Here is script to loop, print, and sleep.

.. code-block:: bash

    #!/bin/bash
    # Save this as loop.sh
    for i in {0..10}; do
        echo "Hello I am loop iteration $i."
        sleep ${i}
    done

Now make the script executable, and submit the job with flux.

.. code-block:: shell

    $ chmod +x ./loop.sh
    $ flux submit ./loop.sh


To see output (and wait until completion) use ``flux job attach``:


.. code-block:: shell

    $ flux job attach ƒ4evXWb9Z
    Hello I am loop iteration 0.
    Hello I am loop iteration 1.
    Hello I am loop iteration 2.
    Hello I am loop iteration 3.
    Hello I am loop iteration 4.
    Hello I am loop iteration 5.

See ``flux help job`` or :core:man1:`flux-job` for more information on ``flux job attach``.

------------
Viewing Jobs
------------

Aside from listing jobs with ``flux jobs`` there are other ways to get metadata about jobs.
For your running jobs, you can use ``flux pstree`` to see exactly that - a tree of jobs.
Let's say we run another sleep job:


.. code-block:: shell

    $ flux submit sleep 350
    ƒ744GwLs

The tree will show us that one sleep!


.. code-block:: shell

    $ flux pstree
    flux
    └── sleep

Submit the same command a few more times? We see that reflected in the tree!

.. code-block:: shell

    $ flux submit sleep 350
    ƒAivupEb
    $ flux submit sleep 350
    ƒB621bj5

    $ flux pstree
    flux
    └── 3*[sleep]


And have you heard of a flux jobspec? This is a data structure that describes the resources, tasks,
and attributes of a job. You can see one doing the following:

.. code-block:: shell

    $ flux job info ƒB621bj5 jobspec | jq

Finally, ``flux top`` is a cool way to see a summary of your jobs:


.. code-block:: shell

    ƒ                                    ƒ63WcEKAP                        3.6e+04d⌚
        nodes [                        0/1]                         0 pending
        cores [                        0/4]                         0 running
         gpus [                        0/0]        3 complete,      0 failed     ♡

     size: 1   depth: 1            uptime: 6.7m               0.47.0-148-ge2b96308f
           JOBID     USER ST NTASKS NNODES RUNTIME NAME                             

Akin to vim, you can hit ``q`` to exit. And that's it!
If you have any questions, please `let us know <https://github.com/flux-framework/flux-docs/issues>`_.
