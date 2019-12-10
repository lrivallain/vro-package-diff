# vRO-package-diff tool

[![PyPI version shields.io](https://img.shields.io/pypi/v/vro-package-diff.svg)](https://pypi.python.org/pypi/vro-package-diff/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/vro-package-diff.svg)](https://pypi.python.org/pypi/vro-package-diff/)
[![Build Status](https://travis-ci.org/lrivallain/vro-package-diff.svg?branch=master)](https://travis-ci.org/lrivallain/vro-package-diff)
[![Documentation Status](https://readthedocs.org/projects/vro_package_diff/badge/?version=latest)](https://vro_package_diff.readthedocs.io/en/latest/?badge=latest)
![GitHub](https://img.shields.io/github/license/lrivallain/vro-package-diff)

## Project description

vRO-package-diff is a Python package to compare 2 VMware vRealize Orchestrator packages.

It provides a table-formated diff of two packages.

![Sample of output](./docs/_static/vro-package-diff-sample.png)

## Installing

Install and update using pip:

    pip install vro-package-diff

vRO-package-diff supports Python 3.4 and newer.

## Usage example

    vro-diff --legend tests/data/package_v1.0.package tests/data/package_v1.1.package

### CLI help

You can get the usage help by using the `-h`/`--help` flag:

    vro-diff -h

    Usage: vro-diff [OPTIONS] REFERENCE_PACKAGE COMPARED_PACKAGE

    Start a diff operation between two vRO packages.

    REFERENCE_PACKAGE is the package you want to use as source
    COMPARED_PACKAGE is the one you want to compare with reference one

    Options:
    -l, --legend    Display the legend after the diff table
    -t, --test      Exit with `0` if package can be safely imported. Else,
                    returns the number of errors
    -a, --ascii     Only use ASCII symbols to display results
    -b, --no_color  Do not colorized the output
    -h, --help      Show this message and exit.


## Documentation

[On ReadTheDocs](https://vro_package_diff.readthedocs.io/)
