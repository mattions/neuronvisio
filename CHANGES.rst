0.8.6 -- 8 March 2013
=====================

- we are using pip and requirements.txt to be able to install packages from DCVS
- MacOs is now supported when we open the model, if not mosinit is present #56
- Better explanation to the User if a model can't be loaded. #55
- Improved Install Docs for Mac. PR #53 and #54
- Added 24 models available from ModelDB


0.8.5 -- 6 Jul 2012
===================

- Closed #49
- Text in the Animation is always formatted with 3 digits.
- Added the ability to load a NeuroML (xml), a Hoc (.hoc) or a HDF file (.h5)  
  with Neuronvisio format directly when the program is launched. 

0.8.4 -- 12 Jun 2012
====================

- Added new model to the ModelDBlist
- updated the documentation
- Added 3 new models to ModelDB

0.8.3 -- 18 May 2012 
====================

- Fixed paver minilib, missing from the tarball
- Added one new model to the ModelDB.xml
- Improved the documentation of several classes
- Inserted the domain in the about (neuronvisio.org)

0.8.2 -- 23 Apr 2012
====================

- Added two new model to ModelDB.xml
- Introduced a new method to assign a color to more than one sections from 
  the console
- Added the apptools patched version as explicit dependency until it's not
  released officially.

0.8.1 -- 19 March 2012
======================

- Added new models on the ModelDB.xml
- Closed #45
- Easy function to export a video as a stack of screenshots
- Updated the docs to work witht the latest pyqt
- Geometry node in the HDF is directly a NeuroML string 
  and not wrapped in a list 

0.8.0 -- 15 Feb 2012
====================

- New repo layout
- Ported to Mayavi 4.1.1.dev
- Closed #31
- Reorganized controls method in alphabetical order.
- Animation set true when simulation is launched.
- Fixed a vectors handling if no values present.
- Updated the doc for Mayavi 4.0.0
- Load hoc or hdf with the same method
- Added new models from ModelDB
- User Interface improvement
- Closed #37
- Closed #32
- Closed #34
- Improved nrnvisio.py to integrate seamlessy with IPython session, 
  or create a new one on the fly
- Automatic handling of Mayavi installation through pip.

0.7.3 -- 24 Nov 2011  
====================

- Inserted how to configure ipython with the pylab and Q4Agg support in the doc
- Selected section is now stored and used if the vector are created only for one sec
- Inserted two new models on the ModelDb.xml. Fix #30.
- Included the ModelDB.xml in the package

0.7.2 -- 8 Nov 2011
===================

- Inserted modeldb in the pavement.

0.7.1 -- 8 Nov 2011
===================

- fixed the name of the exectable on the setup file

0.7.0 -- 3 Nov 2011
===================

- Added a new tab to have a ModelDb explorer inside Neuronvisio 
- Integrate the ability to download and extract a NEURON model from ModelDb
- Ability to load the model directly from Neuronvisio
- Used the logging python system through the package
- Updated the docs to explain the ModelDb integration. 


0.6.2 -- 16 Jun 2011
====================

- New API to select sections directly from the commandline 
  (`controls.select_sections()`)
- Animation Timeliner set up only if simulation has ran or be 
  reloaded.


0.6.1 -- 9 Jun 2011
===================

- Animation ported to the new infrastructure.
- Updated the requirements with setuptools (needed for paver)
- Animation timeline accept an arbitrary time and display it on the 
  visio window.

0.6.0 -- 10 May 2011
====================

- Added the function to plot a 3D plot to the manager (manager.plot3D)
- Animation can will be enabled if any simulation is ran, either from the gui 
  or the code.
- Completely rewrote the visualization method. Now completely integrates in the mayavi pipelines, 
  therefore axes and other modules/filters can be added at will
- Now it's faster. A lot faster
- All the segments are plotted, not only the section. This is extremely helpful with geometrical reconstruct 
  neurons and networks.
- Updated the docs and the screenshots.

0.5.2 -- 26 Jan 2011
====================

- Updated the version recall to GitPython 0.3.1 (used only if present!)
- HocVector into NumpyArray for saving with swap in place, to reduce overhead
- Restructured the package for an easier installation
- Added the possibility to build documentation offline


0.5.1 - 23 Nov 2010
===================

- Fixed the picking of the cylinder. Possible to select a cylinder 
  clicking anywhere.
- Possibility to plot points instead of a lines
- BaseREf class are discriminated through the group id and not any more on
  class base.


0.5.0 - 19 Jun 2010
===================

- Closed #16
- Fixed some typos on the docs
- Mechanisms are shown on the info tab
- Refactored code for extensibility
- Storage moved to a hdf file.
- Extensibility to other kind of variables, not only vectors

0.4.4 - 1 Apr 2010
==================

- Fixed the name on the README
- Treeview updated everytime a database is loaded.


0.4.3 - 2 Mar 2010
==================

- Info sections updated
- Update the docs and website


0.4.2 - 18 Feb 2010
===================

- Added simulation saving abilities.
- Updated the doc


0.4.1 - 28 Jan 2010
========================

- Closed #13
- Introduced a tab to retrieve info on the section

0.4.0 - 19 Jan 2010
========================

- Remplemented using Mayavi2 and Qt4 for better performance and better usability.
- Cleanup and refactoring of the code.
- Closed #11, #12, #15

0.3.5 - 20 Nov 2009 
===================

- Using sphinx for the doc
- Using paver for deployment
- python egg and easy install support
- User manuel available in pdf format


0.3.4 - 15 Sep 2009
===================

- Changed the way the module is imported to allow other program to use the manager 
  as a storing objects for results.

0.3.3 - 3 Sep 2009
==================

- Integrated the pylab interface using the GTK backend provided by pylab. 
  It is possible to zoom and navigate the graph with the pylab tools.
- It is now possible to decide in which figure to plot, using the current figure selector.

0.3.22 - 31 Jul 2009
====================

- Closed bug #10
- Changed the name of the module from nrnVisio to nrnvisio to be python
  standard compliant.
- Manager being transformed into a library (WIP)

0.3.21 - 20 Jul 2009
====================

- Better handling of the pick section routine
- Changed the examples to use the create statement for hoc, to have 
  a proper name of the section also in python.
- Modified the GUI to handle a runtime change of a section. The model is redrawn
  completely, the zoom is conserved.

0.3.2 - 20 Jul 2009
===================

Bug Release. Closed Bug #9

0.3.1 - 18 Jul 2009
===================

Bug Release.

0.3.0 - 14 Jul 2009
===================

New Features
------------

- Stop Button on the animation Control
- Better handling on the timeline updating routine.

BUGFixes
--------

- Closed bug #8
- Closed bug #3


0.2.0 - 6 Jul 2009
==================

New Features
------------

Some new features has been introduced:

- User defined color. The user can now change the colors of the model for a better contrast.
- Info tab. Reports the properties of the selected section.

BUGFixes
--------

- Closed bug #4
- Closed bug #5
- Closed bug #6



0.1.0 - 30 Jun 2009
===================

Fist public release.
 
Features
--------

- 3D visualization of the model with the possibility to change it runtime
- Creation of vectors to record any variable present in the section
- Pylab integration to plot directly the result of the simulation
- Explore of the timecourse of any variable among time using a color coded scale in the 3d representation
- the GUI runs in its own thread so it's possible to use the console to modify/interact with the model.
