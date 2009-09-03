#!/usr/bin/env python

# File to install NeuronVisio module
# To install the package run: 
# python setup.py install


from distutils.core import setup

setup(name='NeuronVisio',
      version='0.3.3',
      description='NeuronVisio is a GTK2 user interface for NEURON \
      simulator.',
      author='Michele Mattioni',
      author_email='mattioni@ebi.ac.uk',
      url='http://mattions.github.com/neuronvisio/',
      packages=['nrnVisio']
     )
