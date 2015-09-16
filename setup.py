#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    import distutils.command.bdist_conda
except ImportError:
    pass

with open('README.rst') as readme_file:
    readme = readme_file.read()


import neuronvisio

version = neuronvisio.__version__
authors = neuronvisio.__authors__
authors_email = neuronvisio.__authors_emails__

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

entry_points="""
    # -*- Entry points: -*-
    """

# compatible with distutils of python 2.3+ or later
setup(
    name='neuronvisio',
    version=version,
    description='Neuronvisio is a Graphical User Interface for NEURON simulator environment',
    long_description=open('README.rst', 'r').read(),
    packages = ['neuronvisio', 'neuronvisio.modeldb'],
    package_dir={'neuronvisio': 'neuronvisio'},
    include_package_data=True,
    scripts= ['bin/neuronvisio', 'bin/neuronvisio.bat', 
              'bin/neuronvisio-modeldb-updater', 'bin/neuronvisio-modeldb-updater.bat'],
    classifiers=classifiers,
    keywords='neuron, gui, pylab, 3D, visualization',
    author=authors,
    author_email=authors_email,
    url='http://neuronvisio.org',
    license='GPLv3',
    zip_safe=False,
    install_requires=install_requires,
    entry_points=entry_points,
    )