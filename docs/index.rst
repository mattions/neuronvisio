***********
Neuronvisio 
***********

What is it
==========

Neuronvisio is a Graphical User Interface for `NEURON simulator enviroment 
<http://www.neuron.yale.edu/neuron/>`_ with 3D capabilities. Neuronvisio 
makes easy to select and investigate sections' properties and it offers 
easy integration with matplotlib for plotting the results. 

The geometry can be saved using NeuroML and the computational results in 
a customised and extensible HDF5 format; the results can then be reload in the software
and analysed in a later stage, without re-running the simulation.

Features
========

- 3D visualization of the model with the possibility to change it runtime
- Creation of vectors to record any variables present in the section
- Pylab integration to plot directly the result of the simulation
- Exploration of the timecourse of any variable among time using a color coded scale
- Saving the results simulation for later analysis



Quick overview
==============

Quick overview of the 3D capabilites. More :ref:`screenshots`. 

.. image:: images/neuronWithSpines.png
    :scale: 50

A zoomed version:

.. image:: images/spines_detailed.png
    :scale: 30



Help and development
====================

Install
-------

- To **install** Neuronvisio check the :ref:`install`
- To **browse** the code online go to the `github repo`_
- To **download and install** the code from github check the :ref:`source-code-section` section
- To **submit a bug** use the `tracker`_


.. _github repo:  http://github.com/mattions/neuronvisio
.. _tracker:  http://github.com/mattions/neuronvisio/issues

MailingList
-----------

There is a `google group`_ to ask for help or send patches. 

.. _google group: http://groups.google.com/group/neuronvisio

Site Map
========

.. toctree::
    :maxdepth: 2
    
    self
    install
    gettingstarted
    storage
    screenshots
    reference
    changes
    
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`