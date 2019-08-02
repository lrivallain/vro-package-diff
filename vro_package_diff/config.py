#!/usr/bin/env python
"""Some config items
"""

# Currently support is limited to the following types of items
SUPPORTED_ELEMENT_TYPES = [
    "Workflow",
    "ScriptModule",
    "Action",
    "ResourceElement",
    "ConfigurationElement"
]

import colored
# define output colors
COLOR_CONFLICT    = colored.fg("red_1")
COLOR_NO_UPGRADE  = colored.fg("turquoise_2")
COLOR_UPGRADE     = colored.fg("chartreuse_2a")
COLOR_NEW         = colored.fg("yellow_1")
COLOR_UNSUPPORTED = colored.fg("grey_78")

# click settings to add two way to get help
CLI_CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])