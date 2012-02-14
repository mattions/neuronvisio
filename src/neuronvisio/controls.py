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
from pyface.qt import QtGui, QtCore 
from PyQt4 import uic

from subprocess import call
from manager import SynVecRef
os.environ['ETS_TOOLKIT'] = 'qt4'


import logging
FORMAT = '%(levelname)s %(name)s %(lineno)s   %(message)s'
if os.environ.has_key('DEBUG'):
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
else: 
    logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)

import sys
sys.path.append(os.path.dirname(__file__)) 

if os.name != 'nt':
    from PyQt4 import QtGui, QtCore, uic

from PyQt4.QtCore import Qt
import numpy as np

import matplotlib as mpl
if mpl.backends.backend is None: 
    mpl.use('Qt4Agg')
mpl.interactive(True)

from neuron import h
h.load_file("stdrun.hoc")

# Visio

from visio import Visio
import manager
import res # icons

# ModelDb
from modeldb.ModelDB import Models

class Controls(object):
    """Main class Neuronvisio"""
    def __init__(self):
        app = QtGui.QApplication.instance()
        self.ui_dir = 'ui'
        # Loading the UI
        self.ui = uic.loadUi(os.path.join(os.path.dirname(__file__), 
                                          self.ui_dir,
                                          "neuronvisio.ui"))
        
        # Connecting
        self.ui.Plot3D.connect(self.ui.Plot3D, 
                                     QtCore.SIGNAL('clicked()'), self.launch_visio)
        self.ui.plot_vector_btn.connect(self.ui.plot_vector_btn,
                                         QtCore.SIGNAL('clicked()'), self.plot_vector)
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
        self.ui.timelineSlider.connect(self.ui.timelineSlider,
                                         QtCore.SIGNAL("valueChanged(int)"),
                                         self.on_timeline_value_changed)
        self.ui.animationTime.connect(self.ui.animationTime,
                                      QtCore.SIGNAL('returnPressed()'),
                                      self.on_animation_time_return_pressed)
        self.ui.actionLoad.connect(self.ui.actionLoad, 
                                   QtCore.SIGNAL("triggered()"),
                                   self.load)
        self.ui.actionSave.connect(self.ui.actionSave,
                                   QtCore.SIGNAL("triggered()"),
                                   self.save_hdf)
        self.ui.tabWidget.connect(self.ui.tabWidget, 
                                  QtCore.SIGNAL('currentChanged(int)'),
                                  self.populate_treeview_model)
        self.ui.tree_models.connect(self.ui.tree_models, 
                                    QtCore.SIGNAL('itemSelectionChanged ()'),
                                    self.select_model_treeview)
        self.ui.load_model_btn.connect(self.ui.load_model_btn, 
                                    QtCore.SIGNAL('clicked()'),
                                    self.load_selected_model)
        self.ui.load_model_btn.connect(self.ui.filter_list_btn, 
                                    QtCore.SIGNAL('clicked()'),
                                    self.filter_list)
        self.ui.filter_input.connect(self.ui.filter_input,
                                     QtCore.SIGNAL('returnPressed()'),
                                     self.filter_list)
        
        
        ### Connection with the console
        widgetDic = {'dt' : self.ui.dtSpinBox, 
                     'tstop' : self.ui.tstopSpinBox,
                     'v_init' : self.ui.vSpinBox, 
                     'time_label' : self.ui.time_label
                    }
        self.timeLoop = Timeloop(widgetDic)
        app.connect( self.timeLoop, QtCore.SIGNAL("updateDt(double)"), self.update_dt )
        app.connect( self.timeLoop, QtCore.SIGNAL("updateTstop(double)"), self.update_tstop )
        app.connect( self.timeLoop, QtCore.SIGNAL("updateVInit(double)"), self.update_v_init )
        self.timeLoop.start()
        
        
        ### Manager class 
        self.manager = manager.Manager()
        self.path_to_hdf = None
        self.visio = None
        self.tab_model_already_populated = False  
        self.ui.show()
        # Start the main event loop.
        #app.exec_()
        
        self.AUTHORS = 1
        self.YEAR = 0
        self.TITLE = 2
        self.ID = 3
        # Dictionary to hold the models class for the ModelDb integration
        self.models = Models()
        
    def populate_treeview_model(self, index, filter=""):
        """populate the tree view and the scroll_area when the tab is 
        activated"""
        if index == 3 and (filter or not self.tab_model_already_populated):
            self.ui.tree_models.clear()
            
            # Populating the treeview with the dictionary
            for model_name in self.models.get_model_names(filter):
                model = self.models.get_model(model_name)
                model_item = QtGui.QTreeWidgetItem(self.ui.tree_models, 'Models')
                model_item.setText(self.YEAR, model.get_year())
                model_item.setText(self.AUTHORS, model.get_authors())
                model_item.setText(self.TITLE, model.get_title())
                model_item.setData(self.ID, 0, model.get_id())
                self._set_tooltip(model, model_item)
            
                
            #Resizing the column.
            #self.ui.tree_models.resizeColumnToContents(0)
            self.ui.tree_models.resizeColumnToContents(self.YEAR)
            self.ui.tree_models.resizeColumnToContents(self.TITLE)
            self.ui.tree_models.resizeColumnToContents(self.ID)
            self.ui.textBrowser_readme.clear()
            self.ui.textBrowser_readme.insertPlainText("No model selected.")
            self.tab_model_already_populated = True #we populated only once.

    def _set_tooltip(self, model, model_item):
        # tooltip
        cols = self.ui.tree_models.columnCount()
        for i in range (cols):
            tooltip = model.get_tooltip()
            model_item.setToolTip(i, tooltip)

       
    def _retrieve_selected_model(self):
        "Return the model selected in the "
        items = self.ui.tree_models.selectedItems()
    
        if items:
            selected_item = items[0] #first element
            model_id = int(selected_item.text(self.ID))
            models_name = self.models.get_model_names()
            for name in models_name:
                mod = self.models.get_model(name)
                if model_id == mod.get_id():
                    return mod
        else:
            logging.info('No model selected!')
            return None
       
    def filter_list(self):
        "Filter the models list using the given text."
        filter = self.ui.filter_input.text()
        logger.debug("Filtering list using keyword '%s'" %(filter))
        self.populate_treeview_model(3, filter)

    def about(self):
        self.aboutUi = uic.loadUi(os.path.join(os.path.dirname(__file__),
                                               self.ui_dir,
                                               "qtAbout.ui"))
        import neuronvisio
        name = '<font size=24><b>Neuronvisio %s<b><font>' %neuronvisio.__version__
        authors = '%s' %neuronvisio.__authors__
        
        self.aboutUi.name.setText(name)
        self.aboutUi.authors.setText(authors)    
        self.aboutUi.show()
     
    def animation(self):
        self.ui.timelineSlider.setRange(0, len (self.manager.groups['t']))
        self.ui.timelineSlider.setEnabled(True)
        self.ui.show()
    
    def create_vector(self):
        var = self.ui.var.text()
        if not var:
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
    
    def dt_changed(self):
    
        h.dt = self.ui.dtSpinBox.value()
        

    def init(self):
        """Set the vm_init from the spin button and prepare the simulator"""
        
        if not self.manager.refs.has_key('VecRef') :
            message = "No vector Created. Create at least one vector to run the simulation"
            logger.info(message)
            self.ui.statusbar.showMessage(message, 3500)
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
            
    def insert_item_treeview(self, groupName, section_name, vecs, 
                             details = None):
        """Insert a new item in the treewidget. 
        Items are grouped by types. If a new type is provided a new group is added.
        Items are then grouped by section.
        In one section more than one variable is allowed.
        Each variable can have a detail associated in a dictionary form """
        group_root = self.get_unique_parent(groupName)
        sec_root = self.get_unique_parent(section_name, 
                                          parentItem = group_root)
        for var,vec in vecs.iteritems():
            item = ItemRef(sec_root, vec)
            item.setText(0, var)
            item.setText(1, details)    
            sec_root.addChild(item)
            
        
    def insert_refs_in_treeview(self):
        for group, ref_list in self.manager.refs.iteritems():
            for ref in ref_list:
                self.insert_item_treeview(group, 
                                          ref.sec_name, 
                                          ref.vecs, 
                                          ref.detail)
        
    def launch_visio(self):
        msg = "Plotting..."
        self.ui.statusbar.showMessage(msg, 3500)
        if self.visio == None:
            
            # Checking there are sections in the model.
            i = 0
            for sec in h.allsec():
                i += 1
            
            if i > 0:
                self.visio = Visio(self.ui.sec_info_label, self.manager)
                self.visio.draw_model()
                self.ui.selected_section.setEnabled(True)
            else:
                msg = """No model found, no section created. You need 
                to have at least one."""
                logger.warning(msg)
        else:
            #Raise the visio window
            self.visio.container.show()
        # Enabling the animation
        try:
            self.animation()
        except KeyError:
            # No simulation run an nothing loaded.
            # just pass
            pass

    def load(self, path_to_file=None):
        """General loading method. It loads either an hoc file or 
        a hdf5 file. The file type is recognised on the extension"""
        if path_to_file == None:
            filename = QtGui.QFileDialog.getOpenFileName()
            if filename:
                path_to_file = str(filename)
        
        base_name, file_extension = os.path.splitext(path_to_file)
        if (file_extension == '.hoc'):
            file_path, hoc_file = os.path.split(path_to_file)
            self.load_hoc_model(file_path, hoc_file)
        else:
            self.load_hdf(path_to_file)

    def load_hdf(self, path_to_hdf):
    
        if path_to_hdf != None:
            self.path_to_hdf=os.path.abspath(path_to_hdf)
            
            self.manager.load_from_hdf(self.path_to_hdf)
            self.update_tree_view()
            msg = "Loaded db: %s" % self.path_to_hdf
            self.ui.statusbar.showMessage(msg, 3500)
            # Enablig the Animation button
            self.animation()
            # Disabling all the rest
            self.ui.init_btn.setEnabled(False)
            self.ui.run_btn.setEnabled(False)
            self.ui.create_vector.setEnabled(False)

    def load_hoc_model(self, model_dir, hoc_file):
        """Load an hoc files. It compiles the mod 
        before loading the hoc."""
        try:
            os.path.isfile(os.path.join (model_dir, hoc_file))
        except IOError:
            logger.error("Not existing file: %s" %e.value)
            
        old_dir = os.path.abspath(os.getcwd())
        logger.info("Path changed to %s" %(os.path.abspath(model_dir)))
        if model_dir != '' :
            os.chdir(model_dir)
        try:
            # Add all mod files into current directory
            self.find_mod_files()
        
            # If windows
            if os.name == 'nt':                
                self.windows_compile_mod_files('.')
                from neuron import h
                h.nrn_load_dll('./nrnmech.dll')
            else: # Anything else.
                call(['nrnivmodl'])
                import neuron            
                neuron.load_mechanisms('.') # Auto loading. Not needed anymore.
            from neuron import gui # to not freeze neuron gui
            from neuron import h
            logger.info("Loading model in %s from %s"%(model_dir, hoc_file))
            h.load_file(hoc_file)
        except Exception as e:
            logger.warning("Error running model: " + e.message)
        logger.info("Path changed back to %s" %old_dir)
        os.chdir(old_dir)
        return True
                        
    def load_selected_model(self):
        "Load the model selected in the treeview."
                    
        mod = self._retrieve_selected_model()
        if mod:
            model_path = mod.download_model()
            # tooltip
            cols = self.ui.tree_models.columnCount()
            items = self.ui.tree_models.selectedItems()
            model_item = items[0]
            for i in range (cols):
                tooltip = mod.get_tooltip()
                model_item.setToolTip(i, tooltip)
            
            if os.path.exists(os.path.join(mod.get_dir(), 'mosinit.hoc')):
                self.load_hoc_model(mod.get_dir(), 'mosinit.hoc')
            else:
                path_info = "Could not locate a predefined mosinit.hoc. Can't automatically load the model. \
                Check the README for hints on which hoc to use and copy it to %s/mosinit.hoc" %model_path
                logging.warning(path_info)
                self.ui.statusbar.showMessage(path_info, 10000)
                mod.browse()
        
    def on_animation_time_return_pressed(self):
        "Getting the value from the text"
        time = self.ui.animationTime.text()
        try:
            time = int (time)
            time_list = self.manager.groups['t']
            time_point_indx = 0
            # If it's a vector on the just ran sim.
            if hasattr(time_list, 'to_python'):
                time_list = time_list.to_python()
                time_list = np.around(time_list, 3)
        
                time_point_indx = np.where(time_list==time)[0]
            # If it's a numpy array saved on the disk
            else:
                rounded = time_list.read().round(3)
                time_point_indx = np.where(rounded==time)[0]
        
            self.sync_visio_3d(time_point_indx)
            self.ui.timelineSlider.setValue(time_point_indx)
        except:
            logger.warning("Value not present in the array.")
        
    def on_timeline_value_changed(self):
        """Draw the animation according to the value of the timeline"""
    
        time_point_indx = self.ui.timelineSlider.value()
        self.sync_visio_3d(time_point_indx)    
        
    def plot_vector(self):
        
        items = self.ui.treeWidget.selectedItems()
        
        x = None
        
        # Plot legend if required
        legend_status = self.ui.legend.isChecked() #return True if toggled.
        
        points_status = self.ui.points.isChecked()
        # Retrieve the fig num
        fig_num = self.ui.fig_num_spinBox.value()
        
        for item in items:
            if item.childCount() == 0: # Leaf, so it is the variable to plot
                
                sectionItem = item.parent()
                sectionName = str(sectionItem.text(0)) #Column used
                var = str(item.text(0))
                detail = str(item.text(1))
                
                groupName = str(sectionItem.parent().text(0))
                x = self.manager.groups[groupName]
                key = sectionName + "_" + var
                vecs_to_plot = { key : item.vec}
                self.manager.plot_vecs(vecs_to_plot, x=x, legend=legend_status, 
                              figure_num=fig_num, points=points_status)
    
    def get_unique_parent(self, name, parentItem = None):
        """Search the name in the treeview and return the qtElement.
        Raise an exception if not unique"""
        search = self.ui.treeWidget.findItems(name , 
                                                Qt.MatchFixedString)
        root_item = None
        if len(search) == 0: # We create the group
            root_item = None
            if parentItem is None:
                root_item = QtGui.QTreeWidgetItem(self.ui.treeWidget)
            else:
                root_item = QtGui.QTreeWidgetItem(parentItem)
            root_item.setText(0, name)
            
        elif len(search) == 1:
            root_item = search[0]
            
        else:
            error = "ERROR - too many match: %d. Group Name not \
            unique." %len(search)
            raise NameError(error)
        
        return root_item
                
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
        self.animation()
            
    def save_hdf(self):
        if not self.path_to_hdf:
            filename = QtGui.QFileDialog.getSaveFileName()
            self.path_to_hdf = str(filename) # It will go with python 3
            if self.path_to_hdf != None:
                self.manager.save_to_hdf(self.path_to_hdf)
                msg = "Saved hdf file: %s" % self.path_to_hdf
                self.ui.statusbar.showMessage(msg, 3500)    
        
    def select_model_treeview(self):
        """Synch the README and the modelOverview with the selected model."""
        mod = self._retrieve_selected_model()
        if mod:
            readme = mod.get_readme_html()
            overview = mod.get_overview()
            self.ui.textBrowser_readme.clear()
            self.ui.textBrowser_readme.insertHtml(readme)            
            self.ui.textBrowser_model_overview.clear()
            self.ui.textBrowser_model_overview.insertHtml(overview)

    
    def select_sections(self, list_of_sections):
        """Select an arbitrary number of sections from the 
        command line.
        
        
        :param: list_of_section - the list of sections to select. Each section should
                          be given by the name (sec.name() from Neuron point 
                          of view. 
        """
        if self.visio is not None:
            selection_scalar = self.visio.get_selection_scalar(list_of_sections)
            self.visio.redraw_color(selection_scalar, 'v')
            self.visio.update_sections_info(list_of_sections)
        else:
            logger.warning("You have to launch the 3D Visio window first!")
    
                
    def sync_visio_3d(self, time_point_indx):
        
        var = self.ui.varToShow.text()
        var = str(var) # This will go with Py3
