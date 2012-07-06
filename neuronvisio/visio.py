# * Copyright (C) Wed Jan  6 10:17:03 GMT 2010 - Michele Mattioni:
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

""":synopsis: 3D Visual operations

Contain all the 3D operations.
"""


import os
os.environ['ETS_TOOLKIT'] = 'qt4'
import logging
logger = logging.getLogger(__name__)

from pyface.qt import QtGui, QtCore
from PyQt4 import uic

from traits.api import HasTraits, Instance, on_trait_change, \
    Int, Dict
from traitsui.api import View, Item
from mayavi.core.ui.api import MayaviScene, MlabSceneModel, \
        SceneEditor

import numpy as np
from mayavi import mlab
#mlab.options.backend = 'envisage'



from bisect import bisect_left

from neuron import h


################################################################################
#The actual visualization
class Visualization(HasTraits):
    scene = Instance(MlabSceneModel, ())

    @on_trait_change('scene.activated')
    def update_plot(self):
        # This function is called when the view is opened. We don't
        # populate the scene when the view is not yet open, as some 
        # VTK features require a GLContext.

        # We can do normal mlab calls on the embedded scene.
#        self.scene.mlab.test_points3d()
        pass

    # the layout of the dialog screated
    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                     height=400, width=500, show_label=False),
                resizable=True # We need this to resize with the parent widget
                )


################################################################################
# The QWidget containing the visualization, this is pure PyQt4 code.
class MayaviQWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.visualization = Visualization()

        # If you want to debug, beware that you need to remove the Qt
        # input hook.
        #QtCore.pyqtRemoveInputHook()
        #import pdb ; pdb.set_trace()
        #QtCore.pyqtRestoreInputHook()

        # The edit_traits call will generate the widget to embed.
        self.ui = self.visualization.edit_traits(parent=self, 
                                                 kind='subpanel').control
        layout.addWidget(self.ui)
        self.ui.setParent(self)



