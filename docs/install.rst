.. _install:

*******
Install
*******

Requirements
============

To install NeuronVisio you need to satisfy the following dependencies

- PyQt4: http://www.riverbankcomputing.co.uk/software/pyqt/download
- ipython: http://ipython.scipy.org/moin/
- mayavi2: http://code.enthought.com/projects/mayavi/ 3.4+ (`Mayavi SVN`_)
- matplotlib: http://matplotlib.sourceforge.net/


and of course NEURON_. compiled with python support

.. _NEURON: http://www.neuron.yale.edu/neuron/

Ubuntu and friends
==================

On Ubuntu you can easily install all the requirements using apt-get with::

    sudo apt-get install python-qt4 ipython python-matplotlib

and then add the `Neuronvisio PPA`_ on launchpad adding the repositories::
    
    deb http://ppa.launchpad.net/mattions/neuronvisio/ubuntu karmic main 
    deb-src http://ppa.launchpad.net/mattions/neuronvisio/ubuntu karmic main

adding the key::
    
    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 4B2C6C7E
    
updating and installing::
    
    sudo update
    sudo install neuronvisio     
    
.. _Neuronvisio PPA: https://launchpad.net/~mattions/+archive/neuronvisio

If you are running a different flavour of GNU/Linux, like Fedora for example, just install 
the requirements with your package manager, then go to the `Package Install`_.

Mayavi SVN
==========

Neuronvisio takes advantage of some of the new features which are only present in Mayavi SVN ATM

`How to install Mayavi from SVN`_.

.. _How to install Mayavi from SVN: http://code.enthought.com/projects/mayavi/docs/development/html/mayavi/installation.html#the-bleeding-edge-svn

On Ubuntu you will need to install manually these two modules: `python-vtk python-configobj`::

    sudo apt-get install python-vtk python-configobj

Mac OS X
========

Install the PyQt4_

.. _PyQt4: http://www.riverbankcomputing.co.uk/software/pyqt/download

To get ipython, mayavi and matplotlib it's higly suggested to get a 
prepackaged scientific python distribution

Some pointers:
 
- Enthought Distribution: http://www.enthought.com/products/epd.php
- Scipy SuperPack: http://macinscience.org/?page_id=6

The last one is maybe missing mayavi2. Follow the instruction on `mayavi doc_` to install it

.. mayavi doc: http://code.enthought.com/projects/mayavi/ 
 
Then move to `Package Install`_.

Windows
=======

You need to install 

- PyQt4:  http://www.riverbankcomputing.co.uk/software/pyqt/download

Some pointers as for MAC:

- Enthought Distribution: http://www.enthought.com/products/epd.php
- Python(x,y): http://www.pythonxy.com/foreword.php

The last one is maybe missing mayavi2. Follow the instruction on `mayavi doc_` to install it

.. mayavi doc: http://code.enthought.com/projects/mayavi/

Proceed to the `Package Install`_ .

Package Install
===============

If you have `pip`_ installed and all the requirements are already met you can install neuronvisio 
in a really handy way::

    pip install neuronvisio

Without pip, if you met all the requirements it's still pretty easy. Download the latest 
neuronvisio.tgz file from `Neuronvisio's PyPI page`_, untar it and run::

    python setup.py install

.. _Neuronvisio's PyPI page: http://pypi.python.org/pypi/neuronvisio/
.. _pip: http://pypi.python.org/pypi/pip

Legacy releases
===============

You can find all the old Neuronvisio releases on `github repo`_

.. _github repo: http://github.com/mattions/neuronvisio/downloads


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


