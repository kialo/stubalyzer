Stubalyzer
==========

.. image:: https://readthedocs.org/projects/stubalyzer/badge/?version=latest
    :target: https://stubalyzer.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status


An analysis tool to
compare handwritten mypy stubs to stubgen-generated stubs.

**stubalyzer** makes the process of crafting types for untyped dependencies easier.
Some example inconsistencies which are found and reported by stubalyzer
are listed below:

-  handcrafted and generated stubs have different method signatures
-  generated stubs are missing functions/class members
-  generated types are more specific than the handcrafted types

How to use?
-----------

Installation
~~~~~~~~~~~~

Install stubalyzer with the following command:

.. code:: shell-session

   $ pip install stubalyzer

How to run
~~~~~~~~~~

Run stubalyzer with the following command:

.. code:: shell-session

   $ stubalyzer -h
   usage: stubalyzer [-h] -c CONFIG [-e EXPECTED_MISMATCHES] [-r REFERENCE_STUBS] [-x CHECKSTYLE_REPORT] [-s] [-p]
                     STUBS_HANDWRITTEN

   Analyze a set of (handcrafted) mypy stubs by comparing them to (generated)
   reference stubs

   required arguments:
   -c CONFIG, --config CONFIG
                           Mypy config file

   positional arguments:
     STUBS_HANDWRITTEN     Directory of handwritten stubs that need to be
                           analyzed

   optional arguments:
     -h, --help            show this help message and exit
     -e EXPECTED_MISMATCHES, --expected-mismatches EXPECTED_MISMATCHES
                           A JSON file, which defines expected mismatching
                           symbols and their match results. If any symbol is
                           declared in an expected_mismatches JSON file,
                           stubalyzer will count it as an expected failure, and
                           ignore this inconsistency.

                           Example contents:
                           {
                               "my.module.function: "mismatch",
                               "another.module.Class: "not_found"
                           }

                           According to the example above, we expect the signature
                           of my.module.function to mismatch, and module.Class to
                           be missing in the generated stubs. stubalyzer will
                           ignore these inconsistencies.
     -r REFERENCE_STUBS, --reference REFERENCE_STUBS

                           Directory of reference stubs to compare against. If
                           not specified stubgen will be used to generate the
                           reference stubs.
     -x CHECKSTYLE_REPORT, --checkstyle-report CHECKSTYLE_REPORT

                           Write an xml report in checkstyle format to the given file.
     -s, --silent
                           Suppress all non-error output.
     -p, --include-private

                           Include definitions stubgen would otherwise consider
                           private, when generating the reference stubs. (e.g.
                           names with a single leading underscore, like "_foo")

Output
~~~~~~

If the comparison ends successfully with zero inconsistencies,
stubalyzer will print a success message to stdout, alongside with an
ignore message.

The ignore message includes the number of failures ignored, which are
declared as expected in the file for expected mismatches. If this file
is not provided, the ignore message will not be printed.

.. code:: shell-session

   Successfully validated 68 stubs.

If there are mismatches in the given types, stubalyzer will print a list
of all inconsistencies with a result message, alongside with an ignore
message -if there is any, similar to the following:

.. code:: shell-session

   Symbol "vars.any_var" not found in generated stubs.

   Types for functions.additional_args do not match:

      Handwritten type: def (foo: builtins.int, bar: builtins.int) -> builtins.str

      Reference type  : def (foo: builtins.int) -> builtins.str


   Failure: 33 of 68 stubs seem not to be valid.

   2 more fail(s) were ignored, because they were defined in expected mismatches.

Development
-----------

The following section contains instructions on how to set up and use the
development environment for this project.

Development Setup
~~~~~~~~~~~~~~~~~

Requirements for development:

-  A recent Python version (we currently use 3.7)
-  ``virtualenv`` and ``virtualenvwrapper``

For a development setup, run the following shell script:

.. code:: shell-session

   $ ./dev/setup.sh

This will create a virtual environment called ``stubalyzer`` and install
the projects dependencies. The setup script also creates a ``.venv``
file so the environment activates automatically if you use
auto-activation with virtualenv.

Tests
~~~~~

Tests are run using pytest:

.. code:: shell-session

   $ pytest

Type Checking
~~~~~~~~~~~~~

Type checking is done with Mypy:

.. code:: shell-session

   $ mypy stubalyzer

Code Formatting
~~~~~~~~~~~~~~~

To set up the pre-commit hook to automatically format files, create the
following link:

.. code:: shell-session

   $ ln -sf ../../dev/pre-commit.sh .git/hooks/pre-commit

The source code is formatted using ``black`` and ``isort``. The
following will format all files in the project:

.. code:: shell-session

   $ ./dev/fmt.sh

Linting
~~~~~~~

Linting is done using ``flake8``, in the root directory run:

.. code:: shell-session

   $ flake8

Dependency Management
~~~~~~~~~~~~~~~~~~~~~

If you need new dependencies, add them in ``requirements.in`` and
``setup.py``, then run the ``pip-compile`` command specified at the top
of ``requirements.txt``.

Documentation
~~~~~~~~~~~~~

The documentation is written using Sphinx.

First install the requirements:

.. code:: shell-session

   $ pip install -r docs/requirements.txt

Then build the documentation using:

.. code:: shell-session

   $ cd doc; make html

The output will be in ``docs/_build/html/index.html``.

You can update the API documentation using the following:

.. code:: shell-session

   $ ./dev/update-apidoc.sh

Releases
~~~~~~~~

Stubalyzer has no fixed release schedule.
Instead releases are made when needed.

To prepare a new release, run the following and follow the instructions in the output:

.. code:: shell-session

   $ ./dev/release.sh <patch|minor|major>