class Visio(object):
    
    def __init__(self, sec_info_label, manager):       
        
        # Needed when user pick the cylinder from visio and 
        # we need to get the section
        self.cyl2sec = {}
        
        # Needed to update the value of a cyl bound to a section
        self.sec2cyl = {}
        
        self.seg2id = {}
        self.sec2coords = {}
        self.connections = []
        self.n3dpoints_per_sec = {}
           
        self.selected_cyl = None # Used for storing the cyl when picked
        self.sec_info_label = sec_info_label # Info for the selected sec
        self.manager = manager
        
        container = QtGui.QWidget()
        container.setWindowTitle("Neuronvisio 3D")
        
        self.mayavi = MayaviQWidget(container)
        layout = QtGui.QVBoxLayout(container)
        layout.addWidget(self.mayavi)
                
        # Tell visual to use this as the viewer.
        #visual.set_viewer(self.mayavi.visualization.scene)
        
        # binding to hide event.
        container.connect(container, QtCore.SIGNAL('closeEvent()'), 
                               self.closeEvent)
        
        container.show()
        
        self.container = container
        
        # Connecting the picker.
        figure = self.mayavi.visualization.scene.mlab.gcf()
        self.outline = None
        self.picker = figure.on_mouse_pick(self.picker_callback, type='cell')
        
        # ScalarBar and time_point
        self.colorbar = None
        self.timelabel = None
    

    def picker_callback(self, picker):
        """ Picker callback: this get called when on pick events.
        """
        # Outline
        
        logger.debug( picker.pick_position)
        
        bounds = self.cyl2sec.keys()
        for bound in bounds:
            x_b, y_b, z_b = bound[0], bound[1], bound[2]
            if bisect_left(x_b, self.picker.pick_position[0]) == 1:
              if bisect_left(y_b, self.picker.pick_position[1]) == 1:
                  if bisect_left(z_b, self.picker.pick_position[2]) == 1:
                      selected_sec = self.cyl2sec[bound]
                      logger.info("Selected Section: %s" %selected_sec.name())
                      
                      self.update_sections_info(selected_sec)
                      
                      info = self.get_sec_info(selected_sec)
                      self.sec_info_label.setText(info)
                      # Creating the list with selected secs.
                      # Only one passing the name
                      selected_secs_name = []
                      # only one sec selected.
                      if hasattr(selected_sec, 'name'):
                          selected_secs_name = selected_sec.name()
                      # More than one.
                      # This happens when we can't select only one 
                      # sec with the box approach...
                      else:
                          for sec in selected_sec:
                              selected_secs_name.append(sec.name())
                      new_scalar = self.get_selection_scalar(selected_secs_name)
                              
                      self.redraw_color(new_scalar, 'v')
                      

    
    def update_sections_info(self, section):
        """Updating the info tab for the given section"""
        # Check if it's only one and retrieve info
        if hasattr(section, 'name'):
            selected_secs_name = section.name()
            info = self.get_sec_info(section)
            self.sec_info_label.setText(info)
            self.selected_cyl = self.sec2cyl[section]
        # Print the list on the tab.
        else: 
            info = "Selected sections: %s" %sections
            self.sec_info_label.setText(info)
    
    def get_selection_scalar(self, selected_secs, scalar_values=None):
        """ Return a scalar array with zero everywhere but one 
        for the selected sections
        
        :param: selected_secs - list with the names of the selected sections 
        
        """
        
        new_scalar = []
        for sec in (h.allsec()):
            if sec.name() in selected_secs:
                if scalar_values:
                    indx = selected_secs.index(sec.name())
                    sec_scalar = self.build_sec_scalar(sec, scalar_values[indx])
                    logger.debug(scalar_values[indx])
                else:
                    sec_scalar = self.build_sec_scalar(sec, 1.)
            else:
                sec_scalar = self.build_sec_scalar(sec, 0.)
            new_scalar.extend(sec_scalar) 

        return np.array(new_scalar)
    
    def get_sec_info(self, section):
        """Get the info of the given section"""
        
        info = "<b>Section Name:</b> %s<br/>" %section.name()
        info += "<b>Length [um]:</b> %f<br/>" % section.L
        info += "<b>Diameter [um]:</b> %f<br/>" % section.diam
        info += "<b>Membrane Capacitance:</b> %f<br/>" % section.cm
        info += "<b>Axial Resistance :</b> %f<br/>" % section.Ra
        info += "<b>Number of Segments:</b> %f<br/>" % section.nseg
        mechs = []
        for seg in section:
            for mech in seg:
                mechs.append(mech.name())
        mechs = set(mechs) # Excluding the repeating ones
        mech_info = "<b>Mechanisms in the section</b><ul>"
        for mech_name in mechs:
            s = "<li> %s </li>" % mech_name
            mech_info += s
        mech_info += "</ul>"
        info += mech_info
        return info
                
            

    
    def closeEvent(self):
        """Just hide the window to not loose the mayavi hook"""
        self.container.hide()
        
    def draw_model(self):
        """Draw the model.
        Params:
        controls - the main gui obj."""
        
        # Draw the new one
        h.define_shape()
        num_sections = 0

        # Disable the render. Faster drawing.
        self.mayavi.visualization.scene.disable_render = True
        

        x,y,z,d = [], [], [], []
        voltage = []
        connections = []
        for sec in h.allsec():
            x_sec, y_sec, z_sec, d_sec = self.retrieve_coordinate(sec)
            self.sec2coords[sec.name()] = [x_sec, y_sec, z_sec]
            # Store the section. later.
            radius = sec.diam/2.
            sec_coords_bound = ((x_sec.min(), x_sec.max()), 
                                (y_sec.min() - radius, 
                                 y_sec.max() + radius), 
                                (z_sec.min() - radius, 
                                 z_sec.max() + radius))
            self.cyl2sec[sec_coords_bound] = sec 
            self.sec2cyl[sec] = sec_coords_bound
            
            
            for i,xi in enumerate(x_sec):
                x.append(x_sec[i])
                y.append(y_sec[i])
                z.append(z_sec[i])
                d.append(d_sec[i])
                indx_geom_seg = len(x) -1
                
                if len(x) > 1 and i > 0:
                    connections.append([indx_geom_seg, indx_geom_seg-1])
            
                    
        self.edges  = connections
        self.x = x
        self.y = y
        self.z = z
        
        # Mayavi pipeline        
        d = np.array(d) # Transforming for easy division
        
        self.draw_mayavi(x, y, z, d, self.edges)
        
    def get_var_data(self, var, time_point=0):
        """Retrieve the value of the `var` for the `time_point`.
        Prameters:
        var - variable to retrieve
        time_point - point in the simulation"""
        
        var_scalar = []
        for sec in h.allsec():
            var_value = 0
            if self.manager.refs.has_key('VecRef'):
                for vecRef in self.manager.refs['VecRef']:
                    if vecRef.sec.name() == sec.name():
                        if vecRef.vecs.has_key(var):
                            vec = vecRef.vecs[var]
                            try:
                                var_value = vec[time_point]
                            except IndexError:
                                pass # vector exist, but not initialized.
            sec_scalar = self.build_sec_scalar(sec, var_value)
            var_scalar.extend(sec_scalar)
                
                    
                        
        
        if len(var_scalar) == 0:
            logger.debug( "Var scalar 0 length. Var: %s point_time: %s" %(var, 
                                                                  time_point))
        return np.array(var_scalar)

    def build_sec_scalar(self, sec, var_value):
        
        sec.push()
        npoints = self.n3dpoints_per_sec[sec.name()]
        sec_scalar = np.repeat(var_value, npoints)
        h.pop_section()
        return sec_scalar

        
    def draw_mayavi(self, x, y, z, d, edges):
        "Draw the surface the first time"
        
        # rendering disabled
        self.mayavi.visualization.scene.disable_render = True
        
        points = mlab.pipeline.scalar_scatter(x, y, z, d/2.0)
        dataset = points.mlab_source.dataset
        dataset.point_data.get_array(0).name = 'diameter'
        dataset.lines = np.vstack(edges)
        dataset.point_data.update()
        self.dataset = dataset

        # The tube
        src = mlab.pipeline.set_active_attribute(points, point_scalars='diameter')
        stripper = mlab.pipeline.stripper(src)
        tube = mlab.pipeline.tube(stripper, tube_sides = 6, tube_radius = 1)
        tube.filter.capping = True
