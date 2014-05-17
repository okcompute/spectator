=================================
  Contributing to ``spectator``
=================================

Contributing to the project is easy.  Just follow these simple steps.

1. Create an issue on the `project issue tracker`_ to describe your feature
   request or bug report.

2. For the project on GitHub_.

3. Get a local copy of your fork.

   ::

      git clone git://github.com/.../spectator.git
      cd spectator

4. Start off with a clean slate.

   ::

      virtualenv site
      . ./site/bin/activate  # ./site/Scripts/activate on Windows.
      pip install -r requirements.txt

5. Check that you're starting off a clean build.

   ::

      flake8 spectator
      pylint spectator
      nosetests

6. Compile and read the documentation.

   ::

      sphinx-build -b html ./docs ./build/docs

7. Work on your feature or bug fix.

   ::

      git checkout -b my-feature-or-bug-fix
      ...

8. Check for any issues and resolve as necessary.

   ::

      nosetests
      flake8 spectator
      pylint spectator
      sphinx-build -q -n -W -b html ./docs ./build/docs


9. Send a pull request!

   ::

      git status
      git add ...
      git commit -m "..."
      git push my-feature-or-bug-fix

   Go to GitHub_ and send the pull request.  Travis_ will take care of running
   tests and static code checkers just in case you forgot to.  When the build
   returns green, I'll look at your pull request, review the changes and merge
   them.


.. _GitHub: https://github.com/
.. _Travis: http://about.travis-ci.org/
.. _`project issue tracker`: https://github.com/AndreLouisCaron/spectator/issues
