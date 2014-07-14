===============================================
  API documentation for ``spectator`` package
===============================================


.. automodule:: spectator

   .. autoclass:: AllSeeingEye

      .. automethod:: time_to_wait
      .. automethod:: watching
      .. automethod:: watch
      .. automethod:: blink

   .. autoclass:: Scheduler

      .. automethod:: next_deadline
      .. automethod:: schedule
      .. automethod:: elapsed

   .. autofunction:: generate_intervals
   .. autofunction:: generate_deadlines
   .. autofunction:: local_stopwatch


Contents:

.. toctree::
   :maxdepth: 2

   api/monitor.rst