#        tube.filter.use_default_normal = False
        tube.filter.vary_radius = 'vary_radius_by_absolute_scalar'
        self.tube = tube
        

        # Setting the voltage
        # Making room for the voltage
        v = []
        for sec in h.allsec():
            sec.push()
            v.extend(np.repeat(0.0, h.n3d()))
            h.pop_section()
        
        v = np.array(v)
        self.draw_surface(v, 'v')
        
        # ReEnable the rendering
        self.mayavi.visualization.scene.disable_render = False

        
    def draw_surface(self, scalar, scalar_name):
        
        self.tube.children= [] # Removing the old ones 
        
        scalar = self.get_var_data('v', 0)
        array_id = self.dataset.point_data.add_array(scalar)
        self.dataset.point_data.get_array(array_id).name = scalar_name
        self.dataset.point_data.update()
        src2 = mlab.pipeline.set_active_attribute(self.tube, 
                                                  point_scalars=scalar_name)
        self.surf = mlab.pipeline.surface(src2, colormap='blue-red')
        
    
    def select_sections(self, secs_list, scalar_values=None):
        """Gets a set of sections and color them according to the scalar, 
        if provided.
        
        Args:
         
            secs_list (list): list of the section to color
            
            scalar_value (float): array with the color value (must be between 0 and 1)
        
        The position of the array is used for the secs_list
        
        Example:
        
            secs_list = [sec1, sec2]
            
            scalar_values = [0.5, 1.0]
            
            sec1 will be coloured with a 0.5 scalar value (middle of the scalar bar), 
            while sec2 will be coloured with 1.0 scalar value (end of the bar).
        
        """
    
        scalar = self.get_selection_scalar(secs_list, scalar_values=scalar_values)
        self.redraw_color(scalar, 'v')
        #self.redraw_color(scalar, 'v') # terrible hack. We need to call it twice. y?
    
    
    def show_variable_timecourse(self, var, time_point, 
                                 start_value, end_value):
        """Show an animation of all the section that have 
        the recorded variable among time"""
        
        
        # Getting the new scalar
        new_scalar = self.get_var_data(var, time_point)
        
        d = self.dataset.point_data.get_array('diameter')
        if len(d) != len(new_scalar):
            message = "ERROR! MISMATCH on the Vector Length. \
            If you assign the new vectors it will not work \
            Diameter length: %s New Scalar length: %s var: %s" %(len(d),
                                                                 len(new_scalar),
                                                                 var)
            logger.error(message)
        # ReEnable the rendering
        self.mayavi.visualization.scene.disable_render = True
        
        self.redraw_color(new_scalar, var)
        

        if not self.colorbar:
            self.colorbar = mlab.colorbar(orientation='vertical')
            time_point_string = "%.3f" %time_point
            self.timelabel = mlab.text(0.05, 
                                       0.05, 
                                       time_point_string, 
                                       width=0.05
                                       )
        
        self.colorbar.data_range = [start_value, end_value]
        time = self.manager.groups['t'][time_point]
        time_point_string = "%.3f" %round(time, 3)
        self.timelabel.text = time_point_string
        self.mayavi.visualization.scene.disable_render = False

    
    def redraw_color(self, new_scalar, var):
        """Redraw the tubes with the new scalar.
        new_scalar -- the scalar used to color the tubes
        var - the name of the variable used"""
        #self.tube.children= [] # Removing the old ones
        
        array_id = self.dataset.point_data.add_array(new_scalar)
        self.dataset.point_data.get_array(array_id).name = var
        self.dataset.point_data.update()
        
        # Updating the dataset
        ms = self.surf.mlab_source
        ms.m_data.update()
    
            
    def retrieve_coordinate(self, sec):
        """Retrieve the coordinates of the section avoiding duplicates"""
        
        sec.push()
        x, y, z, d = [],[],[],[]

        tot_points = 0
        connect_next = False
        for i in range(int(h.n3d())):
            present = False
            x_i = h.x3d(i)
            y_i = h.y3d(i)
            z_i = h.z3d(i)
            d_i = h.diam3d(i)
            # Avoiding duplicates in the sec
            if x_i in x:
                ind = len(x) - 1 - x[::-1].index(x_i) # Getting the index of last value
                if y_i == y[ind]:
                    if z_i == z[ind]:
                        present = True
                    
            if not present:
                k =(x_i, y_i, z_i)
                x.append(x_i)
                y.append(y_i)
                z.append(z_i)
                d.append(d_i)                
        h.pop_section()
        #adding num 3d points per section
        self.n3dpoints_per_sec[sec.name()] = len(d)
        return (np.array(x),np.array(y),np.array(z),np.array(d))
