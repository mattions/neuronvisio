# NeuronVisio 

## What is it

NeuronVisio is a GTK2 user interface for NEURON simulator <http://www.neuron.yale.edu/neuron/>. 
NeuronVisio connect with NEURON using the new python NEURON interface.

## Features

- 3D visualization of the model with the possibility to change it runtime
- Creation of vectors to record any variables present in the section 
- Pylab integration to plot directly the result of the simulation
- Explore of the timecourse of any variable among time using a color coded scale
- the GUI runs in its own thread so it's possible to use the console (strongly suggested ipython)

## Install

To install NeuronVisio you need to satisfy the following dependencies

### Dependences:

- pygtk <http://www.pygtk.org/>
- visual <http://vpython.org/>
- cairo <http://cairographics.org/pycairo/>

then extract the archive and from the directory write

    python setup.py install
    
## Documentation

The documentation is available [online](http://mattions.github.com/neuronvisio/docs.html) and a series 
of examples are available from the examples folder.  

### Quickstart

This code is just to give an idea in how to use nrnVisio module:

1. fire up an ipython console
    ipython
    
2. Import the module
    import nrnVisio         # importing the module
    
When nrnVisio is started the thread is launched. In this thread all the process of nrnVisio will happen without blocking the console.

As a quick example the following code:

1. Creates a single section called soma
2. Insert an Hodgkey-Huxley channel and a passive conductance 
3. Insert an alphaSynapse to provide a stimul.

A quick example can be the following:    
    
    import nrnVisio         # importing the module
    from neuron import h    # Getting the HocInterpreter
    
    soma = h.Section()      # Creating a section
    soma.insert('hh')       # Inserting a HH channel
    soma.insert('pas')      # inserting a passive conductance
    syn = h.AlphaSynapse(0.5, sec=soma)     # synaptic input
    syn.onset = 0.5         # when to fire
    syn.gmax = 0.05         # the conductance of the synapse
    syn.e = 0               # the reversal potential

More example in the example directory show how to use NeuronVisio with more complex model.

More info can be found on the Documentation page
<http://mattions.github.com/neuronvisio/docs.html>

## Contacts

Homepage: <http://mattions.github.com/neuronvisio/>

mail: <mattioni@ebi.ac.uk>

### Development

The code is on github at this address

<http://github.com/mattions/neuronvisio/tree/master>

and git is used as software management tool

To contribute fork the repository with

    git clone git://github.com/mattions/neuronvisio.git

and send me back a patch.

More info on git here: 
<http://git-scm.com/>
