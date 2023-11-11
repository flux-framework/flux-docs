.. raw:: html
   :file: ./comparison-table.html

.. list-table:: Flux Compared to Other Resource Managers
   :widths: 46 6 6 6 6 6 6 6 6 6 
   :header-rows: 1
   :stub-columns: 1
   :class: comparison-table

   * - Features
     - Flux
     - Slurm
     - PBSPro (OpenPBS)
     - LSF
     - MOAB 
     - RadicalPilot
     - Balsam 
     - Parsl 
     - Nitro
   * - 
     - 
     - 
     - 
     - 
     -  
     - 
     -  
     -  
     - 
   * - Open Source
     - yes
     - yes
     - yes
     - no
     - no
     - yes
     - yes
     - yes
     - no

.. list-table:: Multi-User Mode
   :widths: 46 6 6 6 6 6 6 6 6 6 
   :header-rows: 1
   :stub-columns: 1
   :class: comparison-table

   * - Features
     - Flux
     - Slurm
     - PBSPro (OpenPBS)
     - LSF
     - MOAB 
     - RadicalPilot
     - Balsam 
     - Parsl 
     - Nitro
   * - Multi-user workload management
     - yes
     - yes
     - yes
     - yes
     - yes
     - no
     - yes
     - no
     - no
   * - Full hierarchical resource management
     - yes
     - no
     - no
     - no 
     - no 
     - n/a
     - n/a
     - n/a
     - n/a
   * - Graph-based advanced resource management
     - yes
     - no
     - no
     - no 
     - no 
     - n/a
     - n/a
     - n/a
     - n/a
   * - Scheduling specialization
     - yes
     - no
     - no
     - no 
     - no 
     - n/a
     - n/a
     - n/a
     - n/a
   * - Security: only a small isolated layer running in privileged mode for tighter security
     - yes
     - no
     - no
     - no 
     - no 
     - n/a
     - n/a
     - n/a
     - n/a
   * - Modern command-line interface (cli) design
     - yes
     - outdated
     - outdated
     - outdated
     - outdated 
     - n/a
     - n/a
     - n/a
     - n/a
   * - Application programming interface (APIs) for job management, job monitoring, resource monitoring, low-level messaging 
     - yes (4/4)
     - some (3/4)
     - some (2/4)
     - some (2/4)
     - some (3/4) 
     - n/a
     - n/a
     - n/a
     - n/a
   * - Language bindings
     - yes (C, C++, Python, Lua, Rust, Julia, REST)
     - some (C, REST)
     - some (C, Python)
     - some (C, Python)
     - some (C)
     - n/a
     - n/a
     - n/a
     - n/a
   * - Bulk job submission
     - yes
     - only uniform jobs
     - only uniform jobs
     - only uniform jobs
     - only uniform jobs
     - n/a
     - n/a
     - n/a
     - n/a
   * - High-speed streaming job submission
     - yes
     - no
     - no
     - no
     - no
     - n/a
     - n/a
     - n/a
     - n/a

.. list-table:: Single-User Mode
   :widths: 46 6 6 6 6 6 6 6 6 6 
   :header-rows: 1
   :stub-columns: 1
   :class: comparison-table

   * - Features
     - Flux
     - Slurm
     - PBSPro (OpenPBS)
     - LSF
     - MOAB 
     - RadicalPilot
     - Balsam 
     - Parsl 
     - Nitro
   * - User-level workload management intstance
     - yes
     - no
     - no
     - no
     - no
     - yes
     - yes
     - yes
     - yes
   * - Support for nesting within foreign resource manager
     - yes (Slurm, lsf, ...)
     - n/a
     - n/a
     - n/a
     - n/a
     - yes
     - yes
     - yes
     - yes
   * - Fully hierarchical management of instances
     - yes
     - n/a
     - n/a
     - n/a
     - n/a
     - no (two level)
     - no
     - no (two level)
     - no (two level)
   * - Scheduler specialization for user level
     - yes
     - n/a
     - n/a
     - n/a
     - n/a
     - yes
     - no
     - yes (executors)
     - no    
   * - Graph-based advanced scheduling for user level
     - yes
     - n/a
     - n/a
     - n/a
     - n/a
     - no
     - no
     - no
     - no    
   * - Built-in facilities for inter-job communication and coordination
     - yes
     - n/a
     - n/a
     - n/a
     - n/a
     - no
     - no
     - no
     - no    
   * - Modern command-line interface (cli) design
     - yes
     - n/a
     - n/a
     - n/a
     - n/a
     - no cli
     - yes
     - no cli
     - outdated
   * - Application programming interfaces (APIs) for job management, job monitoring, resource monitoring, low-level messaging
     - yes (4/4)
     - n/a
     - n/a
     - n/a
     - n/a
     - yes (4/4)
     - some (2/4)
     - some (2/4)
     - no
   * - Language bindings
     - yes (C, C++, Python, Lua, Rust, Julia, REST)
     - n/a
     - n/a
     - n/a
     - n/a
     - some (Python)
     - some (Python) 
     - some (Python) 
     - no
   * - Bulk job submission
     - yes
     - n/a
     - n/a
     - n/a
     - n/a
     - limited support
     - no
     - limited support
     - only single core jobs
   * - High-speed streaming job submission
     - yes
     - n/a
     - n/a
     - n/a
     - n/a
     - yes
     - no
     - yes
     - no
   * - Support to launch message passing interface (MPI) jobs
     - yes
     - n/a
     - n/a
     - n/a
     - n/a
     - yes
     - yes
     - limited support
     - no