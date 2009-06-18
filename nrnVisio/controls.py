"""
 * Copyright (C) Thu May 28 00:58:29 BST 2009 - Michele Mattioni:
 *  
 * This file is part of NeuronVisio
 * 
 * NeuronVisio is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.

 * NeuronVisio is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.

 * You should have received a copy of the GNU General Public License
 * along with NeuronVisio.  If not, see <http://www.gnu.org/licenses/>.

"""

import sys
import gtk
import gtk.glade
import visio
import threading
import gobject
import os
import pylab
import numpy
import time

try:
    
    from matplotlib.figure import Figure
    # uncomment to select /GTK/GTKAgg/GTKCairo
    #from matplotlib.backends.backend_gtk import FigureCanvasGTK as FigureCanvas
    from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
    #from matplotlib.backends.backend_gtkcairo import FigureCanvasGTKCairo as FigureCanvas
except:
    print "matlab and cairo backend not available"

# We start the threads here
gtk.gdk.threads_init()



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
        self.sectionCol = 0 # Defined in Glade 
        self.visio = visio.Visio()
        self.h = self.visio.h # Unpacking for less typing
        
        # Loop control
        self.user_interaction = None # Used for the loop
        time_loop = TimeLoop(self)
        time_loop.start()
        
        # Show the window
        self.window.show()
 
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
        
        #print "You should kill visio window by yourself for now.\n"
