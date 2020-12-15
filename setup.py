#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

# default python modules
from setuptools import find_packages, setup

# local imports
import vro_package_diff


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "terminaltables",  # Pretty print a table
    "colored",         # A bit of colors from fancy term
    "click",           # CLI arguments management
    "packaging"        # Used to compare versions numbers
]

setup_requirements = [
    'pytest-runner'
]

test_requirements = [
    'pytest>=3'
]

description = "A diff tool for VMware vRealize Orchestrator packages files"

setup(
    name='vro_package_diff',
    version=vro_package_diff.__version__,
    author="Ludovic Rivallain",
    author_email='ludovic.rivallain@gmail.com',
    python_requires='>=3.5',
    packages=find_packages(include=['vro_package_diff', 'vro_package_diff.*']),
    description=description,
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',
    include_package_data=True,
    install_requires=requirements,
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/lrivallain/vro_package_diff',
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows', 'Operating System :: Unix',
        'Operating System :: POSIX :: Linux',
        "License :: OSI Approved :: MIT License", "Environment :: Console"
    ],
    entry_points={
        'console_scripts': [
            'vro-diff=vro_package_diff.__main__:main',
        ],
    })
