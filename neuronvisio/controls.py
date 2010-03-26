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

from visio import Visio
import manager
import res # icons

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
        self.ui.animation_btn.connect(self.ui.animation_btn,
                                      QtCore.SIGNAL('clicked()'),
                                      self.animation)
        self.a_ui = uic.loadUi(os.path.join(os.path.dirname(__file__),
                                                "animation.ui"))
        self.a_ui.view.connect(self.a_ui.view, QtCore.SIGNAL('changed()'),
                               self.draw_gradient)
        self.a_ui.starting_color_btn.connect(self.a_ui.starting_color_btn,
                                        QtCore.SIGNAL("colorChanged(QColor)"),
                                        self.draw_gradient)
        self.a_ui.ending_color_btn.connect(self.a_ui.ending_color_btn,
                                QtCore.SIGNAL("colorChanged(QColor)"),
                                self.draw_gradient)
        self.a_ui.timelineSlider.connect(self.a_ui.timelineSlider,
                                         QtCore.SIGNAL("valueChanged(int)"),
                                         self.on_timeline_value_changed)
        
        self.ui.actionLoad.connect(self.ui.actionLoad, 
                                   QtCore.SIGNAL("triggered()"),
                                   self.load_db)
        self.ui.actionSave.connect(self.ui.actionSave,
                                   QtCore.SIGNAL("triggered()"),
                                   self.save_db)
        self.ui.actionSave_As.connect(self.ui.actionSave_As,
                                      QtCore.SIGNAL("triggered()"),
                                      self.save_as_db)
        
        ### Connection with the console
        widgetDic = {'dt' : self.ui.dtSpinBox, 'tstop' : self.ui.tstopSpinBox,
                      'v_init' : self.ui.vSpinBox, 'time_label' : self.ui.time_label}
        self.timeLoop = Timeloop(widgetDic)
        self.timeLoop.start()
        
        
        ### Manager class 
        self.manager = manager.Manager()
        self.path_to_sql = None                    
        self.ui.show()
        
        # Constant for the Treeview
        self.Vectors_Group_Label = "Vectors"
        self.SynVectors_Group_Label = "SynVectors"
        
        # Start the main event loop.
        app.exec_()
    
    def load_db(self, path_to_sql=None):
        
        if path_to_sql == None:
            filename = QtGui.QFileDialog.getOpenFileName()
            self.path_to_sql = str(filename)
        else:
            self.path_to_sql=path_to_sql
        self.manager.load_db(self.path_to_sql)
        self.update_tree_view()
        msg = "Loaded db: %s" % self.path_to_sql
        self.ui.statusbar.showMessage(msg, 3500)
        # Enablig the Animation button
        self.ui.animation_btn.setEnabled(True)
        
        
        
    def save_db(self):
        if not self.path_to_sql:
            filename = QtGui.QFileDialog.getSaveFileName()
            self.path_to_sql = str(filename) # It will go with python 3
        self.manager.store_in_db(self.path_to_sql)
        msg = "Saved Loaded db: %s" % self.path_to_sql
        self.ui.statusbar.showMessage(msg, 3500)
        
    def save_as_db(self):

        filename = QtGui.QFileDialog.getSaveFileName()
        self.path_to_sql = str(filename)
        self.manager.store_in_db(self.path_to_sql)
        msg = "Saved Loaded db: %s" % self.path_to_sql
        self.ui.statusbar.showMessage(msg, 3500)
            
        

        
    def launch_visio(self):
        msg = "Plotting..."
        self.ui.statusbar.showMessage(msg, 3500)
        if not hasattr(self, 'visio'):
            self.visio = Visio(self.ui.def_col_btn.color, self.ui.sel_col_btn.color,
                               self.ui.sec_info_label)
            self.visio.draw_model()
            self.ui.def_col_btn.connect(self.ui.def_col_btn,
                                        QtCore.SIGNAL("colorChanged(QColor)"),
                                        self.visio.draw_model)
            self.ui.sel_col_btn.connect(self.ui.sel_col_btn,
                                        QtCore.SIGNAL("colorChanged(QColor)"),
                                        self.visio.update_selected_sec)
            self.ui.selected_section.setEnabled(True)
        else:
            #Raise the visio window
            self.visio.container.show()
        
    
    def init(self):
        """Set the vm_init from the spin button and prepare the simulator"""
        
        if len(self.manager.vecRefs) == 0:
            print "No vector Created. Create at least one vector to run the simulation"
            return False
        else:
            v_init = self.ui.vSpinBox.value()
            # Set the v_init
            h.v_init = v_init
            h.finitialize(v_init)
            h.fcurrent()
        
            # Reset the time in the GUI
            self.ui.time_label.setNum(h.t)
            return True
            
    
    def run(self):
        """Run the simulator till tstop"""
        
        #Initializing
        if self.init():
            # Run
            msg = "Running simulation. It will take a while maybe..."
            self.ui.statusbar.showMessage(msg, 5000)
            while h.t < h.tstop:
                h.fadvance()
                
                self.ui.time_label.setText("<b>" + str(h.t) + "</b>")
            # Enabling the animation
            self.ui.animation_btn.setEnabled(True)
                    
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
            if item.childCount() == 0: # Leaf, so it is the variable to plot
                
                sectionItem = item.parent()
                sectionName = sectionItem.text(0) #Column used
                var = item.text(0)
                
                sectionName = str(sectionName) # This will go with Py3
                var = str(var) #idem
                
                group = str(sectionItem.parent().text(0))
                if group == self.Vectors_Group_Label:
                    for vecRef in self.manager.vecRefs: # TODO: Change the 
                        
                        if vecRef.sec_name == sectionName:
                            # get the vec
                            vec = vecRef.vecs[var]
                            key = sectionName + "_" + var
                            vecs_to_plot[key] = vec
                            
                if group == self.SynVectors_Group_Label:
                    for synVecRef in self.manager.synVecRefs:
                        if synVecRef.sec_name == sectionName:
                            vec = synVecRef.syn_vecs[var]
                            chan_type = synVecRef.chan_type
                            key = sectionName + '_' + var + "_" + chan_type 
                            vecs_to_plot[key] = vec
        # Plot legend if required
        legend_status = self.ui.legend.isChecked() #return True if toggled.
        
        # Retrieve the fig num
        fig_num = self.ui.fig_num_spinBox.value()
        
        self.manager.plotVecs(vecs_to_plot, legend=legend_status, 
                              figure_num=fig_num)
    def create_vector(self):
        
        var = self.ui.var.text()
        if var.isEmpty():

            msgBox = QtGui.QMessageBox()
            msgBox.setText("No var specified.")
            msgBox.setIcon(QtGui.QMessageBox.Warning)
            msgBox.exec_()
 
        else:
            if self.ui.all_sections.isChecked():
                allCreated = self.manager.add_all_vecRef(str(var))
            elif self.ui.selected_section.isChecked():
                if self.visio.selected_cyl is not None:
                    sec = self.visio.cyl2sec[self.visio.selected_cyl]
                    self.manager.add_vecRef(str(var), sec)
                else:
                    msgBox = QtGui.QMessageBox()
                    msgBox.setText("<b>No vector has been created.</b>")
                    msg = "You need to select the section where you want to create the vector"
                    msgBox.setInformativeText(msg)
                    msgBox.setIcon(QtGui.QMessageBox.Warning)
                    msgBox.exec_()
        self.update_tree_view()
    
    def insert_vectors_treeview(self):
        """Adding the vectors To the treeview"""
        # Add all the vectors
        root_item = QtGui.QTreeWidgetItem(self.ui.treeWidget)
        root_item.setText(0, self.Vectors_Group_Label)
        for vecRef in self.manager.vecRefs:
            sec_name = vecRef.sec_name
            sec_root_item = QtGui.QTreeWidgetItem(root_item)
            sec_root_item.setText(0, sec_name)
            for var,vec in vecRef.vecs.iteritems():
                item = QtGui.QTreeWidgetItem(sec_root_item)
                item.setText(0, var)
                sec_root_item.addChild(item)
                
    def insert_synvectors_treeview(self):
        """Insert the synVectors"""
        root_item = QtGui.QTreeWidgetItem(self.ui.treeWidget)
        root_item.setText(0, self.SynVectors_Group_Label)
        # Order the synVecRef for section
        
        for synVecRef in self.manager.synVecRefs:
            sec_name = synVecRef.sec_name
            
            target_item = None 
            children = root_item.childCount()
            
            # Search for if the section is already inserted.
            for child in range (children):
                item = root_item.child(child)
                if item.text(0) == sec_name:
                    target_item = item
                    break
            
            if target_item is None: # Create the item if not present
                sec_root_item = QtGui.QTreeWidgetItem(root_item)
                sec_root_item.setText(0, sec_name)
                target_item = sec_root_item
                
            for var,vec in synVecRef.syn_vecs.iteritems():
                child_item = QtGui.QTreeWidgetItem(sec_root_item)
                child_item.setText(0, var)
                child_item.setText(1, synVecRef.chan_type)
                target_item.addChild(child_item)
            
                        
    def update_tree_view(self):
        # Fill the treeview wit all the vectors created
        #Clear all the row
        self.ui.treeWidget.clear()
        
        self.insert_vectors_treeview()
        
        if hasattr(self.manager, 'synVecRefs'):
            