#        self.visio.scene.hide()
#        self.visio = None
        gtk.main_quit()    
        
    def on_drag_clicked(self, btn, data=None):
        """To drag the model in the window"""
        self.visio.scene.mouse.events = 0 # Discard all the previous event
        self.visio.dragModel()
        
    def on_draw_clicked(self, widget, data=None):
        """Draw the whole model"""
        drawn = self.visio.drawModel()
        if drawn:
            btns = ["drag", "pick"]
            for name in btns:
                btn = self.builder.get_object(name)
                btn.set_sensitive(True)
        else:
            no_section = self.builder.get_object("nosection")
            no_section.run()
            no_section.hide()
    
    def on_pick_clicked(self, widget, data=None):
        """Pick a section"""
        sec = self.visio.pickSection()
        statusbar = self.builder.get_object("statusbar")
        context_id = statusbar.get_context_id("sectionInfo")
        if (hasattr(sec, "id")):
            statusbar.push(context_id, "%s (%s)" %(sec.id, sec.name()))
        else:
            statusbar.push(context_id, "%s" %sec.name())
        self.selectedSec = sec
        
    def on_createVector_clicked(self, widget, data=None):
        """Create the vectors list"""
        # Grab the variable
        entry = self.builder.get_object("var_entry")
        var = entry.get_text()
        
        if var is "":
            no_var_warning = self.builder.get_object("novarwarning")
            no_var_warning.run()
            no_var_warning.hide()

        else:
            if self.visio.t is None: # Create the time vector if not already there
                self.visio.t = self.h.Vector()
                self.visio.t.record(self.h._ref_t)
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
                    success = self.visio.addVecRef(var, self.selectedSec)
                    if not success:
                        impossible_creation = self.builder.get_object("impossiblecreation")
                        impossible_creation.run()
                        impossible_creation.hide()
                    else:
                        self._update_tree_view()
                        
            elif allSection_radio_btn.get_active():
                # Create all the vectors
                allCreated = self.visio.addAllVecRef(var)
                if allCreated:
                    all_created_dial = self.builder.get_object("allvecscreated") 
                    all_created_dial.run()
                    all_created_dial.hide()
                else:
                    self._update_tree_view()
        
    def update(self):
        """Update the GUI. For now only the spin button"""
        # Get the default from the Hoc and 
        # Vm
        v_spin = self.builder.get_object("voltage_spin")
        v_init = self.h.v_init
        self._update_spin(v_spin, v_init)
        
        # tstop
        tstop_spin = self.builder.get_object("tstop_spin")
        tstop = self.h.tstop
        self._update_spin(tstop_spin, tstop)
        # dt
        dt_spin = self.builder.get_object("dt_spin")
        dt = self.h.dt
        self._update_spin(dt_spin, dt)
     
    def _update_spin(self, spin_button, value):
        """Update the spin button with the right number of digits"""
        (base, digits) = str(value).split('.')
        spin_button.set_digits(len(digits))
        spin_button.set_value(value)
        
            
                    
    def _update_tree_view(self):
        # Fill the treeview wit all the vectors created
        #Clear all the row
        self.treestore.clear()
        
        # Add all the vectors
        for vecRef in self.visio.vecRefs:
            sec = vecRef.sec
            sec_iter = self.treestore.append(None, [sec.name()])
            for var,vec in vecRef.vecs.iteritems():
                self.treestore.append(sec_iter, [var])
    
    def on_about_activate(self, widget, data=None):
        """About dialogue pop up"""
        about_dialog = self.builder.get_object("aboutdialog")
        about_dialog.run()
        about_dialog.hide()
        
    def run(self):
        """Running the gtk loop in our thread"""
        gtk.gdk.threads_enter()
        gtk.main()
        gtk.gdk.threads_leave()
    
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
                    #print sectionName
                    # get the vecRef
                    
                    for vecRef in self.visio.vecRefs:
                        sec = vecRef.sec
                        #print "SectionName vecRef: %s" %sec.name()
                        if sec.name() == sectionName:
                            # get the vec
                            vec = vecRef.vecs[var]
                            
                            vecs_to_plot[sec.name()] = vec  
                            break # Out of the inner loop
            
            #plot it
            #print vecs_to_plot, var
            self.plotVecs(vecs_to_plot, var, legend=True)

    def on_init_clicked(self, widget):
        """Set the vm_init from the spin button and prepare the simulator"""
        v_spin = self.builder.get_object("voltage_spin")
        v_init = v_spin.get_value()
        self.h.v_init = v_init
        self.h.finitialize(v_init)
        self.h.fcurrent()
        time_label = self.builder.get_object("time_value")
        time_label.set_text(str(self.h.t))
    
    
    def on_run_sim_clicked(self,widget):
        time_label = self.builder.get_object("time_value")
        #Initializing
        self.on_init_clicked(widget)
        # Run
        while self.h.t < self.h.tstop:
            self.h.fadvance()
            time_label.set_text(str(self.h.t))
            
    def on_voltage_spin_value_changed(self,widget):
        """Update the voltage value in the simulator"""
        self.user_interaction = True
        self.h.v_init = widget.get_value()
            
    def on_tstop_spin_value_changed(self,widget):
        """Update the tstop value in the simulator"""
        self.user_interaction = True
        self.h.tstop = widget.get_value()
        
    def on_dt_spin_value_changed(self, widget):
        """Update the dt value in the simulator"""
        self.user_interaction = True
        self.h.dt = widget.get_value()
            
    def plotVecs(self, vecs_dic, var, legend=True):
        """Plot the vectors with pylab
        :param:
            vecs_dic - dictionary with section name as k and the vec obj 
            as value
            var - Which variable we are plotting. Used to put the unit in 
            the graph
            legend - boolean. If True the legend is plotted"""
        figure = Figure(figsize=(5,4), dpi=100)
        area = figure.add_subplot(111) # One subplot where to draw everything
         
        for sec_name, vec in vecs_dic.iteritems():
            
            if legend:
                area.plot(self.visio.t, vec, label=sec_name)
            else:
                area.plot(self.visio.t, vec)
#        area.xlabel("Time [ms]")
#        
#        if var == 'v':
#            area.ylabel("Voltage [mV]")

        # Figure ready. Let's create a window and show it
        self.pylab_win(figure)

    def on_pylab_win_destroy(self, widget):
        
        win = self.builder.get_object("pylab_win")
        win.hide()
            
    def pylab_win(self, figure):
        """Create a pylab window with the provided figure"""
        
        win = self.builder.get_object("pylab_win")
        
        # We need to get the old widget
        
        # Destroy it
        
        # Put the new one.
        
        canvas = FigureCanvas(figure)  # a gtk.DrawingArea
        win.add(canvas)
        win.show_all()
        
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
            gtk.gdk.threads_enter()
            try:
                if not self.controls.user_interaction:
                    self.controls.update()
            finally:
                gtk.gdk.threads_leave()
            