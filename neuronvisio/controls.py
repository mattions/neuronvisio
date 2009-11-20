# * Copyright (C) Thu May 28 00:58:29 BST 2009 - Michele Mattioni:
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

""":synopsis: Gtk UI module

GTK2 class and helpers' thread
"""

import sys
import threading
import os
import time

import numpy
from neuron import h

# uncomment to select /GTK/GTKAgg/GTKCairo
try:
    import gtk
    import gtk.glade
    import cairo
    import gobject
    from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
    import pylab
    # We start the threads here
    gobject.threads_init()
    import visio
    import manager
except:
    print "No GTK available. Batch execution"
#from matplotlib.backends.backend_gtkcairo import FigureCanvasGTKCairo as FigureCanvas



class Controls(threading.Thread):
    """Main GTK control window. create a control object and start with
    controls.start()"""
    def __init__(self):
        threading.Thread.__init__(self)
        
        # Selected Section
        self.selectedSec = None # Used from pick


        # create widget tree ...
        self.builder = gtk.Builder()
        self.builder.add_from_file(os.path.join(os.path.dirname(__file__),
                                           "nrnVisioControl.glade"))
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("window")
        self.treestore = self.builder.get_object("treestore")
        # multiple selection
        treeview = self.builder.get_object("treeview")
        treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        
        self.sectionCol = 0 # Defined in Glade 
        self.visio = visio.Visio()
        self.set_colors()
        
        self.manager = manager.Manager()
        
        # Loop control
        self.user_interaction = None # Used for the loop
        time_loop = TimeLoop(self)
        time_loop.start()
        
        # Animation
        self.continue_animation = True
        
        # Show the window
        self.window.show()
        
        # Starting the thread
        self.start()
 
    def run(self):
        """Running the gtk loop in our thread"""
        gtk.main()
 
    def on_window_destroy(self, widget, data=None):
        self._shutdown()
