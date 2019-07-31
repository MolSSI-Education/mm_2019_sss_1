Quickstart Guide
=============================

To do a developmental install, type

 1. `$ git clone https://github.com/MolSSI-Education/mm_2019_sss_1`
 2. `$ cd mm_2019_sss_1`
 3. `$ pip install .`

Dependencies
============================
You need to install: 
 - Python 3.6+

 - numpy

 - matplotlib


Usage
=============================
 1. $ `import mm_2019_sss_1 as mm`

 2. $ `sim = MC(method='random', num_particles = 100, reduced_den = 0.9, reduced_temp = 0.9, max_displacement = 0.1, cutoff = 3.0)`

 3. $ `sim.run(n_steps=50000, freq=1000)`

 4. $ `sim.plot()`



