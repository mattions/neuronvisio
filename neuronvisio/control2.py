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
import sys
sys.path.append(os.path.dirname(__file__)) 

from PyQt4 import QtGui, QtCore, uic

# Pylab
import numpy as np
import matplotlib
matplotlib.use("Qt4Agg")
matplotlib.interactive(True)
import matplotlib.pyplot as plt

from neuron import h

# Visio

from visio2 import Visio


class Controls():
    """Main class Neuronvisio"""
    def __init__(self):
        app = QtGui.QApplication.instance()
        # Loading the UI
        self.main_win = uic.loadUi(os.path.join(os.path.dirname(__file__),
                                                "neuronvisio.ui"))
        
        # Connecting
        self.main_win.Plot3D.connect(self.main_win.Plot3D, 
                                     QtCore.SIGNAL('clicked()'), self.launch_visio)
        self.main_win.pylab_test.connect(self.main_win.pylab_test,
                                         QtCore.SIGNAL('clicked()'), self.plot_x)
        self.main_win.show()
        
        # Start the main event loop.
        app.exec_()
        
    def launch_visio(self):
        if not hasattr(self, 'visio'):
            self.visio = Visio()
            self.visio.draw_model(self.main_win.defaultSec_colorButton.color)
    
    def plot_x(self):
        
        fig = plt.figure()
        x = np.linspace(0,10)
        plt.plot(x, np.sin(x))
     
if __name__ == "__main__":
    ctl = Control()
