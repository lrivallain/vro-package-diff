from distutils.core import setup
import setuptools
import vro_package_diff

try:
    with open("README.md", "r") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "" # empty
except Exception as e:
    raise e

setup(
    name='vro_package_diff',
    version=vro_package_diff.__version__,
    author="Ludovic Rivallain",
    author_email='ludovic.rivallain+vropackagediff@gmail.com',
    packages=setuptools.find_packages(),
    description=
    "Provide a table-formated diff of two VMware vRealize Orchestrator packages.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "terminaltables",  # Pretty print a table
        "colored",  # A bit of colors from fancy term
        "click",  # CLI arguments management
    ],
    classifiers=[
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Operating System :: POSIX :: Linux',
        "License :: OSI Approved :: MIT License", "Environment :: Console"
    ],
    entry_points={
        'console_scripts': [
            'vro-diff=vro_package_diff.__main__:main',
        ],
    })