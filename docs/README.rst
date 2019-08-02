
vRO-package-diff tool
=====================

Provide a table-formated diff of two vRealize Orchestrator packages.

.. figure:: ./_static/vro-package-diff-sample.png
    :alt: Sample of output


Installation
------------

Requirements:

* Python (>=3.1)
* pip

Then:

::

    pip install vro_package_diff


Usage
-----

Help
^^^^

::

    vro-diff --help
    Usage: vro-diff [OPTIONS] REFERENCE_PACKAGE COMPARED_PACKAGE

    Start a diff operation between two vRO packages.

    REFERENCE_PACKAGE is the package you want to use as source
    COMPARED_PACKAGE is the one you want to compare with reference one

    Options:
    -l, --legend  Display the legend after the diff table
    -t, --test    Exit with `0` if package can be safely imported. Else, returns
                    the number of errors
    -h, --help    Show this message and exit.


Examples
^^^^^^^^


Compare only

::

    vro-diff tests/data/package_v1.0.package tests/data/package_v1.1.package


Compare, then display legend (`--legend`) and exit with error if there is comflicts (`--test`)

::

    vro-diff --legend --test tests/data/package_v1.0.package tests/data/package_v1.1.package
