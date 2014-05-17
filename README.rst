=====================================================
  ``spectator``: a process resource monitoring tool
=====================================================

:author: Andre Caron (andre.l.caron@gmail.com)


Introduction
============

This project is a simple process monitoring tool.  It measures stuff like CPU
time, memory usage and displays it conveniently.


Running the spectator agent
===========================

Runing on Windows
-----------------

.. attention:: On Windows you need to install the ``pywin32`` package.

.. hint:: To install ``pywin32`` in a virtual environment, you can use the
   following command::

   $ env\Scripts\activate
   $ easy_install pywin32-nnn.win32-py2.7.exe


Testing
=======

Testing on Windows
------------------

Nose's ``attrib`` plug-in is used to filter out platform-specific tests.  To
run tests for platform-agnostic code **and** Windows-specific tests, use the
following command::

   $ env\Scripts\activate
   $ nosetests -a "!platform" -a "platform=windows"


Licensing and redistribution
============================

The project is released under a GPL-compatible 2-clause BSD license.  See the
``LICENSE.txt`` file for exact text.
