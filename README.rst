vRO-package-diff tool
=====================

|PyPI version shields.io| |PyPI pyversions| |Build Status|
|Documentation Status| |GitHub|

Project description
-------------------

vRO-package-diff is a Python package to compare 2 VMware vRealize
Orchestrator packages.

It provides a table-formated diff of two packages:

|Sample of output|

It is also possible to export `unified diff`_ files for each supported
element:

::

   tree -L 2 ./diff/
   ./diff/
   ├── conflict
   │   ├── action
   │   ├── configurationelement
   │   ├── resourceelement
   │   └── workflow
   ├── no_upgrade
   │   ├── action
   │   ├── configurationelement
   │   └── workflow
   └── upgrade
       ├── action
       ├── configurationelement
       ├── resourceelement
       └── workflow

   cat ./diff/conflict/action/af7b881d-ba59-40d0-8207-be9e9b2ae34d.diff

.. code:: diff

   --- tests/data/package_v1.0.package - Action: this_is_action_a (0.0.1)
   +++ tests/data/package_v1.1.package - Action: this_is_action_a (0.0.1)
   @@ -13,7 +13,5 @@
           // nothing, just for fun :)
    }

   -Plop;
   -
    System.debug("this_is_action_a stopped");]]></script>

Installing
----------

Install and update using pip:

::

   pip install vro-package-diff

vRO-package-diff supports Python 3.5 and newer.

Usage example
-------------

::

   vro-diff --legend --reference_package tests/data/package_v1.0.package tests/data/package_v1.1.package

CLI help
~~~~~~~~

You can get the usage help by using the ``-h``/``--help`` flag:

::

   vro-diff -h

   Usage: vro-diff [OPTIONS] COMPARED_PACKAGE

       Compare two vRealize Orchestrator packages.

       Use the [--reference_package] option to specify the reference package.

   Options:
       -r, --reference_package FILENAME
                                       Reference package to compare your package
                                       with.  [required]
       -l, --legend                    Display the legend after the diff table
       -t, --test                      Exit with `0` if package can be safely
                                       imported. Else, returns the number of errors
       -a, --ascii                     Only use ASCII symbols to display results
       -b, --no_color                  Do not colorized the output
       -d, --diff PATH                 A folder where to generate unified diff

.. _unified diff: https://www.gnu.org/software/diffutils/manual/html_node/Detailed-Unified.html

.. |PyPI version shields.io| image:: https://img.shields.io/pypi/v/vro-package-diff.svg
   :target: https://pypi.python.org/pypi/vro-package-diff/
.. |PyPI pyversions| image:: https://img.shields.io/pypi/pyversions/vro-package-diff.svg
   :target: https://pypi.python.org/pypi/vro-package-diff/
.. |Build Status| image:: https://travis-ci.org/lrivallain/vro-package-diff.svg?branch=master
   :target: https://travis-ci.org/lrivallain/vro-package-diff
.. |Documentation Status| image:: https://readthedocs.org/projects/vro_package_diff/badge/?version=latest
   :target: https://vro_package_diff.readthedocs.io/en/latest/?badge=latest
.. |GitHub| image:: https://img.shields.io/github/license/lrivallain/vro-package-diff
.. |Sample of output| image:: ./docs/_static/vro-package-diff-sample.png