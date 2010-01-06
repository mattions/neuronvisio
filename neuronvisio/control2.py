# * Copyright (C) Tue Jan  5 10:10:19 GMT 2010 - Michele Mattioni:
# *  
# * This file is part of NeuronVisio
# * 
# * NeuronVisio is free software: you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation, either version 3 of the License, or
# * (at your option) any later version.
#
# * NeuronVisio is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
#
# * You should have received a copy of the GNU General Public License
# * along with NeuronVisio.  If not, see <http://www.gnu.org/licenses/>.

#@PydevCodeAnalysisIgnoren 
import os
os.environ['ETS_TOOLKIT'] = 'qt4'

from PyQt4 import QtGui, QtCore, uic

from enthought.mayavi import mlab
from enthought.tvtk.tools import visual

from neuron import h


# Testing pylab here
import numpy as np
import matplotlib
matplotlib.use("Qt4Agg")
matplotlib.interactive(True)
import matplotlib.pyplot as plt

class Control():
    """Main class Neuronvisio"""
    def __init__(self):
        app = QtGui.QApplication.instance()
        # Loading the UI
        self.main_win = uic.loadUi("neuronvisio.ui")
        self.main_win.Plot3D.connect(self.main_win.Plot3D, 
                                     QtCore.SIGNAL('clicked()'), self.launch_mayavi)
        self.main_win.pylab_test.connect(self.main_win.pylab_test,
                                         QtCore.SIGNAL('clicked()'), self.plot_x)
        self.main_win.show()
        self.mayavi_started = False
        
        # Start the main event loop.
        app.exec_()
        
    def launch_mayavi(self):
        self.visio = Visio()
        if self.mayavi_started is False:     
            self.mayavi_fig = mlab.figure(size=(500,500))
            # Tell visual to use this as the viewer.
            visual.set_viewer(self.mayavi_fig)
        self.plotCyl()
        
        
    def plotCyl(self):
        
        cyl = visual.Cylinder(pos=(0.,0.,0.), radius=8, length=10)
        cyl2 = visual.Cylinder(pos=(8.,0.,0.,), axis=(0.,4.,5.), radius=4, length=13)
        cyl3 = visual.Cylinder(pos=(-4.,0.,0.))
    
    def plot_x(self):
        
        fig = plt.figure()
        x = np.linspace(0,10)
        plt.plot(x, np.sin(x))
     
if __name__ == "__main__":
    ctl = Control()
