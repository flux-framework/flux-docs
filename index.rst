:hide-navigation:

.. Copyright 2020-2023 Lawrence Livermore National Security, LLC
   (c.f. AUTHORS, NOTICE.LLNS, COPYING)

   SPDX-License-Identifier: (LGPL-3.0)

.. Flux documentation master file, created by
   sphinx-quickstart on Fri Jan 10 15:11:07 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Flux's documentation!
================================

.. image:: images/logo.png
  :width: 600px

Flux is a flexible framework for resource management, built for your site.
The framework consists of a suite of projects, tools, and libraries which may be used to build site-custom resource managers for High Performance Computing centers.
Unlike traditional resource managers, Flux can run as a parallel job under most launchers that support MPI, including under Flux itself. This not only makes batch scripts and workflows for Flux portable to other resource managers (just launch Flux as a job), but it also means that batch jobs have all the features of a full resource manager at their disposal, as if they have an entire cluster to themselves.
If you are interested in a high level comparison of Flux to other resource managers, see :ref:`comparison-table`. If you want to get a high level overview of Flux projects or components, take a look at our :ref:`flux-components` page.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   quickstart
   faqs
   tutorials/index
   jobs/index
   guides/index
   contributing
   glossary
   comics/index

.. toctree::
   :maxdepth: 1
   :caption: Sub-Projects

   projects

.. toctree::
   :maxdepth: 1
   :caption: Comparison Table

   tables/comparison-table


Contributor Relevant RFCs
-------------------------

- :doc:`rfc:spec_1`
- :doc:`rfc:spec_2`
- :doc:`rfc:spec_7`
- :doc:`rfc:spec_9`


All RFCs
--------

- :doc:`rfc:index`


Manual Pages
------------

- :ref:`core:man-pages`
- :ref:`sched:man-pages`
- :ref:`security:man-pages`
