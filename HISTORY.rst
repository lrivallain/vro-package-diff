=======
History
=======

2.2.1 (2020-11-06)
------------------

Fix: Error in version comparaison #44


2.2.0 (2020-09-18)
------------------

Check for values in the configuration elements: if so, exit with failure status.

Add a new flag to enable this check:

::

   -e, --empty-config   Check for values in the configuration
                           elements: if so, exit with failure status.


2.1.0 (2019-12-19)
------------------

Provide an option to export diff files to a specific folder when a conflict is detected

Add a new option to specify a diff destination folder:

::

   -d, --diff PATH   A folder where to generate unified diff
                        files output



2.0.2 (2019-12-10)
------------------

Support for non UTF8 and non colorized output(s)

Add two new flag to enable specific output formating:

::

   -a, --ascii     Only use ASCII symbols to display results
   -b, --no_color  Do not colorized the output


2.0.1 (2019-08-06)
------------------

MacOSX and Windows support

Note for Windows users:

Windows usage is supported with some limitations:

-  No colored output.

   -  Currently I have no idea on how to fix this.

-  Some UTF-8 symbols used in output are only with some fonts like
   *DejaVu Sans Mono*.

   -  In future, I will try to implement a version of script that do not
      request UTF-8 support to return results.


2.0.0 (2019-08-06)
------------------

vro-package-diff is now a Pypi hosted project

Changes:

-  ``vro-package-diff`` is now a Pypi hosted project:
   `vro-package-diff` and so, can be installed with ``pip install``
   command.
-  An endpoit ``vro-diff`` to access to the tool from any path location.
-  Usage of ```click``` to manage:

   -  inputs packages
   -  help
   -  legend display
   -  test feature

-  A *test* feature
-  Documentation is hosted on `vro-package-diff.readthedocs.io`
-  `Travis pipeline`

.. vro-package-diff: https://pypi.org/project/vro-package-diff/
.. ``click``: https://click.palletsprojects.com/
.. vro-package-diff.readthedocs.io: https://vro-package-diff.readthedocs.io
.. Travis pipeline: https://travis-ci.org/lrivallain/vro-package-diff/


1.0.0 (2018-02-22)
------------------

* First release.