#        
#        #Update the label on the scale
        
        if len (self.manager.groups['t']) == time_point_indx:
            time_point_indx = time_point_indx - 1 # Avoid to go out of scale
        time = self.manager.groups['t'][time_point_indx]
        self.ui.animationTime.setText(str(time))
        
        
        start_value = float(self.ui.startValue.text())
        end_value = float(self.ui.endValue.text())

        self.visio.show_variable_timecourse(var, time_point_indx, 
                                            start_value, end_value)
    
    def tstop_changed(self):
        h.tstop = self.ui.tstopSpinBox.value()
        
    def update_dt(self, new_dt):
        self.ui.dtSpinBox.setValue(new_dt)
        
    def update_tree_view(self):
        # Fill the treeview wit all the vectors created
        #Clear all the row
        self.ui.treeWidget.clear()
        self.insert_refs_in_treeview()
            
    def update_tstop(self, new_tstop):
        self.ui.tstopSpinBox.setValue(new_tstop)
    
    def update_v_init(self, new_v_init):
        self.ui.vSpinBox.setValue(new_v_init)
        
    def v_changed(self):
        h.v_init = self.ui.vSpinBox.value()
    
    # create the command line to compile mod files into nrnmech.dll and launch it. command line is
    # <cygwin-dir>\bin\bash.exe -c "cd <model-dir>; /usr/bin/sh -c '<nrnhome>/lib/mknrndll.sh <nrnhome>'"
    def windows_compile_mod_files(self, model_dir):
        # Get the required pathes
        if os.environ.has_key('NEURONHOME'):
            s1=os.environ['NEURONHOME']
            s2=os.environ['NEURONHOME']
        else:
            import _winreg
            k1=_winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Cygwin\\setup")
            s1=_winreg.QueryValueEx(k1, 'rootdir')[0]
            _winreg.CloseKey(k1)

            k2=_winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\NEURON\\nrn72") 
            s2=_winreg.QueryValueEx(k2, 'Install_Dir')[0]
            _winreg.CloseKey(k2)

        s1u=s1.replace('\\', '/')
        s2u=s2.replace('\\', '/')
        cmd=s1+"\\bin\\bash.exe"
        arg="cd "+model_dir+";"+s1u+"/bin/sh -c '" + s2u + "/lib/mknrndll.sh " + s2u + "'"
        import subprocess
        subprocess.Popen([cmd, '-c', arg], stdin=subprocess.PIPE).communicate(input="\r\n")

    # Copy all mod files under model directory into the root directory
    def find_mod_files(self):
        import shutil
        mod_files = []
        for root, dirnames, filenames in os.walk('.'):
            if (root == '.'): continue
            for filename in filenames:
                base_name, file_extension = os.path.splitext(filename)
                if file_extension == '.mod':
                    logger.info('Copy %s into model directory'%os.path.join(root, filename))
                    # Double checking we are not copying over the same file.
                    logger.debug("%s %s" %(root, filename))
                    filename_src = os.path.join(root, filename)
                    filename_dest = os.path.join('.', filename)
                    if not os.path.isfile(filename_dest):
                        shutil.copy(filename_src, filename_dest)

class ItemRef(QtGui.QTreeWidgetItem):
    def __init__(self, sec_root, vec):
        QtGui.QTreeWidgetItem.__init__(self, sec_root) # >1000 if custom.
        self.vec = vec
    
    
        
class Timeloop(QtCore.QThread):
    """Daemon thread to connect the console with the gui"""
    def __init__(self, widgetDic, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.widgetDic = widgetDic
        
    def __del__(self):
        self.wait()
        
    def run(self):
        """Update the gui interface"""
        while True:
            self.sleep(1) #check every sec
            
            if h.dt != self.widgetDic['dt'].value():
                self.emit( QtCore.SIGNAL('updateDt(double)'), h.dt )
            if h.tstop != self.widgetDic['tstop'].value():
                self.emit( QtCore.SIGNAL('updateTstop(double)'), h.tstop )
            if h.v_init != self.widgetDic['v_init'].value():
                self.emit( QtCore.SIGNAL('updateVInit(double)'), h.v_init )
            
                
            
            
