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
- the GUI runs in its own thread so it's possible to use the console 
(strongly suggested to run through ipython)


More info are available on the homepage: http://mattions.github.com/neuronvisio/

Offline Documentation
---------------------

To create offline documentation similar to the one online you will need 
sphinx http://sphinx.pocoo.org/ installed.

Move in the doc directory::
    
    cd docs
    
and then launch::

    sphinx-build . html

In the html directory you will have the online doc. 


