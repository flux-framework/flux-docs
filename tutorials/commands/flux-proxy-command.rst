.. _flux-proxy-command:

=====================================
Send Commands to Other Flux Instances
=====================================

It is very common to want to connect to other Flux instances other than the default one.  For example, you may want to see the current status of your jobs on a different machine.  Or perhaps you've launched a Flux :ref:`subinstances<subinstance>`, and want submit a new job to that subinstance.

This tutorial will introduce the :core:man1:`flux-proxy` command, which can be used to locally connect yourself to another Flux instance.  It will then allow you to run commands on that instance.

---------------------------
Starting a Flux Subinstance
---------------------------

To illustrate the ``flux proxy`` command, let's create a Flux subinstance to work with.  If you are not familiar with Flux subinstances, subinstances are complete Flux instances run under a subset of resources.  They will have their own scheduler and other Flux services completely independent of the parent instance.

A common way to create a subinstance is through ``flux alloc``.  Let's launch a 4 node subinstance on a cluster called "corona".

.. code-block:: console

   corona-login-node:~$ flux alloc -N4
   corona171:~$ flux resource list
        STATE NNODES   NCORES    NGPUS NODELIST
         free      4      192       32 corona[171,173-175]
    allocated      0        0        0
         down      0        0        0

Notice that we were previously on the node "corona-login-node" and now we are on "corona171".  The ``flux alloc`` command has dropped us into a shell within our own Flux subinstance.  And as you can see, we requested 4 nodes ``-N4`` and ``flux resource list`` shows that our Flux subinstance contains 4 nodes worth of resources.

Let's now submit several ``sleep`` jobs to our subinstance.  To make some later output easier to read, let's label these sleep jobs "Level1" with the ``--job-name`` option.

 .. code-block:: console

   corona171:~$ flux submit -n1 --job-name=Level1 sleep inf
   ƒUSiZvRm
   corona171:~$ flux submit -n1 --job-name=Level1 sleep inf
   ƒUiCzRCj
   corona171:~$ flux jobs
          JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
       ƒUiCzRCj achu     Level1      R      1      1   11.75s corona174
       ƒUSiZvRm achu     Level1      R      1      1   12.36s corona175

Nothing too special here.  We've submitted two jobs to our subinstance and the ``flux jobs`` command shows that we have two jobs running.  You'll notice the name of the jobs is "Level1".

Let's open up another window on the corona login node and type ``flux jobs``.

.. code-block:: console

   corona-login-node:~$ flux jobs
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
     ƒhBaWbFD1nF achu     flux        R      4      4   2.492m corona[171,173-175]

The first thing you'll notice is our two "Level1" jobs are missing.  They aren't listed here.  The reason is that we are now on the parent Flux instance, so it is only showing jobs that were executed under the parent instance.  In this case, its only showing our subinstance.

.. note::

   Depending on your terminal settings, the subinstance may be colored blue in ``flux jobs``, indicating it is a subinstance.

Where are our two "Level1" jobs?  Well, we can show them in ``flux jobs`` via the ``--recursive`` option.

.. code-block:: console

    corona-login-node:~$ flux jobs --recursive
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
     ƒhBaWbFD1nF achu     flux        R      4      4   3.329m corona[171,173-175]

    ƒhBaWbFD1nF:
        ƒUiCzRCj achu     Level1      R      1      1   2.233m corona174
        ƒUSiZvRm achu     Level1      R      1      1   2.243m corona175

As you can see, ``flux jobs`` has recursively started listing jobs in subinstances, showing our two "Level1" jobs.

Now in this particular example, we happen to have a shell that is connected to our subinstance.  However, that may not always be the case (we will show this in an example below).  How can we interact with the subinstance if we don't have a shell open?  For example, how could we submit additional jobs to our subinstance?

--------------------------
Connect to the Subinstance
--------------------------

The easiest way to operate with a subinstance is to use the ``flux-proxy`` command.  It will connect you to another Flux instance, allowing you send commands to it as though you were locally connected.

Let's launch a shell with ``flux proxy`` that will connect us to the subinstance.  All we have to do is give ``flux proxy`` the jobid of the subinstance to connect to it.  If you don't know the jobid of the subinstance, you can find it via ``flux jobs``.

.. code-block:: console

    corona-login-node:~$ flux proxy ƒhBaWbFD1nF
    corona-login-node:~$ flux jobs
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
        ƒUiCzRCj achu     Level1      R      1      1   3.525m corona174
        ƒUSiZvRm achu     Level1      R      1      1   3.535m corona175

You now have a local connection to that Flux subinstance and run commands against it.  This time the ``flux jobs`` output lists the two sleep jobs that we previously submitted.  Notice that the prompt indicates we are still on the the corona login node.  You can exit from the subinstance by typing ``exit``.

You can also specify commands for the other Flux instance on the command line.  Let us try and submit another job to the subinstance.  Again to make display of jobs easier in this example, I'll name the job "Level1A".

.. code-block:: console

    corona-login-node:~$ flux proxy ƒhBaWbFD1nF flux submit -n1 --job-name=Level1A sleep inf
    ƒ4UE5h9qZ

    corona-login-node:~$ flux proxy ƒhBaWbFD1nF flux jobs
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
       ƒ3hRvPnXZ achu     Level1A     R      1      1   8.894s corona173
        ƒUiCzRCj achu     Level1      R      1      1   5.016m corona174
        ƒUSiZvRm achu     Level1      R      1      1   5.026m corona175

As you can see, we've successfully submitted another job to the subinstance running a ``flux submit`` via ``flux proxy``.

You can also use ssh to proxy to an instance by using the instance's native :ref:`URI<URI>` instead of the jobid.  This may be useful if you need to tunnel via ssh to the instance (see :ref:`SSH Across Clusters`<ssh-across-clusters>` for more information).

