# vRO-package diff python tool

Provide a table-formated diff of two vRealize Orchestrator packages.

![Sample of output](docs/img/vro-package-diff-sample.png)

## Installation

**Requirements:** Python 3 and pip

Download and create virtual env (optionnal):
```
git clone https://github.com/lrivallain/vro-package-diff.git
cd vro-package-diff
virtualenv -p python3 --no-site-packages venv
. venv/bin/activate
```

Install required python packages:
```
pip install -r requirements.txt
```

## Usage

```
python ./vro_package_diff.py packageA.package packageB.package
```
With:
* `packageA.package` : oldest package file
* `packageB.package` : newest package file

## Logs

Execution logs are saved in the `diff.log`file. The file is overwritten at each execution of the diff tool.
