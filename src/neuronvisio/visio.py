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

from PyQt4 import QtGui, QtCore, uic

from enthought.traits.api import HasTraits, Instance, on_trait_change, \
    Int, Dict
from enthought.traits.ui.api import View, Item
from enthought.mayavi.core.ui.api import MayaviScene, MlabSceneModel, \
        SceneEditor

import numpy as np
from enthought.mayavi import mlab
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
        layout.setMargin(0)
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
    
    def __init__(self, default_cyl_color, selected_cyl_color, sec_info_label,
                 manager):       
        
        # Needed when user pick the cylinder from visio and 
        # we need to get the section
        self.cyl2sec = {}
        
        # Needed to update the value of a cyl bound to a section
        self.sec2cyl = {}
        
        self.seg2id = {}
        self.sec2coords = {}
        self.connections = []

        self.default_cyl_color = default_cyl_color
        self.selected_cyl_color = selected_cyl_color                
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
        
        # ScalarBar
        self.colorbar = None
    

    def picker_callback(self, picker):
        """ Picker callback: this get called when on pick events.
        """
        # Outline
        if not self.outline: 
            self.outline = mlab.outline(line_width=1, color=(1.0, 1.0, 1.0))
            self.outline.outline_mode = 'cornered'
        self.outline.visible = False
        
        # Deselect
#        if self.selected_cyl is not None: 
#            self.selected_cyl.actor.property.color = self.update_color(self.default_cyl_color)
#            self.selected_cyl = None
        print picker.pick_position
        
        bounds = self.cyl2sec.keys()
        for bound in bounds:
            x_b, y_b, z_b = bound[0], bound[1], bound[2]
            if bisect_left(x_b, self.picker.pick_position[0]) == 1:
              if bisect_left(y_b, self.picker.pick_position[1]) == 1:
                  if bisect_left(z_b, self.picker.pick_position[2]) == 1:
                      print "Selected Section: %s" %self.cyl2sec[bound].name()
                      self.selected_cyl = bound
                      info = self.get_sec_info(self.cyl2sec[self.selected_cyl])
                      self.sec_info_label.setText(info)
                      self.outline.bounds = (x_b[0], x_b[1], y_b[0],
                                             y_b[1], z_b[0], z_b[1])
                      self.outline.visible = True
                   
#        for surf in surfs:
#            tube = surf.parent.parent
#            dataset = tube.outputs[0]
#            points = dataset.points.to_array()
#            x,y,z = points.T
#            x_b = [x.min(), x.max()]
#            y_b = [y.min(), y.max()]
#            z_b = [z.min(), z.max()]
#            
#            if bisect_left(x_b, self.picker.pick_position[0]) == 1:
#                if bisect_left(y_b, self.picker.pick_position[1]) == 1:
#                    if bisect_left(z_b, self.picker.pick_position[2]) == 1:
#                        self.selected_cyl = surf
#                        surf.actor.property.color = self.update_color(self.selected_cyl_color)
#                        info = self.get_sec_info(self.cyl2sec[self.selected_cyl])
#                        self.sec_info_label.setText(info)
##                        self.outline.bounds = (x_b[0], x_b[1], y_b[0], y_b[1], z_b[0], z_b[1])
##                        self.outline.visible = True
#                        break

        
#    def picker_callback(self, picker):
#        """ Picker callback: this get called when on pick events. 
#        """
#        picked = picker.actor
#        
#        #deselect
#        if self.selected_cyl is not None:
#            self.update_color(self.selected_cyl, self.default_cyl_color)
#            self.selected_cyl = None
#            
#        for cyl in self.cyl2sec.keys():
#            if picked == cyl.actor:
#                sec = self.cyl2sec[cyl]
#                self.selected_cyl = cyl
#                self.update_color(cyl, self.selected_cyl_color)
#                break
#        if self.selected_cyl is not None:
#            info = self.get_sec_info(self.cyl2sec[self.selected_cyl])
#            self.sec_info_label.setText(info)
#        else:
#            self.sec_info_label.setText("No section is selected.")
        
        
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
            for vecRef in self.manager.refs['VecRef']:
                if vecRef.sec == sec:
                    if vecRef.vecs.has_key(var):
                        vec = vecRef.vecs[var]
                        var_value = None
                        if len(vec) == 0: # Not initialized
                            var_value = 0
                        else:
                            var_value = vec[time_point]
                        sec.push()
                        var_scalar.extend(np.repeat(var_value, h.n3d()))
                        h.pop_section()
        
        return np.array(var_scalar)

    def draw_mayavi(self, x, y, z, d, edges):
        "Draw the surface the first time"
        
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
        
        dataset = self.tube.outputs[0]
               
        # Extending the vector to the right lenght:
        d = dataset.point_data.get_array('diameter')
        scalar = scalar.flatten() # Collapsing in 1-D
        print "Scalar lenght %s" %len(scalar)
        repeat = len(d) / len(scalar)
        scalar = np.repeat(scalar, repeat)
        array_id = dataset.point_data.add_array(scalar)
        dataset.point_data.get_array(array_id).name = scalar_name
        dataset.point_data.update()
        src2 = mlab.pipeline.set_active_attribute(self.tube, 
                                                  point_scalars=scalar_name)
        self.surf = mlab.pipeline.surface(src2)
        

    def update_color(self, color):
        
        return (color.red()/255., color.green()/255., color.blue()/255.)
    
    def update_selected_sec(self, color):
        """Update the color of the select section"""
        if self.selected_cyl is not None:
            self.update_color(self.selected_cyl, color)
            self.selected_cyl_color = color
    
    def update_def_sec(self, color):
        """Update the default color of all cyls"""
        cyls = self.cyl2sec.keys()
        for cyl in cyls:
            self.update_color(cyl, color)
        
        if self.selected_cyl:
            self.update_color(self.selected_cyl, self.selected_cyl_color)
        self.default_cyl_col = color
        
        
    def calc_offset(self, start_v, end_v, v):
        """Calculate the offset for the gradient 
        according to the input variable"""
        
        range = abs(start_v - end_v)
        delta = abs(start_v - v)
        # range : delta = 1 : offset
        offset = delta/range
        return offset
    
    def calculate_gradient(self, var_value, start_value, start_col, 
                           end_value, end_col):
        """Calculate the color in a gradient given the start and the end
        
        params:
        var_value - The value read from the vector
        start_value - the initial value for the var
        end_value - the final value for the var
        start_col - the starting color for the linear gradient
        end_col - the final color for the linear gradient"""
        
        
        offset = self.calc_offset(start_value, end_value, var_value)
 