.. code-block:: console

    corona-login-node:~$ flux uri ƒhBaWbFD1nF
    ssh://corona171/var/tmp/achu/flux-bsZTZV/local-0

    corona-login-node:~$ flux proxy ssh://corona171/var/tmp/achu/flux-bsZTZV/local-0 flux jobs
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
       ƒ3hRvPnXZ achu     Level1A     R      1      1    1.56m corona173
        ƒUiCzRCj achu     Level1      R      1      1   6.428m corona174
        ƒUSiZvRm achu     Level1      R      1      1   6.438m corona175

-------------------------------------
Connect to Subinstance in Subinstance
-------------------------------------

What if you have subinstances inside a subinstance?  You could run a ``flux proxy`` inside of another ``flux proxy``.  But you can also use ``flux proxy's`` slash shorthand.

Let's create an additional subinstance inside our current Flux instance.  We'll create it via the ``flux batch`` command.  If you are unfamiliar with this command, it is similar to ``flux alloc`` except you will not be dropped into a shell.

We will feed this script into the batch command.

.. code-block:: sh

   #!/bin/sh
   #filename: subinstance-jobs.sh

   jobid1=`flux submit -n1 --job-name=Level2 sleep inf`
   jobid2=`flux submit -n1 --job-name=Level2 sleep inf`
   flux job status ${jobid1} ${jobid2}

As you can see, all this script does is launch several ``sleep`` jobs and then wait for the jobs to complete via ``flux job status``.  To make some output easier for later, we've named these jobs "Level2".

Let's launch this in the subinstance using ``flux proxy``.

.. code-block:: console

    corona-login-node:~$ flux proxy ƒhBaWbFD1nF flux batch -n4 ./subinstance-jobs.sh
    ƒ4xzRvx87

    corona-login-node:~$ flux proxy ƒhBaWbFD1nF flux jobs
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
       ƒ4xzRvx87 achu     subinstan+  R      4      1   35.62s corona171
       ƒ3hRvPnXZ achu     Level1A     R      1      1   3.376m corona173
        ƒUiCzRCj achu     Level1      R      1      1   8.243m corona174
        ƒUSiZvRm achu     Level1      R      1      1   8.254m corona175

As you can see, the new sleep jobs are not listed in the proxy ``flux jobs`` output.  They are within the new Flux subinstance we just created, which you can see in the above as jobid ``ƒ4xzRvx87`` .  I can prove this to you by using ``flux jobs --recursive``.

.. code-block:: console

    corona-login-node:~$ flux jobs --recursive
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
     ƒhBaWbFD1nF achu     flux        R      4      4   10.21m corona[171,173-175]

    ƒhBaWbFD1nF:
       ƒ4xzRvx87 achu     subinstan+  R      4      1   1.466m corona171
       ƒ3hRvPnXZ achu     Level1A     R      1      1   4.248m corona173
        ƒUiCzRCj achu     Level1      R      1      1   9.116m corona174
        ƒUSiZvRm achu     Level1      R      1      1   9.126m corona175

    ƒhBaWbFD1nF/ƒ4xzRvx87:
         ƒdAoUkw achu     Level2      R      1      1   1.426m corona171
         ƒYfsfAF achu     Level2      R      1      1   1.429m corona171

With this output you can see all the jobs we've submitted.  We have our original subinstance ("ƒhBaWbFD1nF"), the 3 "Level1" sleep jobs in the first subinstance, the new subinstance within a subinstance ("ƒ4xzRvx87") and our new "Level2" sleep jobs.

So how could we connect to this new subinstance within a subinstance?

To get the job ids of one of the subinstances we can run a ``flux proxy`` inside of another ``flux proxy``.

.. code-block:: console

    corona-login-node:~$ flux proxy ƒhBaWbFD1nF flux proxy ƒ4xzRvx87 flux jobs
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
         ƒdAoUkw achu     Level2      R      1      1    1.97m corona171
         ƒYfsfAF achu     Level2      R      1      1   1.973m corona171

Or we can use the special shorthand which separates job ids by a slash.

.. code-block:: console

    corona-login-node:~$ flux proxy ƒhBaWbFD1nF/ƒ4xzRvx87 flux jobs
           JOBID USER     NAME       ST NTASKS NNODES     TIME INFO
         ƒdAoUkw achu     Level2      R      1      1   2.336m corona171
         ƒYfsfAF achu     Level2      R      1      1   2.339m corona171

Each of these allows us to connect to the new inner subinstance and interact with it.

-------------------------
Proxy to Flux Under Slurm
-------------------------

A special slurm proxy resolver is also available if you launch Flux under Slurm.  Let's launch a Flux instance under Slurm on another cluster.

.. code-block:: console

    $ srun -N4 --pty flux start

From another window let's get the job id of this Slurm job.  I'll get it via ``squeue``:

.. code-block:: console

    $ squeue
        JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
       321104    pbatch     flux     achu  R       0:28      4 opal[63-66]

We can proxy to the Flux instance via the ``slurm`` prefix, indicating this is a Slurm jobid.

As an exmple, I'll submit a job to the Flux instance via ``flux submit`` then we see can see the jobs with ``flux jobs``.

.. code-block:: console

    $ flux proxy slurm:321104 flux submit sleep 60
    fqyZGwh1

    $ flux proxy slurm:321104 flux jobs
           JOBID USER     NAME       ST NTASKS NNODES  RUNTIME NODELIST
        fqyZGwh1 achu     sleep       R      1      1   5.605s opal66

If you have any questions, please `let us know <https://github.com/flux-framework/flux-docs/issues>`_.