#        print "You should kill visio window by yourself for now."
##       self.visio.display.hide()
##       self.window.hide()
#        gtk.main_quit()
    
    def on_quit_activate(self, widget, data=None):
        """Destroy the window"""
        self.window.destroy() # Destroy the window
        self._shutdown() # Common procedure to destroy visio
        
    
    def _shutdown(self):
        """Procedure to shutdown the gtk control window and the \
        visio instance"""
        
        # Killing visio
        self.visio.scene.visible = False
        
        # Destroy the animation window
        animation_win = self.builder.get_object("animation_control")
        animation_win.destroy()
        
        # Destroy all the Pylab win
        pylab.close('all')
        
        gtk.main_quit()
        
        
    def on_drag_clicked(self, btn, data=None):
        """To drag the model in the window"""
        self.visio.scene.mouse.events = 0 # Discard all the previous event
        self.visio.drag_model()
        
    
    def set_colors(self):
        """Set the colors in the visio module"""
        back_col_btn = self.builder.get_object("background_button")
        back_col = back_col_btn.get_color()
        self.visio.background_color = self._scale_rgb(back_col)
        self.visio.scene.background = self.visio.background_color
        
        default_section_btn = self.builder.get_object("section_button")
        default_col = default_section_btn.get_color()
        self.visio.default_section_color = self._scale_rgb(default_col)
        
        selected_section_btn = self.builder.get_object("selected_section_button")
        selected_col = selected_section_btn.get_color()
        self.visio.selected_section_color = self._scale_rgb(selected_col)
    
    def on_draw_clicked(self, widget, data=None):
        """Draw the whole model"""
        # 
        self.set_colors()
               
        if self.visio.draw_model(self) == True:
            self.update_visio_buttons()
        else:
            no_section = self.builder.get_object("no_section")
            no_section.run()
            no_section.hide()
    

    def on_background_button_color_set(self, widget):
        """set the background color in the visio window"""
        back_col = widget.get_color()
        self.visio.background_color = self._scale_rgb(back_col)
        self.visio.scene.background = self.visio.background_color
        
    def on_section_button_color_set(self, widget):
        """Set the default color for the section"""
        default_col = widget.get_color()
        self.visio.default_section_color = self._scale_rgb(default_col)
        # Redraw the entire model
        self.visio.draw_model(self)

    def on_selected_section_button_color_set(self, widget):
        """Set the default color for the selected section"""
        selected_col = widget.get_color()
        self.visio.selected_section_color = self._scale_rgb(selected_col)
        # Re-draw
        self.visio.draw_model(self)
        
        
    def update_visio_buttons(self):
        """Update the ui buttons connected with visio"""
        
        if self.visio.drawn:
            btns = ["drag", "pick", "animation"]
            for name in btns:
                btn = self.builder.get_object(name)
                btn.set_sensitive(True)
        else:
            no_section = self.builder.get_object("nosection")
            no_section.run()
            no_section.hide()
    
    def on_pick_clicked(self, widget, data=None):
        """Select a section from the 3D visio"""
        sec = self.visio.pickSection()
        selected_section_label = self.builder.get_object("selected_section_label")
        
        if (hasattr(sec, "id")):
            selected_section_label.set_text("%s (%s)" %(sec.id, sec.name()))
        else:
            selected_section_label.set_text("%s" %sec.name())
        self.selectedSec = sec
        
        section_info = self.builder.get_object("section_info")
        buffer = section_info.get_buffer()
        info = self.get_info(sec)
        buffer.set_text(info)
        
    def get_info(self, section):
        """Get the info of the given section"""
        
        info = "Name: %s\n" %section.name()
        info += "L: %f\n" % section.L
        info += "diam: %f\n" % section.diam
        info += "cm: %f\n" % section.cm
        info += "Ra: %f\n" % section.Ra
        info += "nseg: %f\n" % section.nseg
        
        return info
        
    def on_createVector_clicked(self, widget, data=None):
        """Create the vectors list"""
        # Grab the variable
        entry = self.builder.get_object("var_entry")
        var = entry.get_text()
        
        # Control if there is any secs available.
        num_secs = 0
        for sec in h.allsec():
            num_secs += 1
        
        if var is "":
            no_var_warning = self.builder.get_object("novarwarning")
            no_var_warning.run()
            no_var_warning.hide()
            
        elif num_secs == 0:
            no_section = self.builder.get_object("no_section")
            no_section.run()
            no_section.hide()

        else:
            # Grab the section
            selectedSection_radio_btn = self.builder.get_object("selected_sec_btn")
            
            allSection_radio_btn = self.builder.get_object("all_sections_btn")
            # Only for one section
            if selectedSection_radio_btn.get_active():
                
                # No section picked
                # Throw a warning message
                if self.selectedSec is None:
                    no_section_sel = self.builder.get_object("nosectionsel")
                    no_section_sel.run()
                    no_section_sel.hide()
                    
                # Section selected. Let's create the vector
                else:
                    success = self.manager.add_vecRef(var, self.selectedSec)
                    if not success:
                        impossible_creation = self.builder.get_object("impossiblecreation")
                        impossible_creation.run()
                        impossible_creation.hide()
                    else:
                        self._update_tree_view()
                        
            elif allSection_radio_btn.get_active():
                # Create all the vectors
                allCreated = self.manager.add_all_vecRef(var)
                if allCreated:
                    all_created_dial = self.builder.get_object("allvecscreated") 
                    all_created_dial.run()
                    all_created_dial.hide()
                else:
                    self.update_tree_view()
        
    def update(self):
        """Update the GUI spinbuttons only if the user is not using them 
        with the value from the console."""
        # Get the default from the Hoc and 
        # Vm
        v_spin = self.builder.get_object("voltage_spin")
        if not v_spin.is_focus():
            v_init = h.v_init
            self._update_spin(v_spin, v_init)
        
        # tstop
        tstop_spin = self.builder.get_object("tstop_spin")
        if not tstop_spin.is_focus():
            tstop = h.tstop
            self._update_spin(tstop_spin, tstop)
        # dt
        dt_spin = self.builder.get_object("dt_spin")
        if not dt_spin.is_focus():
            dt = h.dt
            self._update_spin(dt_spin, dt)
     
    def _update_spin(self, spin_button, value):
        """Update the spin button with the right number of digits"""
        (base, digits) = str(value).split('.')
        spin_button.set_digits(len(digits))
        spin_button.set_value(value)
        
            
                    
    def update_tree_view(self):
        # Fill the treeview wit all the vectors created
        #Clear all the row
        self.treestore.clear()
        
        # Add all the vectors
        for vecRef in self.manager.vecRefs:
            sec_name = vecRef.sec_name
            sec_iter = self.treestore.append(None, [sec_name])
            for var,vec in vecRef.vecs.iteritems():
                self.treestore.append(sec_iter, [var])
    
    def on_about_activate(self, widget, data=None):
        """About dialogue pop up"""
        about_dialog = self.builder.get_object("aboutdialog")
        # Setting the version also here. Should be read somewhere.
        about_dialog.set_version("0.3.3") 
        about_dialog.run()
        about_dialog.hide()
    
    def on_plot_clicked(self, widget, data=None):
        """Create a plot of the selected vector"""
        treeview = self.builder.get_object("treeview")
        treeselection = treeview.get_selection()
        
        #Nothing selected
        if treeselection.count_selected_rows() == 0:
            no_vec_selected = self.builder.get_object("novecselected")
            no_vec_selected.run()
            no_vec_selected.hide()
        
        else:
            # Retrieving the selection
            (treestore, pathlist) = treeselection.get_selected_rows()
            # Cicling through all the selection
            vecs_to_plot = {}
            var = ""
            for path in pathlist:
                iter = treestore.get_iter(path)
                var = treestore.get_value(iter, self.sectionCol)
                parent = treestore.iter_parent(iter) 
                if parent is None:
                    no_vec_selected = self.builder.get_object("novecselected")
                    no_vec_selected.run()
                    no_vec_selected.hide()
                    return # Out of the method.
                else:
                    # Retrieve the correct vecRef
                    sectionName = treestore.get_value(parent, self.sectionCol)
                    
                    for vecRef in self.manager.vecRefs:
                        
                        if vecRef.sec_name == sectionName:
                            # get the vec
                            vec = vecRef.vecs[var]
                            key = sectionName + "_" + var
                            vecs_to_plot[key] = vec
            #plot it
            
            # Check the legend
            legend = self.builder.get_object("legend")
            legend_status = legend.get_active() #return True if toggled.
            
            #Retrieve the fig selector
            fig_num_selector = self.builder.get_object("fig_num_selector")
            
            # Retrieve the fig num
            fig_num = fig_num_selector.get_value_as_int()
            
            self.manager.plotVecs(vecs_to_plot, legend=legend_status, 
                                  figure_num=fig_num)
            pylab.draw()
            # Set the last plotted figure as default.
            fig_num_selector.set_value(fig_num)

    def on_init_clicked(self, widget):
        """Set the vm_init from the spin button and prepare the simulator"""
        v_spin = self.builder.get_object("voltage_spin")
        v_init = v_spin.get_value()
        
        # Set the v_init
        h.v_init = v_init
        h.finitialize(v_init)
        h.fcurrent()
        
        # Reset the time in the GUI
        time_label = self.builder.get_object("time_value")
        time_label.set_text(str(h.t))
    
    def on_run_sim_clicked(self, widget):
        """Run the simulator till tstop"""
        time_label = self.builder.get_object("time_value")
        
        #Initializing
        self.on_init_clicked(widget)
        # Run
        while h.t < h.tstop:
            h.fadvance()
            time_label.set_markup("<b>" + str(h.t) + "</b>")
    
    
         
    def on_voltage_spin_value_changed(self,widget):
        """Update the voltage value in the simulator"""
        h.v_init = widget.get_value()
        
        
            
    def on_tstop_spin_value_changed(self,widget):
        """Update the tstop value in the simulator"""
        h.tstop = widget.get_value()
        
        
    def on_dt_spin_value_changed(self, widget):
        """Update the dt value in the simulator"""
        h.dt = widget.get_value()


