"""Provide a table-formated diff of two VMware vRealize Orchestrator packages.

.. moduleauthor:: Ludovic Rivallain <ludovic.rivallain+senseo -> gmail.com>

"""

import sys
if sys.version_info < (3, 4):
    raise Exception('vRO package diff tool requires Python versions 3.4 or later.')

__all__ = [
    'config'
    'vro_element',
]

__version__="2.0.1"
"""Define the version of the package.
"""