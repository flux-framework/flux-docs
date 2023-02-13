.. _ssh-across-clusters:

===================
SSH across clusters
===================

Let's say you want to create a Flux instance in an allocation on a cluster (e.g., let's say out first cluster is "noodle") 🍜️
and then connect to it via ssh from another cluster (let's say our second cluster is called "quartz"). This is possible with the right
setup of your ``~/.ssh/config``. 

----------------------
Create a Flux Instance
----------------------

First, let's create the allocation on the first cluster. We typically want to ask for an allocation,
and run ``flux start`` via our job manager. Here we might be on a login node:

.. code-block:: console

    # slurm specific
    $ salloc -N4 --exclusive
    $ srun -N4 -n4 --pty --mpibind=off flux start

And then we get our allocation! You might adapt this command to be more specific to your resource manager. E.g., slurm uses srun.
After you run ``flux start``, you are inside of a Flux instance on your allocation!
Let's run a simple job on our allocation. This first example will ask to see the hostnames of your nodes:

.. code-block:: console

    noodle:~$ flux mini run -N 4 hostname
    noodle220
    noodle221
    noodle222
    noodle223

You can sanity check the resources you have within the instance by then running:

.. code-block:: console
    
    noodle:~$ flux resource list
         STATE NNODES   NCORES    NGPUS NODELIST
          free      4      160        0 noodle[220,221,222,223]
     allocated      0        0        0 
          down      0        0        0 


And you can echo ``$FLUX_URI`` to see the path of the socket that you will also need later:

.. code-block:: console

    noodle:~$ echo $FLUX_URI 
    local:///var/tmp/flux-MLmxy2/local-0    

We now have defined a goal for success - getting this listing working by running a command 
from a different cluster node.

-----------------------
Connect to the Instance
-----------------------

Next, let's ssh into another cluster.  Take the hostname where your instance is running,
and create a `proxy jump <https://en.wikibooks.org/wiki/OpenSSH/Cookbook/Proxies_and_Jump_Hosts>`_ in your ``~/.ssh/config``:

.. code-block:: ssh 

    Host noodle
        HostName noodle

    Host noodle220
        hostname noodle220
        ProxyJump noodle

.. note::

  This ``~/.ssh/config`` needs to be written on the cluster system where you are going to connect from.
  In many cases, the shared filesystem could map your home across clusters so you can see the file in
  multiple places.


You'll first need to tell Flux to use ssh for the proxy command:

.. code-block:: ssh 

    quartz:~$ export FLUX_SSH=ssh

Next, from this same location, try using ``flux proxy`` to connect to your Flux Instance! Target the URI
that you found before, ``local:///var/tmp/flux-MLmxy2/local-0``, and add the hostname ``noodle220`` to the address:

.. code-block:: console

     quartz:~$ flux proxy ssh://noodle220/var/tmp/flux-MLmxy2/local-0

If you have trouble - use the force!

.. code-block:: console

     quartz:~$ flux proxy --force ssh://noodle220/var/tmp/flux-MLmxy2/local-0


You should then be able to run the same resource list:

.. code-block:: console

    quartz:~$ flux resource list
         STATE NNODES   NCORES    NGPUS NODELIST
          free      4      160        0 noodle[220,221,222,223]
     allocated      0        0        0 
          down      0        0        0 

Next, try submitting a job! You should be able to see that you are running on the first cluster,
but from the second. 

.. code-block:: console

    quartz:~$ flux mini run hostname
    noodle220

If you are still connected to the first, you should also be able to query the jobs.
E.g., here we submit a sleep from the second connected cluster:

.. code-block:: console

    quartz:~$ flux mini submit sleep 60
    f22hdyb35

And then see it from either cluster node!

.. code-block:: console

    $ flux jobs
       JOBID  USER     NAME       ST NTASKS NNODES     TIME INFO
    f22hdyb35 fluxuser sleep      R       1      1     1.842s 

And that's it! With this strategy, it should be easy to interact with Flux instances from
two resources where ssh is supported. If you have any questions, please `let us know <https://github.com/flux-framework/flux-docs/issues>`_.
