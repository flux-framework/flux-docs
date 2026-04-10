:hide-navigation:

.. Copyright 2020-2023 Lawrence Livermore National Security, LLC
   (c.f. AUTHORS, NOTICE.LLNS, COPYING)

   SPDX-License-Identifier: (LGPL-3.0)

=============================
Flux Framework Documentation
=============================

.. image:: images/logo.png
  :width: 400px
  :align: center

Flux is a resource manager for high-performance computing that schedules jobs across
HPC clusters, cloud resources, and containers. Unlike traditional resource managers,
Flux doesn't require administrator privileges—launch it within other resource managers
or Flux itself, on your laptop, or deploy it as your site's primary scheduler.

This means you get a full-featured resource manager for complex workflows, ensemble
runs, or testing without waiting for sysadmin support. Schedule 10,000-node MPI jobs,
run millions of tasks, or dynamically manage resources within a single batch job.

:ref:`Compare Flux to Slurm/PBS/LSF <comparison-table>` |
:doc:`Get Started <core:guide/start>`

---------------
Getting Started
---------------

.. grid:: 3
   :gutter: 2

   .. grid-item-card:: 🚀 New to Flux

      - :doc:`Try Flux in Docker <tutorials/containers/flux-sched-container>`
      - :doc:`Install Flux <core:guide/build>`
      - :doc:`Tutorials <tutorials/index>`

   .. grid-item-card:: 💻 Using Flux

      - :doc:`Command guide <core:guide/interact>`
      - :doc:`Workflows <core:guide/workflows>`
      - :doc:`Batch jobs <jobs/batch>`
      - :doc:`Job hierarchies <jobs/hierarchies>`
      - :doc:`Debugging jobs <jobs/debugging>`
      - :ref:`Command references <core:man-pages>`

   .. grid-item-card:: ⚙️ Administration/Development

      - :doc:`Admin guide <core:guide/admin>`
      - :doc:`Troubleshooting <core:guide/troubleshooting>`
      - :doc:`Python API <core:python/index>`
      - :doc:`C API <core:man3/index>`
      - :ref:`Architecture & Components <flux-components>`
      - :doc:`About the Flux broker <core:guide/broker>`

------------
Manual Pages
------------

**Command and API references:**
:ref:`core:man-pages` (job commands) |
:ref:`sched:man-pages` (scheduling) |
:ref:`security:man-pages` (security tools)

---------------
Installing Flux
---------------

**Start with** `flux-core <https://github.com/flux-framework/flux-core>`_
(:doc:`install guide <core:guide/build>`) for job execution, commands, APIs, and built-in schedulers.

**For advanced scheduling,** add `flux-sched <https://github.com/flux-framework/flux-sched>`_
(:doc:`install guide <sched:guide/build>`) to enable the fluxion scheduler with graph-based resource matching.

**For multi-user installations,** `flux-security <https://github.com/flux-framework/flux-security>`_
is required for authentication. `flux-accounting <https://github.com/flux-framework/flux-accounting>`_
provides resource accounting and priority management.

-------------
Flux Projects
-------------

Complete documentation for the core Flux projects:

.. grid:: 4
   :gutter: 2

   .. grid-item-card:: flux-core
      :link: https://flux-framework.readthedocs.io/projects/flux-core/en/latest/

      Core resource manager with simple schedulers, job execution, commands, and APIs

   .. grid-item-card:: flux-sched
      :link: https://flux-framework.readthedocs.io/projects/flux-sched/en/latest/

      Fluxion scheduler with graph-based scheduling and resource matching

   .. grid-item-card:: flux-accounting
      :link: https://flux-framework.readthedocs.io/projects/flux-accounting/en/latest/

      Multi-user resource accounting and priority management

   .. grid-item-card:: flux-security
      :link: https://flux-framework.readthedocs.io/projects/flux-security/en/latest/

      Security plugin for authentication in multi-user environments

**See also:** :doc:`flux-pmix, flux-coral2, dyad, and other projects <projects>`

.. toctree::
   :maxdepth: 1
   :hidden:

   faqs
   tutorials/index
   jobs/index
   guides/index
   glossary
   contributing
   projects
   tables/comparison-table

-----------
Quick Links
-----------

:doc:`FAQs <faqs>` |
:doc:`Tutorials <tutorials/index>` |
:doc:`Comics <comics/index>` 🎨 |
`Flux Website <https://flux-framework.org>`_

**Technical:** :doc:`RFCs <rfc:index>` | :doc:`Contributing <contributing>`