#            iterator = QtGui.QTreeWidgetItemIterator(self.ui.treeWidget)
#            item = iterator.value()
#            while(item):
            self.insert_synvectors_treeview()
            
                
            # for all the row in treeview
                # for all the synVecRef
    
    def animation(self):
        
        self.a_ui.timelineSlider.setRange(0, len (self.manager.t))
        self.draw_gradient()
        self.a_ui.show()
    
    def draw_gradient(self):
        
        x = self.a_ui.view.x()
        y = self.a_ui.view.y()
        h = self.a_ui.view.height()
        w = self.a_ui.view.width()
        
        gradient = QtGui.QLinearGradient(x, y/2, x+w, y/2)
        gradient.setColorAt(0.0, self.a_ui.starting_color_btn.color)
        gradient.setColorAt(1.0, self.a_ui.ending_color_btn.color)
        brush = QtGui.QBrush(gradient)
        scene = QtGui.QGraphicsScene()
        scene.setSceneRect(x,y,w,h)    
        
        # Rect fills all the graphicview
        rect = QtGui.QGraphicsRectItem(x, y, w, h) 
        rect.setBrush(brush)
        scene.addItem(rect)
        
        #scene.addText("Hello")
        self.a_ui.view.setScene(scene)
        self.a_ui.view.show()
        
    def on_timeline_value_changed(self):
        """Draw the animation according to the value of the timeline"""
        
        # cast to int from str
        time_point_indx = self.a_ui.timelineSlider.value()
        
        

        var = self.a_ui.varToShow.text()
        var = str(var) # This will go with Py3
