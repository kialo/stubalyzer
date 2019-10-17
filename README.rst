Stub Analyzer
=============

Development
-----------

The following section contains instructions on how to set up and use
the development environment for this project.

Setup
+++++

Requirements for development:

*  A recent Python version (we currently use 3.7)
*  ``virtualenv`` and ``virtualenvwrapper``

For a development setup, run the following shell script:

.. code-block:: shell-session

   $ ./dev/setup.sh

This will create a virtual environment called ``stub-analyzer``
and install the projects dependencies.
The setup script also creates a ``.venv`` file so the environment
activates automatically if you use auto-activation with virtualenv.

Tests
+++++

Tests are run using pytest:

.. code-block:: shell-session

   $ pytest

Code Formatting
+++++++++++++++

To set up the pre-commit hook to automatically format files,
create the following link:

.. code-block:: shell-session

   $ ln -sf ../../dev/pre-commit.sh .git/hooks/pre-commit

The source code is formatted using ``black`` and ``isort``.
The following will format all files in the project:

.. code-block:: shell-session

   $ ./dev/fmt.sh


Linting
+++++++

Linting is done using ``flake8``, in the root directory run:

.. code-block:: shell-session

   $ flake8


Dependency Management
+++++++++++++++++++++

If you need new dependencies, add them in ``requirements.in`` and ``setup.py``,
then run the ``pip-compile`` command specified at the top of ``requirements.txt``.