# Animation control

    def on_animation_control_delete_event(self, widget, event):
        """Hide the animation control instead of destroying"""
        animation_win = self.builder.get_object("animation_control")
        animation_win.hide()
        return True


    def on_animation_clicked(self, widget):
        """Show the animation control"""
        
        animation_win = self.builder.get_object("animation_control")
        
        # Set the color
        gtk_btn_color_start = self.builder.get_object("start_color")
        gtk_start_color =gtk_btn_color_start.get_color()
        
        # Store it in RGB 0-1 format
        self.start_color = self._scale_rgb(gtk_start_color)
        
        gtk_btn_color_end = self.builder.get_object("end_color")
        gtk_end_color = gtk_btn_color_end.get_color()
        
        # Store it in RGB 0-1 format
        self.end_color = self._scale_rgb(gtk_end_color)
        
        gradient_area = self.builder.get_object("gradient_area")
        gradient_area.connect("expose-event", self.expose_gradient)
        
        # Setting the timeline with the time of the simulation
        timeline = self.builder.get_object("timeline")
        if self.manager.t is None:
            no_vector = self.builder.get_object("no_vector")
            no_vector.run()
            no_vector.hide()
            #print "You didn't create any vector"
        elif len (self.manager.t) == 0:
            no_simulation = self.builder.get_object("no_simulation")
            no_simulation.run()
            no_simulation.hide()
            #print "You should run the simulation first"
        else:
            timeline.set_range(0, len (self.manager.t))
            #timeline.set_increments(1, 10) #minimal increment equal to dt
            animation_win.show_all()
            animation_win.present()
                
             
            
    def on_start_color_set(self, widget):
        """Set the start color when changed"""
        self.start_color = self._scale_rgb(widget.get_color())
    
    def on_end_color_set(self, widget):
        "Set the end color when changed"
        self.end_color = self._scale_rgb(widget.get_color())
    
    def on_timeline_value_changed(self, widget):
        """Draw the animation according to the value of the timeline"""
        time_point_indx = widget.get_value()
        # cast to int from str
        time_point_indx = int(time_point_indx)
        
        entry_var = self.builder.get_object("animation_var")
        var = entry_var.get_text()
        start_col_value = self.builder.get_object("start_var_value").get_text()
        
        #Update the label on the scale
        animation_time_label = self.builder.get_object("animation_time")
        if len (self.manager.t) == time_point_indx:
            time_point_indx = time_point_indx - 1 # Avoid to go out of scale
        time = self.manager.t[time_point_indx]
        animation_time_label.set_text(str(time))
        
        
        start_value = self.builder.get_object("start_var_value").get_text()
        end_value = self.builder.get_object("end_var_value").get_text()
        
        self.visio.show_variable_timecourse(var, time_point_indx, start_value, 
                                            self.start_color, end_value, 
                                            self.end_color, self.manager.vecRefs)

    def on_play_clicked(self, widget):
        """Play the animation with the voltage color coded"""
        self.continue_animation = True 
        entry_var = self.builder.get_object("animation_var")
        var = entry_var.get_text()
        start_value = self.builder.get_object("start_var_value").get_text()
        end_value = self.builder.get_object("end_var_value").get_text()
    
        # Play the animation
        
        if not self.visio.drawn:
            self.visio.draw_model(self)
            
        # Using a thread to run the cicle 
           
        thread_for_timeline = TimelineHelper(self, var, start_value, 
                                            self.start_color, end_value, 
                                            self.end_color, self.manager.vecRefs)
        thread_for_timeline.start()
        
    
    def on_stop_clicked(self, widget):
        """Stop the animation"""
        self.continue_animation = False
    
    def update_timeline(self, t_indx, time):
        """update the timeline"""
        #print time
        timeline = self.builder.get_object("timeline")
        animation_time_label = self.builder.get_object("animation_time")
        timeline.set_value(t_indx) #Advancing the timeline
        animation_time_label.set_text(time)

 
    def expose_gradient(self, widget, event):
        """Redraw the gradient everytime is shown. The colors value are taken 
        by the tow gtkbuttoncolors"""
        
        cr = widget.window.cairo_create()
        
        # Getting the rectangle where to draw
        x = widget.allocation.x
        y = widget.allocation.y
        w = widget.allocation.width
        h = widget.allocation.height
        x1 = x+w
        y1 = y+h
        
        # We want an horizontal gradient
        gradient = cairo.LinearGradient(x, y/2, x1, y/2) 
        gradient.add_color_stop_rgb(0, self.start_color[0], self.start_color[1]
                                  , self.start_color[2])
        gradient.add_color_stop_rgb(1, self.end_color[0], self.end_color[1], 
                                  self.end_color[2])
        
        cr.rectangle(x,y,x1,y1)
        cr.set_source(gradient)
        cr.fill()
        

    def _scale_rgb(self, gtk_color):
        """Scale the gtk color to the rgb domain"""
        gtk_color_bit = 65535.0
        r = gtk_color.red / gtk_color_bit
        g = gtk_color.green / gtk_color_bit
        b = gtk_color.blue / gtk_color_bit

        return [r,g,b]
    
    def read_only(self, storage):
        """Function used to inspect the results of a simulation"""
        # convert sto into manager
    
        self.manager.t = storage.t
        # Attach the section to the proper vecRefs
        for sec in h.allsec():
            for vecRef in storage.vecRefs:
                if sec.name() == vecRef.sec_name:
                    vecRef.sec = sec
                    
        self.manager.vecRefs = storage.vecRefs
        self.manager.synVecRefs = storage.synVecRefs
        
        # Gray out stuff we can't use
        btns = ["createVector", "init", "run_sim"]
        for name in btns:
            btn = self.builder.get_object(name)
            btn.set_sensitive(False)
        self.update_tree_view()
        

