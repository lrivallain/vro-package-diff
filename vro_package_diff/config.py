#!/usr/bin/env python
"""Some config items
"""

SUPPORTED_ELEMENT_TYPES = [
    "Workflow",
    "ScriptModule",
    "Action",
    "ResourceElement",
    "ConfigurationElement"
]
"""list: Currently support is limited to the following types of items."""

import colored
OUTPUT_SETUP = {
    'no_upgrade': {
        'symbol_utf8': ' ⇄ ',
        'symbol_ascii': '<->',
        'color': colored.fg("turquoise_2"),
        'legend': "Items with no upgrade required"
    },
    'upgrade': {
        'symbol_utf8': ' ⇉ ',
        'symbol_ascii': '==>',
        'color': colored.fg("chartreuse_2a"),
        'legend': "Items that will be upgraded in import process"
    },
    'new': {
        'symbol_utf8': '[+]',
        'symbol_ascii': '[+]',
        'color': colored.fg("yellow_1"),
        'legend': "New items (will be imported)"
    },
    'unsupported': {
        'symbol_utf8': ' ⇄ ',
        'symbol_ascii': ' ? ',
        'color': colored.fg("grey_78"),
        'legend': "Items ignored in the vRO merge process"
    },
    'conflict': {
        'symbol_utf8': ' ≠ ',
        'symbol_ascii': '=/=',
        'color': colored.fg("red_1"),
        'legend': "Items with a version conflict"
    },
}
"""dict: Define the configuration of output display (color and symbols)"""

CLI_CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
"""dict: Click module settings to add two way to get help."""