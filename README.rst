Neuronvisio
===========

What is it
----------

NeuronVisio is a Graphical User Interface for `NEURON simulator enviroment 
<http://www.neuron.yale.edu/neuron/>`_. 
NeuronVisio connect with NEURON using the new python NEURON interface.

Features
--------

- 3D visualization of the model with the possibility to change it runtime
- Creation of vectors to record any variables present in the section 
- Pylab integration to plot directly the result of the simulation
- Exploration of the timecourse of any variable among time using a color 
coded scale
- the GUI runs in its own thread so it's possible to use the console (strongly suggested to run through ipython)


Installation
============

To install NeuronVisio you need to satisfy the following dependencies

- pygtk: http://www.pygtk.org/
- visual: http://vpython.org/
- matplotlib: http://matplotlib.sourceforge.net/

and of course NEURON_

.. _NEURON: http://www.neuron.yale.edu/neuron/

Easy Install
------------

The easiest way to get neuronvisio is if you have setuptools_ installed::

	easy_install neuronvisio

Without setuptools, it's still pretty easy. Download the neuronvisio.tgz file from 
`neuronvisio's Cheeseshop page`_, untar it and run::

	python setup.py install

.. _neuronvisio's Cheeseshop page: http://pypi.python.org/pypi/neuronvisio/
.. _setuptools: http://peak.telecommunity.com/DevCenter/EasyInstall

Documentation
=============

The documentation is available in the doc folder or online_ or in pdf format in the docs direcotry

.. _online: http://mattions.github.com/neuronvisio

Quickstart
==========

This code is just to give an idea in how to use nrnvisio module:

1. fire up an ipython console with pylab switch.::

    ipython -pylab 	# If you don't use the switch you will not see any graph.
    
2. Import the module::

    from neuronvisio.controls import Controls
    controls = Controls()
    
When nrnvisio is started the thread is launched. In this thread all the process of 
nrnvisio will happen without blocking the console.

As a quick example the following code:

1. Creates a single section called soma
2. Insert an Hodgkey-Huxley channel and a passive conductance 
3. Insert an alphaSynapse to provide a stimul.

A quick example can be the following:::
    
    from nrnvisio.controls import Controls
    controls = Controls() # Starting the GUI
    
    from neuron import h    # Getting the HocInterpreter
    
    soma = h.Section()      # Creating a section
    soma.insert('hh')       # Inserting a HH channel
    soma.insert('pas')      # inserting a passive conductance
    syn = h.AlphaSynapse(0.5, sec=soma)     # synaptic input
    syn.onset = 0.5         # when to fire
    syn.gmax = 0.05         # the conductance of the synapse
    syn.e = 0               # the reversal potential

More example in the example directory show how to use Neuronvisio with more 
complex model.

Contacts
========

Homepage: http://mattions.github.com/neuronvisio/
Mailing List: http://groups.google.com/group/neuronvisio

Help and development
====================

If you'd like to help out, you can fork the project
at http://github.com/mattions/neuronvisio and report any bugs 
at http://github.com/mattions/neuronvisio/issues.


