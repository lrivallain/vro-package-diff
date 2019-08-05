# vRO-package-diff tool

[![Build Status](https://travis-ci.org/lrivallain/vro-package-diff.svg?branch=master)](https://travis-ci.org/lrivallain/vro-package-diff)
[![Documentation Status](https://readthedocs.org/projects/vro_package_diff/badge/?version=latest)](https://vro_package_diff.readthedocs.io/en/latest/?badge=latest)
![GitHub](https://img.shields.io/github/license/lrivallain/vro-package-diff)

## Project description

vRO-package-diff is a Python package to compare 2 VMware vRealize Orchestrator packages.

It provides a table-formated diff of two packages.

![Sample of output](./docs/_static/vro-package-diff-sample.png)

## Installing

Install and update using pip:

    pip install click

vRO-package-diff supports Python 3.4 and newer.

## Usage example

    vro-diff --legend tests/data/package_v1.0.package tests/data/package_v1.1.package

## Documentation

[On ReadTheDocs](https://vro_package_diff.readthedocs.io/)
