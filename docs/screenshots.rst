.. _screenshots:

***********
Screenshots
***********

Everybody loves screenshots, so here we go. 

*Notice: Some of the screenshots are missing the modelDB tabs, 'cause 
the functionality was added at later stage. We decided to keep them,
'cause they are stil informative to what you can do with Neuronvisio.* 

GUI control
===========

This is the Controls window. You can create vectors and run simulations. The time shows 
you the time of the NEURON_ simulator.

.. _NEURON: http://www.neuron.yale.edu/neuron/ 

You can change the `tstop`, the `dt` and the initial voltage from the GUI or 
the console.

.. image:: images/Neuronvisio_Controls_Init_and_Run.png

3-Dimensions with a simple model
================================

Rendering of a simple model with 3 section.

.. image:: images/Simple_model.png

The neurons is rendered using the Mayavi pipeline, where is possibile to choose
from different colormap and additional filters.
Using the `GnBu` colormap with the Axes.

.. image:: images/nrnvisio-mayavi-color.png
	:scale: 70

Using the `red-blue` colormap with the Axes.

.. image:: images/nrnvisio-mayavi-color2.png
	:scale: 70

3-Dimensions with a complex model
=================================

Rendering of a more complex model, a pyramidal neuron.

.. image:: images/Neuronvisio_3D.png
    :scale: 70


Animation and pylab graphs
==========================

It is possible to follow the timecourse of a variable in the whole neuron or 
networks using the bottom slider, after the simulation has been ran, 
or reloaded. If a particular point in time is of interest, insert in the 
animation Time line textfield and hit return.
 
The pylab graphs are integrated and can be easily generated with a click. 
For example here we shows hhow the voltage change in a simple model and in 
a pyramidal one.

Simple model
------------

A simple 3 sections model showing the different value of the voltage in the 
cell.

.. image:: images/voltage_variation_among_time.png
    :scale: 70

Pyramidal neuron
----------------

The propagation of the voltage among the neuron. The stimul was given in the 
soma.

.. image:: images/pyramidal_3D_change_voltage.png
    :scale: 70

Pylab integration
-----------------

It is possible to use the standard pylab tool and to plot the timecourses in 
the current figure, or create a new one just selecting another output figure 
number.

.. image:: images/pylab_integration.png
    :scale: 70