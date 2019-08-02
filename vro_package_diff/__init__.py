"""Provide a table-formated diff of two VMware vRealize Orchestrator packages.

.. moduleauthor:: Ludovic Rivallain <ludovic.rivallain+senseo -> gmail.com>

"""

import sys

if sys.version_info < (3, 0):
    raise Exception(
        'vRO package diff tool requires Python versions 3.0 or later.')

__all__ = [
    'config'
    'vro_element',
]
