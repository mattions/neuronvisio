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

from neuron import h
h.load_file("stdrun.hoc")

# Visio

from visio2 import Visio
import manager

class Controls():
    """Main class Neuronvisio"""
    def __init__(self):
        app = QtGui.QApplication.instance()
        # Loading the UI
        self.ui = uic.loadUi(os.path.join(os.path.dirname(__file__),
                                                "neuronvisio.ui"))
        
        # Connecting
        self.ui.Plot3D.connect(self.ui.Plot3D, 
                                     QtCore.SIGNAL('clicked()'), self.launch_visio)
        self.ui.plot_vector_btn.connect(self.ui.plot_vector_btn,
                                         QtCore.SIGNAL('clicked()'), self.plot_vector)
        
        self.ui.def_col_btn.setColor(QtGui.QColor(255.,255.,255.))
        self.ui.sel_col_btn.setColor(QtGui.QColor(0.,0.,255.))
        self.ui.init_btn.connect(self.ui.init_btn, 
                                 QtCore.SIGNAL('clicked()'), self.init)
        self.ui.run_btn.connect(self.ui.run_btn, 
                                QtCore.SIGNAL('clicked()'), self.run)
        self.ui.dtSpinBox.connect(self.ui.dtSpinBox, 
                                  QtCore.SIGNAL('valueChanged(double)'), 
                                  self.dt_changed)
        self.ui.tstopSpinBox.connect(self.ui.tstopSpinBox, 
                                     QtCore.SIGNAL('valueChanged(double)'), 
                                     self.tstop_changed)
        self.ui.vSpinBox.connect(self.ui.vSpinBox, 
                                 QtCore.SIGNAL('valueChanged(double)'), 
                                     self.v_changed)
        self.ui.create_vector.connect(self.ui.create_vector,
                                      QtCore.SIGNAL('clicked()'), 
                                      self.create_vector)
        self.ui.actionAbout.connect(self.ui.actionAbout,
                                      QtCore.SIGNAL('triggered()'), 
                                      self.about)
        
        ### Connection with the console
        spinBoxDic = {'dt' : self.ui.dtSpinBox, 'tstop' : self.ui.tstopSpinBox,
                      'v_init' : self.ui.vSpinBox}
        self.timeLoop = Timeloop(spinBoxDic)
        self.timeLoop.start()
        
        
        ### Manager class 
        self.manager = manager.Manager()
                            
        self.ui.show()
        
        # Start the main event loop.
        app.exec_()
        
    def launch_visio(self):
        if not hasattr(self, 'visio'):
            self.visio = Visio()
            self.visio.draw_model(self.ui.def_col_btn.color)
            self.ui.def_col_btn.connect(self.ui.def_col_btn,
                                        QtCore.SIGNAL("colorChanged(QColor)"),
                                        self.visio.draw_model)
    
    def init(self):
        """Set the vm_init from the spin button and prepare the simulator"""
        
        v_init = self.ui.vSpinBox.value()
        
        # Set the v_init
        h.v_init = v_init
        h.finitialize(v_init)
        h.fcurrent()
        
        # Reset the time in the GUI
        self.ui.time_label.setNum(h.t)
    
    def run(self):
        """Run the simulator till tstop"""
        
        #Initializing
        self.init()
        # Run
        while h.t < h.tstop:
            h.fadvance()
            
            self.ui.time_label.setText("<b>" + str(h.t) + "</b>")
            
    def tstop_changed(self):
        
        h.tstop = self.ui.tstopSpinBox.value()
        
        
    def dt_changed(self):
        
        h.dt = self.ui.dtSpinBox.value()
    
    def v_changed(self):
        
        h.v_init = self.ui.vSpinBox.value()
    
    def plot_vector(self):
        
        items = self.ui.treeWidget.selectedItems()
        vecs_to_plot = {}
        var = ""
        for item in items:
            if item.parent() is None:
                print "Can't plot the section, skipping."
            else:
                sectionName = item.parent().text(0) #Column used
                var = item.text(0)
                
                sectionName = str(sectionName) # This will go with Py3
                var = str(var) #idem
                for vecRef in self.manager.vecRefs:
                    
                    if vecRef.sec_name == sectionName:
                        # get the vec
                        vec = vecRef.vecs[var]
                        key = sectionName + "_" + var
                        vecs_to_plot[key] = vec
        
        # Plot legend if required
        legend_status = self.ui.legend.isChecked() #return True if toggled.
        
        # Retrieve the fig num
        fig_num = self.ui.fig_num_spinBox.value()
        
        self.manager.plotVecs(vecs_to_plot, legend=legend_status, 
                              figure_num=fig_num)
    def create_vector(self):
        
        var = self.ui.var.text()
        allCreated = self.manager.add_all_vecRef(str(var))
        self._update_tree_view()
        
    def _update_tree_view(self):
        # Fill the treeview wit all the vectors created
        #Clear all the row
        self.ui.treeWidget.clear()
        
        # Add all the vectors
        for vecRef in self.manager.vecRefs:
            sec_name = vecRef.sec_name
            sec_root_item = QtGui.QTreeWidgetItem(self.ui.treeWidget)
            sec_root_item.setText(0, sec_name) 
            for var,vec in vecRef.vecs.iteritems():
                item = QtGui.QTreeWidgetItem(sec_root_item)
                item.setText(0, var)
                sec_root_item.addChild(item)
    
    def get_info(self, section):
        """Get the info of the given section"""
        
        info = "Name: %s\n" %section.name()
        info += "L: %f\n" % section.L
        info += "diam: %f\n" % section.diam
        info += "cm: %f\n" % section.cm
        info += "Ra: %f\n" % section.Ra
        info += "nseg: %f\n" % section.nseg
        return info
    
    def about(self):
        
        self.aboutUi = uic.loadUi(os.path.join(os.path.dirname(__file__),
                                                "qtAbout.ui"))
        import neuronvisio
        name = '<font size=32><b>Neuronvisio %s<b><font>' %neuronvisio.__version__
        authors = '%s' %neuronvisio.__authors__
        
        self.aboutUi.name.setText(name)
        self.aboutUi.authors.setText(authors)
        
        self.aboutUi.show()
        
        
class Timeloop(QtCore.QThread):
    """Daemon thread to connect the console with the gui"""
    def __init__(self, spinBoxDict, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.spinBoxDict = spinBoxDict
        
        
    def run(self):
        """Update the gui interface"""
        while True:
            self.sleep(1) #check every sec
            
            if h.dt != self.spinBoxDict['dt'].value():
                self.spinBoxDict['dt'].setValue(h.dt)
            if h.tstop != self.spinBoxDict['tstop'].value():
                self.spinBoxDict['tstop'].setValue(h.tstop)
            if h.v_init != self.spinBoxDict['v_init'].value():
                self.spinBoxDict['v_init'].setValue(h.v_init)
            
            