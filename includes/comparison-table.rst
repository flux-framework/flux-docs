.. raw:: html
   :file: ./comparison-table.html

.. list-table:: Resource Managers
   :widths: 45 11 11 11 11 11 
   :header-rows: 1
   :stub-columns: 1
   :class: comparison-table

   * - Features
     - Flux
     - Slurm
     - PBSPro (OpenPBS)
     - LSF
     - MOAB 
   * - Open Source
     - yes
     - yes
     - yes
     - no
     - no
   * - License
     - LGPL-3.0
     - GPL-2.1
     - AGPL
     - proprietary
     - proprietary
   * - Multi-user workload management
     - yes
     - yes
     - yes
     - yes
     - yes
   * - Designed to run in user-space without elevated privilege
     - yes
     - no
     - no
     - no 
     - no 
   * - Minimal privileged code contained in separate package and only required for multi-user instances
     - yes
     - no
     - no
     - no 
     - no 
   * - Multiple, customizable scheduling policies and backfill
     - yes (with `flux-sched <https://github.com/flux-framework/flux-sched>`_)
     - yes
     - yes
     - yes 
     - yes
   * - User and project node-hour tracking / accounting
     - yes (with `flux-accounting <https://github.com/flux-framework/flux-accounting>`_)
     - yes
     - yes
     - yes
     - yes
   * - Full hierarchical resource management
     - yes [1]_
     - no
     - no
     - no
     - no 
   * - Model for scheduling arbitrary resource types
     - yes
     - no
     - no
     - no
     - no
   * - Full scheduling happening in each allocation
     - yes 
     - no
     - no
     - no
     - no
   * - Full user control of environment, scheduling policy, resource definitions (and more) in allocations
     - yes
     - no
     - no
     - no
     - no
   * - Unified CLI namespace (``flux batch``, ``flux resource``, etc.)
     - yes
     - no
     - no
     - no
     - no
   * - Batch script submission directives
     - yes
     - yes
     - yes
     - yes
     - yes
   * - C language bindings
     - yes
     - viral (see license)
     - viral (see license)
     - yes 
     - yes 
   * - Python language bindings
     - yes
     - community supported
     - yes
     - yes
     - no 
   * - REST binding for job submission and monitoring
     - in progress
     - yes
     - no
     - no 
     - no
   * - Bulk job submission
     - yes
     - only uniform jobs
     - only uniform jobs
     - only uniform jobs
     - only uniform jobs
   * - Supported binary packages for major Linux distributions
     - in progress for Fedora/RHEL [2]_
     - yes
     - yes
     - yes
     - yes
   * - Officially supported containers on DockerHub
     - yes
     - no
     - community supported
     - no
     - no
   * - Interoperability with Kubernetes
     - yes
     - yes
     - no
     - yes
     - no
   * - Support for batch job elasticity (grow and shrink on demand)
     - in progress [3]_
     - yes
     - no
     - yes
     - no
   * - Automatic failover/restart capabilities (resiliency)
     - in progress [4]_
     - yes
     - yes
     - yes
     - yes
   * - Support for advanced reservations / deferred job start time
     - in progress [5]_
     - yes
     - yes
     - yes
     - yes
   * - Multi-cluster shared accounting database
     - more design needed
     - yes
     - yes
     - yes
     - yes

Footnotes
---------

.. [1] `Flux Learning Guide: Fully Hierarchical Resource Management
       <https://flux-framework.readthedocs.io/en/latest/guides/learning_guide.html#fully-hierarchical-resource-management>`_

.. [2] `flux-core Issue #7211: Request: Official Packaging for Fedora and EPEL
       <https://github.com/flux-framework/flux-core/issues/7211>`_

.. [3] `flux-core Issue #2791: discussion: grow support
       <https://github.com/flux-framework/flux-core/issues/2791>`_

.. [4] `flux-core Issue #3801: enable system instance to be restarted without affecting running jobs
       <https://github.com/flux-framework/flux-core/issues/3801>`_

.. [5] `flux-core Issue #5201: feature tracking: Advanced Reservations (DATs)
       <https://github.com/flux-framework/flux-core/issues/5201>`_
