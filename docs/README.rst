
|Build Status| |Documentation Status| |GitHub|

.. |Build Status| image:: https://travis-ci.org/lrivallain/vro-package-diff.svg?branch=master
   :target: https://travis-ci.org/lrivallain/vro-package-diff
.. |Documentation Status| image:: https://readthedocs.org/projects/vro_package_diff/badge/?version=latest
   :target: https://vro_package_diff.readthedocs.io/en/latest/?badge=latest
.. |GitHub| image:: https://img.shields.io/github/license/lrivallain/vro-package-diff

vRO-package-diff tool
=====================

Provide a table-formated diff of two vRealize Orchestrator packages.

.. figure:: ./_static/vro-package-diff-sample.png
    :alt: Sample of output


Installation
------------

Requirements:

* Python (>=3.4)
* pip

Then, install and update using pip:

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
                    the number of errors.
    -h, --help    Show this message and exit.


Examples
^^^^^^^^


Compare only:

::

    vro-diff tests/data/package_v1.0.package tests/data/package_v1.1.package


Compare, then display legend (`--legend`):

::

    vro-diff --legend --test tests/data/package_v1.0.package tests/data/package_v1.1.package

Compare, then exit with error if there is any conflict (`-–test`):

::

    vro-diff --test tests/data/package_v1.0.package tests/data/package_v1.1.package
    echo $?

The script will exit with the number of items with a conflict situation.

This `-–test` option can be usefull to implement CI/CD pipelines to compare, then upload(if there is no conflict) vRO packages.


Documentation
-------------

`On ReadTheDocs`_

.. _On ReadTheDocs: https://vro_package_diff.readthedocs.io/
