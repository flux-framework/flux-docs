.. _debugging:

==============
Debugging Jobs
==============

Debugging Flux jobs has been tested with Rogue Wave Software (RWS)'s
`TotalView parallel debugger <https://totalview.io>`_ and
Linaro `DDT <https://www.linaroforge.com/linaroDdt/>`_. More detailed
instructions for specific debuggers are included in the sections below.

----------------------------------
Parallel Debugging using TotalView
----------------------------------

Debugging your MPI job from the beginning
of parallel program execution:

.. code-block:: console

  $ totalview --args flux run -N 2 -n 2 ./mpi-program

Attaching to an already running job:

.. code-block:: console

  $ flux job attach --debug <JOBID> &
  $ PID=$!
  $ totalview -pid ${PID} /proc/${PID}/exe

You can also just type ``totalview`` without ``-pid`` option.

For the TotalView Classic user interface, select the process of this
``flux-job`` command with
:menuselection:`Start a Debugging Session --> A running program (attach)`.

For new UI: use :menuselection:`Attach To Process`.

.. note::
  You use TotalView with the newly invoked ``flux job attach``
  when your job has been launched via ``flux run`` (or ``flux submit``).
  This is because Flux currently does not allow TotalView
  to attach to your running code if you just attach it
  to the ``flux run`` process that controls your code. For
  performance reasons, ``flux run`` does not generate
  sufficient debug information when it is invoked with no tool control.

Flux provides ``MPIR_partial_attach_ok`` `[1] <https://www.mpi-forum.org/docs/mpir-specification-10-11-2010.pdf>`_
so you can attach TotalView to a subset of parallel processes as well, which
can be handy when you debug a large-scale job. Please refer to
`TotalView user guide`_ on its subset-attach capability.

.. _TotalView user guide: https://docs.roguewave.com/en/totalview/current/html/

Exiting TotalView without completing a full run of your code may not clean
up the Flux job.  In that case you will need to cancel the flux job manually.

.. code-block:: console

  $ flux cancel <JOBID>

.. note::
  Use ``flux jobs`` to find <JOBID>

----------------------------------------------
Better Handling of Flux's Internal Exec Events
----------------------------------------------

Flux executes a series of subcommands before launching
your parallel program.
Thus, a side effect of the above commands is that TotalView
will stop Flux's own program execution each time
a new subcommand is ``exec(3)``'ed (e.g., when ``flux`` ``exec``'s
``flux-run``) before your parallel program processes are spawned.
This means you must manually click "Yes" whenever a stop-at-exec
dialogue window is popped up. You do not need to stop
it unless you are a Flux developer!
Instead, you can make TotalView automatically
continue on these events by building the the following
exec-handling Tcl code into TotalView::

    catch {dset TV::exec_handling { {^(flux|lrun|srun|jsrun)(<python[^>]*>(<flux-job>)?|<bash>|<jsrun>|<jswrap>)*$ go}} }

This code should either be added to the site-wide ``.tvdrc`` file
to enable this for all TotalView sessions
or per-user file (e.g., ``tvdrc`` in the current working directory)
to enable this only for the user's own sessions.
For the latter case, you should provide ``-s tvdrc`` option
to ``totalview``. For example,

.. code-block:: console

  $ totalview -s tvdrc --args flux run -N 2 -n 2 ./mpi-program

Notice that it is designed to support not only Flux but also Slurm's
srun and IBM JSM's jsrun commands. The ``regex`` syntax of
``exec_handling`` within TotalView can be found in `TotalView user guide`_.

---------------------------
Parallel Debugging with DDT
---------------------------

While at this time DDT does not have native support for Flux, small to
medium size jobs can be debugged with DDT using a combination of the
:core:man1:`flux job` :command:`hostpids` command and the :command:`ddt
--attach` option. For example, to attach :command:`ddt` to the previous
job

.. code-block:: console

  $ ddt --attach=$(flux job hostpids $(flux job last))

Flux can launch jobs with every task stopped in :linux:man2:`exec` by
providing the ``stop-tasks-in-exec`` job shell option. Thus, launching a
job under control of DDT can be simulated by something like:

.. code-block:: console

  $ ddt --attach=$(flux job hostpids $(flux submit -n 265 myapp))

The :command:`flux job hostpids` command will block until the job has started
running and the process IDs for all tasks are available, and therfore
:command:`ddt` will not launch until the job has started and is ready
for debugger attach. Since tasks have been stopped in :linux:man2:`exec`,
the debugger will have control of job tasks before execution begins.

.. note::

  :command:`flux job hostpids` was added in flux-core v0.60.0.

------------
Known Issues
------------
Parallel debugging support within Flux is new and we are working with
tool builders to mature our functionality further. This section documents
some of known limitations.

1. Depending on how the site configured TotalView,
the parallel program may not stop at the first instruction
to allow TotalView to debug them from the beginning of execution.
For performance reasons, TotalView can be configured
not to stop and process dynamic libraries and this
can cause this issue. RWS is actively looking
at this issue.