#        print "Start_value: %f, var_value: %f, end_value: %f, offset \
#        %f" %(start_value, var_value, end_value, offset)
        
        start_col = self._rgb(start_col)
        end_col = self._rgb(end_col)
        col = [0, 0, 0]
        for i, primary in enumerate(col):
            col[i] = (end_col[i] - start_col[i]) * offset + start_col[i] 
            if col[i] < 0:
                s = "Color out of range: start %s, end: %s, var: %s, \
                start_col: %s, end_col: %s, col:%s" %(start_value, 
                                                      end_value,
                                                      var_value,
                                                      start_col,
                                                      end_col,
                                                      col[i])
                msg = "Current value out of bounderies. Value: %s, Min: %s,\
                Max: %s." %(var_value, start_value, end_value)
                
                print msg
                if var_value < start_value:
                    col[i] = start_col[i]
                    print "Setting the color to the starting color."
                elif var_value > end_value:
                    col[i] = end_col[i]
                    print "Setting the color to the ending color."                                                       
        #print "start %s, end %s Calculated color %s" % (start_col, end_col, col)
        return QtGui.QColor(col[0],col[1],col[2])
    
    def show_variable_timecourse(self, var, time_point, start_value, end_value):
        """Show an animation of all the section that have 
        the recorded variable among time"""
        
        # Getting the new scalar
        new_scalar = self.get_var_data(var, time_point)
        
        # Swapping the old with the new
        #dataset = self.tube.outputs[0]
        
        d = self.dataset.point_data.get_array('diameter')
        if len(d) != len(new_scalar):
            print "ERROR! MISMATCH on the Vector Lenght."
            print "If you assign the new vectors it will not work"
            print "Diameter lenght: %s New Scalar lenght: %s var: %s" %(len(d),
                                                                        len(new_scalar),
                                                                        var)
        
        array_id = self.dataset.point_data.add_array(new_scalar)
        self.dataset.point_data.get_array(array_id).name = var
        self.dataset.point_data.update()
        
        # Updating the dataset
        ms = self.surf.mlab_source
        ms.m_data.update()
        
#        module_manager = self.surf.parent
#        module_manager.scalar_lut_manager.data_range = np.array([start_value, 
#                                                                 end_value])
        if not self.colorbar:
            self.colorbar = mlab.colorbar(orientation='vertical')
            #self.text 
#        for vecRef in vecRefs:
#            if vecRef.vecs.has_key(var):
#                vec = vecRef.vecs[var]
#                var_value = vec[time_point]
#                
#                ## Use it to retrieve the value from the gradient with the index
#                color = self.calculate_gradient(var_value, start_value, 
#                                                start_col, end_value, 
#                                                end_col)
#                
#                self.draw_section(vecRef.sec, color=color)
        
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
        return (np.array(x),np.array(y),np.array(z),np.array(d))
    
        
    def _rgb(self, qcolor):
        return (qcolor.red(), qcolor.green(), qcolor.blue())
