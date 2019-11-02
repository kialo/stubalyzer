Stubalyzer
=============

.. image:: https://readthedocs.org/projects/stubalyzer/badge/?version=latest
    :target: https://stubalyzer.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status


An analysis tool to compare handwritten mypy stubs to stubgen-generated stubs.

**stubalyzer** makes the process of crafting types for untyped dependencies easier.
Some example inconsistencies which are found and reported by stubalyzer are listed below:

- handcrafted and generated stubs have different method signatures
- generated stubs are missing functions/class members
- generated types are more specific than the handcrafted types


How to use?
-----------

Installation
++++++++++++

Install stabalyzer with the following command:

.. code-block:: shell-session

   $ pip install stabalyzer

How to run
++++++++++

Run stabalyzer with the following command:

.. code-block:: shell-session

   $ stabalyzer [-h] -c CONFIG
                [-e EXPECTED_MISMATCHES]
                [-r REFERENCE_STUBS] STUBS_HANDWRITTEN


    required arguments:
        -c CONFIG, --config CONFIG
                            Mypy config file.

    positional arguments:
        STUBS_HANDWRITTEN   Directory of handwritten stubs that need to be
                            analyzed.

    optional arguments:
        -h, --help          Show help message and exit



        -e EXPECTED_MISMATCHES, --expected-mismatches EXPECTED_MISMATCHES

                            Directory of JSON file which defines expected mismatching
                            symbols and their match results. If any symbol is declared
                            in an expected_mismatches JSON file, stabalyzer will count
                            it as an expected failure, and ignore this inconsistency.

                            Example expected mismatches JSON file content:
                            {
                                "my.module.function: "mismatch",
                                "another.module.Class: "not_found"
                            }

                            According to the example mismatches JSON node above,
                            we expect my.module.function signature to mismatch,
                            and another.module.Class to be missing in generated stubs.
                            stubalyzer will ignore these inconsistencies.

        -r REFERENCE_STUBS, --reference REFERENCE_STUBS

                            Directory of reference stubs to compare against.
                            If not specified, stubgen will be used to generate the
                            reference stubs.

Output
++++++

In case of a successful comparison without any inconsistencies in types found,
stubalyzer will print a success message to stdout, alongside
with an ignore message.

Ignore message includes the number of failures ignored,
which are declared as expected in expected_mismatches file. If expected_mismatches file
is not provided, ignore message will always return 0 failure.

.. code-block:: shell-session

      Successfully validated 68 stubs.

      0 fail(s) were ignored.


In case of a comparison with some mismatches in the types found,
stubalyzer will print a list of all inconsistencies
with a result message, alongside with an ignore message
similar to the following:

.. code-block:: shell-session

    Symbol "vars.any_var" not found in generated stubs.

    Types for functions.additional_args do not match:

        def (foo: builtins.int, bar: builtins.int) -> builtins.str

        def (foo: builtins.int) -> builtins.str


    Failure: 33 of 68 stubs seem not to be valid.

    0 fail(s) were ignored.



Development
-----------

The following section contains instructions on how to set up and use
the development environment for this project.


Development Setup
+++++++++++++++++

Requirements for development:

*  A recent Python version (we currently use 3.7)
*  ``virtualenv`` and ``virtualenvwrapper``

For a development setup, run the following shell script:

.. code-block:: shell-session

   $ ./dev/setup.sh

This will create a virtual environment called ``stubalyzer``
and install the projects dependencies.
The setup script also creates a ``.venv`` file so the environment
activates automatically if you use auto-activation with virtualenv.


Tests
+++++

Tests are run using pytest:

.. code-block:: shell-session

   $ pytest


Type Checking
+++++++++++++

Type checking is done with Mypy:

.. code-block:: shell-session

   $ mypy stubalyzer


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


Documentation
+++++++++++++

The documentation is written using Sphinx.

First install the requirements:

.. code-block:: shell-session

    $ pip install -r docs/requirements.txt

Then build the documentation using:

.. code-block:: shell-session

    $ cd doc; make html

The output will be in ``docs/_build/html/index.html``.

You can update the API documentation using the following:

.. code-block:: shell-session

    $ ./dev/update-apidoc.sh
