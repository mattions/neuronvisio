.. _install:

*******
Install
*******

Requirements
============

To install NeuronVisio you need to satisfy the following dependencies

- PyQt4: http://www.riverbankcomputing.co.uk/software/pyqt/download
- ipython: http://ipython.org 0.12 or better
- mayavi2: http://code.enthought.com/projects/mayavi/  4.4.1.dev or better
- matplotlib: http://matplotlib.sourceforge.net/
- setuptools: http://pypi.python.org/pypi/setuptools
- pytables: http://www.pytables.org/

and of course NEURON_ compiled with python support

.. _NEURON: http://www.neuron.yale.edu/neuron/  

Ubuntu and friends
------------------

On Ubuntu you can easily install all the requirements using apt-get with::

    sudo apt-get install python-qt4 ipython python-matplotlib \
    python-setuptools python-tables python-mayavi 

If you are running a different flavour of GNU/Linux, like Fedora for example, just install 
the requirements with your package manager, then go to the `Package Install`_.

Mac OS X
---------

Install the PyQt4_

.. _PyQt4: http://www.riverbankcomputing.co.uk/software/pyqt/download

To get ipython, mayavi and matplotlib it's higly suggested to get a 
prepackaged scientific python distribution

Some pointers:
 
- Enthought Distribution: http://www.enthought.com/products/epd.php
- Scipy SuperPack: http://macinscience.org/?page_id=6

The last one is maybe missing mayavi2. you can automatically installing it
following the `Package Install`_.

Windows
-------

You need to install 

- PyQt4:  http://www.riverbankcomputing.co.uk/software/pyqt/download

Some pointers as for MAC:

- Enthought Distribution: http://www.enthought.com/products/epd.php
- Python(x,y): http://www.pythonxy.com/foreword.php

The last one is maybe missing mayavi2. Follow the instruction on 
`mayavi doc_` to install it

.. mayavi doc: http://code.enthought.com/projects/mayavi/docs/development/html/mayavi/installation.html

Proceed to the `Package Install`_ .


Package Install
===============

To install neuronvisio we suggest to create a virtualenv and install
the packages there. Check out virtualenv_ and virtualenvwrapper_

.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _virtualenvwrapper: http://pypi.python.org/pypi/virtualenvwrapper


.. note:: Neuronvisio 0.8.0 depends on a development version of Mayavi, until this is integrated in Mayavi master. You still have to fullfill the Mayavi's requirements listed on `Mayavi website`_.

.. _Mayavi website: http://github.enthought.com/mayavi/mayavi/installation.html#requirements-for-manual-installs 

If you have `pip`_ installed and all the requirements are already met you 
can install neuronvisio typing::

    pip install -U --extra-index-url=http://www.ebi.ac.uk/~mattioni/snapshots/ neuronvisio

.. _Neuronvisio's PyPI page: http://pypi.python.org/pypi/neuronvisio/
.. _pip: http://pypi.python.org/pypi/pip

Running the bleeding edge
-------------------------

If you want to run the latest code you can clone the git repo and run the software from there::

    git clone git://github.com/mattions/neuronvisio.git neuronvisio

then you need to add the directory (the absolute path) to your PYTHONPATH (in bash)::
    
    export PYTHONPATH=$PYTHONPATH:/path-to-neuronvisio-dir
    
.. _source-code-section:

Source Code
===========

The `source code`_ is on github_ at this address and git_ is used as software 
management tool

.. _source code: http://github.com/mattions/neuronvisio
.. _github: https://github.com/
.. _git: http://git-scm.com/

To install from the git just clone the repo::

    git clone git://github.com/mattions/neuronvisio.git

and then run::
    
    python setup.py install    