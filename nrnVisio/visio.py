"""
 * Copyright (C) Thu May 21 11:46:55 BST 2009 - Michele Mattioni:
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

from __future__ import division # to have the floating point properly managed
import visual
import visual.text
from neuron import h
import threading
import gtk
import gobject


"""Manage the visual window and offer some useful methods to explore the model"""

class Visio(object):
    
    def __init__(self):

        self.scene = visual.display(title="NeuronVisio 3D")
        # Needed when user pick the cylinder from visio and 
        # we need to get the section
        self.cyl2sec = {}
        
        # Needed to update the value of a cyl bound to a section
        self.sec2cyl = {}
        
        self.selected_cyl = None # Used for storing the cyl when picked
        
        self.vecRefs = []
        
        self.selected_section_color = () 
        self.default_section_color = () 
        self.background_color = ()
        self.h = h # Link to the neuron interpreter
        self.t = None # Var to track the time Vector
        self.drawn = False # Check if the section are alredy drawn or not
        # Load the std run for NEURON
        h.load_file("stdrun.hoc")

        
        
    def getVec(self,sec, var=None):
        """Return the vecs that record given a section
        
        param: 
            sec - Section of interest
            var - if None return all the vectors that record in that section
            as a list, otherwise return the vector that record the variable var"""
        vecsSection = [] 
        for vecRef in self.vecRefs:
            if vecRef.sec == sec:
                if var is None:
                    vecsSection.append(vecRef.vec)
                elif var == vecRef.var:
                    return vecRef.vec
        
        return vecsSection
                        
    
    def pickSection(self):
        """Pick a section of the model"""
        while(True):
            if self.scene.mouse.clicked:
                 m = self.scene.mouse.getclick()
                 loc = m.pos
                 picked = m.pick
                 if picked is not None:
                     # Redraw the old one with the default color
                     if self.selected_cyl != None:
                         self.selected_cyl.color = self.default_section_color
                     
                     picked.color = self.selected_section_color
                     self.selected_cyl = picked
                     sec = self.cyl2sec[picked]
                     
                     return sec
                     
                     #print "Section: %s Name: %s" %(sec, sec.name())
    
    
    
    def createVector(self, var):
        """Create a Hoc Vector and record the variable given."""
        
        sec = self.pickSection()
        vecNotPresent = True
        for vecRef in self.vecRefs:
            print "Searched: var %s, sec %s.\tCurrent var: %s sec: %s" %(var, sec, vecRef.var, vecRef.sec) 
            if vecRef.var == var and vecRef.sec == sec:
                  vecNotPresent = False
                  break
        if vecNotPresent:      
            vec = h.Vector()
            varRef = '_ref_' + var
            vec.record(getattr(sec(0.5), varRef))
            vecRef = VecRef(var, vec, sec)
            self.vecRefs.append(vecRef)
        return sec     
                       
    def retrieve_coordinate(self, sec):
        """Retrieve the coordinates of the section"""
        coords = {}
        sec.push()
        coords['x0'] = h.x3d((h.n3d()- h.n3d()))
        coords['x1'] = h.x3d((h.n3d()- 1))
        coords['y0'] = h.y3d((h.n3d()- h.n3d()))
        coords['y1'] = h.y3d((h.n3d()- 1))
        coords['z0'] = h.z3d((h.n3d()- h.n3d()))
        coords['z1'] = h.z3d((h.n3d()- 1))
        h.pop_section()
        return coords
        
    
    def draw_section(self, sec, color):
        """Draw the section with the optional color
        and add it to the dictionary cyl2sec
        
        :params:
            sec - Section to draw
            color - tuple for the color in RGB value. i.e.: (0,0,1) blue"""
        
        # If we already draw the model we don't have to get the coords anymore.
        cyl = None
        
        if not self.drawn :
            
            coords = self.retrieve_coordinate(sec)
            x_ax = coords['x1'] -coords['x0']
            y_ax = coords['y1'] -coords['y0']
            z_ax = coords['z1'] -coords['z0']
        
            cyl = visual.cylinder(pos=(coords['x0'],coords['y0'],coords['z0']), 
                          axis=(x_ax,y_ax,z_ax), radius=sec.diam/2)
            
            if not self.cyl2sec.has_key(cyl):
                self.cyl2sec[cyl] = sec
        
            if not self.sec2cyl.has_key(sec.name()):
                self.sec2cyl[sec.name()] = cyl #Name for Hoc compability
        else:
            cyl = self.sec2cyl[sec.name()]   
        
        cyl.color = color
    
    def show_variable_timecourse(self, var, time_point, start_value, start_col, end_value, end_col):
        """Show an animation of all the section that have 
        the recorded variable among time
        
        :params:
            var - the variable to show"""
        
        for vecRef in self.vecRefs:
            if vecRef.vecs.has_key(var):
                vec = vecRef.vecs[var]
                var_value = vec.x[time_point]
                
                ## Use it to retrieve the value from the gradient with the index 
                color = self.calculate_gradient(var_value, start_value, 
                                                start_col, end_value, 
                                                end_col)
                self.draw_section(vecRef.sec, color=color)
        #return # give back the control to the gtk thread
        
    def calculate_gradient(self, var_value, start_value, start_col, end_value, end_col):
        """Calculate the color in a gradient given the start and the end
        
        params:
        var_value - The value read from the vector
        start_value - the initial value for the var
        end_value - the final value for the var
        start_col - the starting color for the linear gradient
        end_col - the final color for the linear gradient"""
        
        # Not built in cairo function 
        # Has to be implemented by hand.
        # See more on this
        # http://lists.cairographics.org/archives/cairo/2008-September/014955.html
        
        # Cast from str to int
        start_value = int(start_value)
        end_value = int(end_value)
        
        #Get the scale
        
        scale = abs(start_value) + abs(end_value)
        
        # To calc the indx we need concord signs
        indx = 0
        if var_value < 0:
            indx = abs(start_value - var_value)
        else:
            indx = abs(abs(start_value) + var_value)
 
#        print "Scale: %f, start_value: %f, var_value: %f, end_value: %f, indx: %f" %(scale,
#                                                                           start_value,
#                                                                           var_value,
#                                                                           end_value,
#                                                                           indx)

        
        # Now on the color
        (hue1, s1, v1) = visual.color.rgb_to_hsv(start_col)
        (hue2, s2, v2) = visual.color.rgb_to_hsv(end_col)
        
        scale_color = hue1 + hue2
        # scale : scale_color = indx : indx_col
        indx_col = (scale_color * indx)/scale
        hue = indx_col
        

                                                                           
#        print "Scale color: %f, hue1: %f, hue2: %f, hue: %f" %(scale_color, hue1, hue2, hue)
        
        color = visual.color.hsv_to_rgb((hue, s1,v1)) # Saturation and Value are the same
        return color 
                
    def findSecs(self, secList, secName):
        """Find a section with a given Name in a List of Section"""
        selectedSec = None
        for sec in secList:
            if hasattr(sec, "head"): # it's a spine
                spines_attr = ["head","neck","psd"]
                for attr in spines_attr:
                    #print attr, sec.__dict__[attr].name(), secName    
                    if sec.__dict__[attr].name() == secName:
                        selectedSec = sec
                        print "Found sec %s, spine %s" %(sec.__dict__[attr].name(), sec.id)
                        break
            else: # Normal secion
            
                if sec.name() == secName:
                    selectedSec = sec
                    break
        if selectedSec is None:
            return ""    
            
        return selectedSec
    
    def draw_model(self, controls):
        """Draw the model.
        Params:
        controls - the main gui obj."""
        # Draw the new one
        h.define_shape()
        num_sections = 0
        for sec in h.allsec():
            if sec == controls.selectedSec:
                self.draw_section(sec, self.selected_section_color)
            else:
                self.draw_section(sec, self.default_section_color)
            num_sections += 1
        
        if num_sections >= 1:
            self.drawn = True
        
        return self.drawn 
            
    def drag_model(self):
        """Drag the model"""
        pick = None # no object picked out of the scene yet
        
        while True:
            if self.scene.mouse.events:
                m1 = self.scene.mouse.getevent() # get event
                if m1.drag and m1.pick : # if touched a cylinder
                    drag_pos = m1.pickpos # where on the cylinder
                    pick = m1.pick # pick now true (not None)
                elif m1.drop and not m1.drag: # released at end of drag
                    pick = None # end dragging (None is false)
                    break # Out of the loop.
            if pick:
                # project onto xy plane, even if scene rotated:
                new_pos = self.scene.mouse.project(normal=(0,0,1))
                
                if new_pos != drag_pos: # if mouse has moved
                    # offset for where the ball was clicked:
                    offset = new_pos - drag_pos
                    # For all the object
                    for obj in self.scene.objects:
                            obj.pos += offset
                            drag_pos = new_pos # New drag pos start is the new pos
                            
    def addVecRef(self, var, sec):
        """Add a vecRef in the list. It takes care to create the vector
        
        :param: 
        var - The variable to record
        sec - The section where to record
        
        return success"""
        success = False
        if hasattr(sec, var):
            # Adding the vector only if does not exist
            alreadyPresent=False
            for vecRef in self.vecRefs:
                if vecRef.sec.name() == sec.name():
                    if vecRef.vecs.has_key(var):
                        alreadyPresent = True
                        break
             
            if not alreadyPresent:
                
                # Creating the vector
                vec = h.Vector()
                varRef = '_ref_' + var
                vec.record(getattr(sec(0.5), varRef))
                
                # Adding to the list
                vecRef = VecRef(sec)
                vecRef.vecs[var] = vec
                self.vecRefs.append(vecRef)
                success = True
        
        return success
    
    def addAllVecRef(self, var):
        """Create the vector for all the section with the given variable"""
        done = False
        responses = []
        for sec in h.allsec():
            response = self.addVecRef(var, sec)
            responses.append(response)
        # If all the responses are False it means we already
        # created all the vecs and we are done    
        if any(responses) == False: #all False we're done
            done = True
        return done
                
        

class VecRef(object):
    """Basic class to associate one or more vectors with a section"""
    def __init__(self, sec):
        # section
        self.sec = sec
        #Dict with all the vecs
        # Key: var Value: Hoc.Vector
        self.vecs = {}
        
    