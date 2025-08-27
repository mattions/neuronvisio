Neuronvisio
===========

NOTICE: READ-ONLY REPO
=========
This repository is now **read-only** and will no longer accept Issues or Pull Requests.
I’ve archived it mainly to prevent the automated GitHub bots from running on it—saving a 
bit of energy and avoiding unnecessary emails and notifications.

The code remains available here for historical reasons (you can also find it on the CD included 
with my PhD thesis at the University of Cambridge Library).

A heartfelt thank you to everyone who used Neurovisio (quite some time ago, to be honest).
I hope it proved useful for your research, scientific communication, and maybe even gave 
you some fun along the way.

All the best,
Michele

-----------------------------------------------

.. image:: https://readthedocs.org/projects/neuronvisio/badge/?version=latest
	:target: https://readthedocs.org/projects/neuronvisio/?badge=latest
	:alt: Documentation Status
	
.. image:: https://img.shields.io/pypi/v/neuronvisio.svg
    :target: https://pypi.python.org/pypi/neuronvisio

What is it
----------

Neuronvisio is a Graphical User Interface for `NEURON simulator environment 
<http://www.neuron.yale.edu/neuron/>`_. 
Neuronvisio connect with NEURON using the new python NEURON interface.

Features
--------

- 3D visualization of the model with the possibility to change it runtime
- Creation of vectors to record any variables present in the section 
- Pylab integration to plot directly the result of the simulation
- Exploration of the timecourse of any variable among time using a color coded scale
- the GUI runs in its own thread so it's possible to use the console (integrated with IPython)
- automatically download and load models from `ModelDB <http://senselab.med.yale.edu/modeldb/>`_

More info are available on the homepage: https://neuronvisio.readthedocs.io

Offline Documentation
---------------------

To create offline documentation similar to the one online you will need 
sphinx http://sphinx.pocoo.org/ installed.

Move in the doc directory::
    
    cd docs
    
and then launch::

    make html

In the `_build/html` directory you will have the online doc. 

How To release
--------------

1. Update Changelog
2. Change version at `neuronvisio/__init__.py`
3. Change to same version in conda.recipe/meta.yaml
4. Commit everything
5. Tag repo 
	`python setup.py tag`
6. Upload to pipy and anaconda.org
	- PiPy:
	
		python setup.py make_release
	
	- Anaconda.org:
		Got to anaconda.org and click on the website so the last build will be uploaded 
		to the channel.