#        
#        #Update the label on the scale
        
        if len (self.manager.t) == time_point_indx:
            time_point_indx = time_point_indx - 1 # Avoid to go out of scale
        time = self.manager.t[time_point_indx]
        self.a_ui.animationTime.setText(str(time))
        
        
        start_value = float(self.a_ui.startValue.text())
        end_value = float(self.a_ui.endValue.text())

        start_col = self.a_ui.starting_color_btn.color
        end_col = self.a_ui.ending_color_btn.color
        self.visio.show_variable_timecourse(var, time_point_indx, start_value, 
                                            start_col, 
                                            end_value, 
                                            end_col, 
                                            self.manager.vecRefs)
    
    def about(self):
        
        self.aboutUi = uic.loadUi(os.path.join(os.path.dirname(__file__),
                                                "qtAbout.ui"))
        import neuronvisio
        name = '<font size=24><b>Neuronvisio %s<b><font>' %neuronvisio.__version__
        authors = '%s' %neuronvisio.__authors__
        
        self.aboutUi.name.setText(name)
        self.aboutUi.authors.setText(authors)    
        self.aboutUi.show()
    
    def on_def_col_btn_changed(self):
        
        self.visio.default_cyl_col = self.ui.def_col_btn.color
    
    def on_sel_col_btn_changed(self):
        
        self.visio.selected_cyl_col = self.ui.sel_col_btn.color
        
class Timeloop(QtCore.QThread):
    """Daemon thread to connect the console with the gui"""
    def __init__(self, widgetDic, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.widgetDic = widgetDic
        
        
    def run(self):
        """Update the gui interface"""
        while True:
            self.sleep(1) #check every sec
            
            if h.dt != self.widgetDic['dt'].value():
                self.widgetDic['dt'].setValue(h.dt)
            if h.tstop != self.widgetDic['tstop'].value():
                self.widgetDic['tstop'].setValue(h.tstop)
            if h.v_init != self.widgetDic['v_init'].value():
                self.widgetDic['v_init'].setValue(h.v_init)
#            if h.t != float (self.widgetDic['time_label'].text()):
#                self.widgetDic['time_label'].setText(str(h.t))
            
                
            
            