class TimelineHelper(threading.Thread):
    """Thread to update the timeline when the play button is clicked"""
    def __init__(self, controls, var, start_value, start_color, 
                 end_value, end_color, vecRefs):
        threading.Thread.__init__(self)
        self.controls = controls
        self.var = var
        self.start_value = start_value
        self.start_color = start_color
        self.end_value = end_value
        self.end_color = end_color
        self.vecRefs = vecRefs
        
    
    def run(self):
        for t_indx,time in enumerate(self.controls.manager.t):
            if self.controls.continue_animation == True:
                self.controls.visio.show_variable_timecourse(self.var, t_indx, self.start_value, 
                                                         self.start_color, self.end_value, 
                                                         self.end_color, self.vecRefs)
            # Update done on the main gtk
                if t_indx % 4 == 0:
                    gobject.idle_add(self.controls.update_timeline, t_indx, str(time)) 
        
class TimeLoop(threading.Thread):
    """Daemon Thread to connect the console with the GUI"""
    def __init__(self, controls):
        threading.Thread.__init__(self)
        self.interval = 0.5 # More relaxed
        self.setDaemon(True)
        self.controls = controls
        
        
    def run(self):
        """Update the GUI interface calling the update method"""
        while True:
            time.sleep(self.interval)
            gobject.idle_add(self.controls.update)