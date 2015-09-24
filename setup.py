#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import subprocess

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()


import neuronvisio

version = neuronvisio.__version__
authors = neuronvisio.__authors__
authors_email = neuronvisio.__authors_emails__


if sys.argv[-1] == 'tag':
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

if sys.argv[-1] == 'make_docs':
    p = subprocess.Popen(["make", "html"], cwd="docs")
    p.wait()
    sys.exit()

if sys.argv[-1] == "make_package":
    os.system("python setup.py sdist bdist_wheel")
    sys.exit()

if sys.argv[-1] == "make_release":
    os.system("python setup.py sdist bdist_wheel upload")
    sys.exit()

classifiers = [
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    "Development Status :: 4 - Beta",
    "Programming Language :: Python",
    "Topic :: Scientific/Engineering :: Visualization"

    ]

install_requires = [
    # -*- Install requires: -*-
    'setuptools',
    'pip'
    ]

entry_points = {
                  'console_scripts': [
                    'neuronvisio = neuronvisio.command_line:main_neuronvisio',
                    'neuronvisio-model-updater = neuronvisio.command_line:main_model_updater'
                    ],
               }
# compatible with distutils of python 2.3+ or later
setup(
    name='neuronvisio',
    version=version,
    description='Neuronvisio is a Graphical User Interface for NEURON simulator environment',
    long_description=open('README.rst', 'r').read(),
    packages = ['neuronvisio', 'neuronvisio.modeldb'],
    package_dir={'neuronvisio': 'neuronvisio'},
    include_package_data=True,
    classifiers=classifiers,
    keywords='neuron, gui, pylab, 3D, visualization',
    author=authors,
    author_email=authors_email,
    url='http://neuronvisio.org',
    license='GPLv3',
    zip_safe=False,
    install_requires=install_requires,
    entry_points=entry_points
    )