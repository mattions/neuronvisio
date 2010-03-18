.. _install:

*******
Install
*******

Requirements
============

To install NeuronVisio you need to satisfy the following dependencies

- PyQt4: http://www.riverbankcomputing.co.uk/software/pyqt/download
- ipython: http://ipython.scipy.org/moin/
- mayavi2: http://code.enthought.com/projects/mayavi/ 3.3.1 (or better)
- matplotlib: http://matplotlib.sourceforge.net/


and of course NEURON_. compiled with python support

.. _NEURON: http://www.neuron.yale.edu/neuron/

Ubuntu and friends
==================

On Ubuntu you can easily install all the requirements using apt-get with::

    sudo apt-get install python-qt4 ipython python-matplotlib

If you are running a different flavour of GNU/Linux, like Fedora for example, just install 
the requirements with your package manager, then go to the `Package Install`_.

Mayavi 
======

If you have pip_ installed you can install Mayavi just running::

    pip install "Mayavi[app]"
    
if you prefer easy_install just run::

    easy_install "Mayavi[app]"
    
If you want to use another method for installation look at the `Mayavi doc`_

.. _Mayavi doc: http://code.enthought.com/projects/mayavi/docs/development/html/mayavi/installation.html

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

.. mayavi doc: http://code.enthought.com/projects/mayavi/docs/development/html/mayavi/installation.html

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

Running the bleeding edge
-------------------------

If you want to run the latest code you can clone the git repo and run the software from there::

    git clone git://github.com/mattions/neuronvisio.git neuronvisio

then you need to add the directory (the absolute path) to your PYTHONPATH (in bash)::
    
    export PYTHONPATH=$PYTHONPATH:/path-to-neuronvisio
    
Legacy releases
===============

You can find all the old Neuronvisio releases on `github repo`_ Note there was a major
rewriting of the software from series 0.3 to 0.4 and the use of the old releases is not 
encouraged. 

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


