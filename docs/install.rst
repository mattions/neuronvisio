.. _install:

*******
Install
*******

Requirements
============

To install NeuronVisio you need to satisfy the following dependencies

- pygtk: http://www.pygtk.org/
- visual: http://vpython.org/
- matplotlib: http://matplotlib.sourceforge.net/


and of course NEURON_.

.. _NEURON: http://www.neuron.yale.edu/neuron/

Ubuntu and friends
==================

On Ubuntu you can easily install all the requirements using apt-get with::

    sudo apt-get install python-numpy python-gtk2 python-visual python-matplotlib

and then add the `Neuronvisio PPA`_ on launchpad adding the repositories::
    
    deb http://ppa.launchpad.net/mattions/neuronvisio/ubuntu karmic main 
    deb-src http://ppa.launchpad.net/mattions/neuronvisio/ubuntu karmic main

adding the key::
    
    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 4B2C6C7E
    
updating and installing::
    
    sudo update
    sudo install neuronvisio     
    
.. _Neuronvisio PPA: https://launchpad.net/~mattions/+archive/neuronvisio

If you are running a different flavour of GNU/Linux, like Fedora for example, just install the requirements 
with your package manager, then go to the `Package Install`.

Mac OS X
========

You need to install the requirements by yourself, because there is no package manager 
able to do it for you. I suggest you to get an `Ubuntu`_. Anyway, for the brave, I'll give here 
some links to make this work easier for you:

- `GTK for MAC`_ : this is the GTK port for MAC
- `Visual for MAC`_ : there is a dedicated installer
- `Matplotlib for MAC`_ : Install the superpack and you will get Numpy, Scipy, and matplotlib.

.. _Ubuntu: http://www.ubuntu.com/
.. _GTK for MAC: http://gtk-osx.sourceforge.net/
.. _Visual for MAC: http://vpython.org/OSX_download.html
.. _Matplotlib for MAC: http://macinscience.org/?page_id=6 

If you have all this stuff installed then proceed to the `Package Install`_.

Windows
=======

Seriously? As for Mac, you need to install the requirements by yourself, because there is no package manager 
able to do it for you. It can be done but it's really painful. I suggest you to get an `Ubuntu`_. 
Anyway, for the brave:


- `PyGTK stack`_: To get this working you need to build the GTK, libglade, and PyGTK and install python
- `Visual Python`_: You can install the visual package with the install
- `Matplot and numpy`_: You need to compile everything.

.. _Ubuntu: http://www.ubuntu.com/
.. _PyGTK stack: http://faq.pygtk.org/index.py?file=faq21.002.htp&req=show
.. _Visual Python: http://vpython.org/win_download25.html
.. _Matplot and numpy: http://www.scipy.org/Installing_SciPy/Windows

If you have all this stuff installed then proceed to the `Package Install`_.

Package Install
===============

If you have `pip`_ installed and all the requirements are already met you can install neuronvisio and a really handy way::

    pip install neuronvisio

Without pip, if you met all the requirements it's still pretty easy. Download the lates neuronvisio.tgz file 
from `Neuronvisio's PyPI page`_, untar it and run::

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


