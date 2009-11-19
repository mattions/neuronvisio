Neuronvisio  
===========

What is it
----------

NeuronVisio is a GTK2 user interface for `NEURON simulator enviroment 
<http://www.neuron.yale.edu/neuron/>`_. 
NeuronVisio connect with NEURON using the new python NEURON interface.

Features
--------

- 3D visualization of the model with the possibility to change it runtime
- Creation of vectors to record any variables present in the section 
- Pylab integration to plot directly the result of the simulation
- Exploration of the timecourse of any variable among time using a color coded scale
- the GUI runs in its own thread so it's possible to use the console (strongly suggested ipython)


Quick overview
==============

Quick overview of the 3D capabilites. More [screenshots available](screenshots.html).


.. image:: images/neuronWithSpines.png
    :scale: 50


.. image:: images/spines_detailed.png
    :scale: 30

Help and development
====================

MailingList
-----------

There is a `google group`_ to ask for help or send patches. 

.. _google group: http://groups.google.com/group/neuronvisio

Code
----

You can browse the `source code`_ online or if you find a bug please 
submit it to the `tracker`_. 

.. _source code:  http://github.com/mattions/neuronvisio

.. _tracker:  http://github.com/mattions/neuronvisio/issues

Contents
========

.. toctree::
    :maxdepth: 2
    
    installation
    gettingstarted
    screenshots
    reference
    changes
    
 
   

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
