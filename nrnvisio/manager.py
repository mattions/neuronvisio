"""
 * Copyright (C) Thu Jul  9 11:08:09 BST 2009 - Michele Mattioni:
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

from neuron import h
import numpy
from matplotlib.figure import Figure

class Manager(object):
    """The Manager class is used to manage all the vecRef, to create them 
    and retrieve the information
    """


    def __init__(self):
        
        self.vecRefs = []
        self.synVecRefs = []
        self.t = None # Var to track the time Vector
        # Load the std run for NEURON
        h.load_file("stdrun.hoc")
        
    def add_vecRef(self, var, sec):
        """Add the vecRef to the vec_res list. It takes care to create the vector 
        and record the given variable
                
        :params: 
        var - The variable to record
        sec - The section where to record
        
        return True if the vector is created successfully."""
        
        if self.t is None: # Create the time vector if not already there
            self.t = h.Vector()
            self.t.record(h._ref_t)
            
        success = False
        if hasattr(sec, var):
            # Adding the vector only if does not exist
            alreadyPresent=False
            for vecRef in self.vecRefs:
                if vecRef.sec_name == sec.name():
                    if vecRef.vecs.has_key(var):
                        alreadyPresent = True
                        break
                    else: # Adding a variable to an existing vecRef
                        vec = h.Vector()
                        varRef = '_ref_' + var
                        vec.record(getattr(sec(0.5), varRef))
                        vecRef.vecs[var] = vec
                        alreadyPresent = True
                        success = True
             
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
    
    def get_vector(self, sec, var):
        """Return the vec that record the var in a given section
        
        param: 
            sec - Section of interest
            var - variable recorded by the vector.
            
            return - the vector that record the variable var"""
        for vecRef in self.vecRefs:
            if vecRef.sec_name == sec.name():
                if vecRef.vecs.has_key(var):
                   return vecRef.vecs[var]
    
    def get_vectors(self, section_list, var):
        """Return a dictionary containing the vector which record the var. The 
        section name is used as key.
        :param section_list: The list of the section which is interested
        :param var: The variable of interest
        
        :return: The dictionary with section name as key and the vector as the value
        """
        vecs = {}
        for sec in section_list:
            vec = self.get_vector(sec, var)
            vecs[sec.name()] = (vec)
        return vecs
            
    def add_all_vecRef(self, var):
        """Create the vector for all the section present in the model 
        with the given variable"""
        done = False
        responses = []
        for sec in h.allsec():
            response = self.add_vecRef(var, sec)
            responses.append(response)
        # If all the responses are False it means we already
        # created all the vecs and we are done    
        if any(responses) == False: #all False we're done
            done = True
        return done
    
    def get_tree(self, sec):
        """Return the minimal tree of section 
        Using the given section as the last leave"""
        tree = []
        tree.append(sec)
        tree = self.__get_parent(sec, tree)
        return tree
    
    def __get_parent(self, sec, tree):
        """Recursive function used to create the tree list of section"""
        sec.push()
        secRef = h.SectionRef()
        if secRef.has_parent():
            parentSeg = secRef.parent()
            parentSec = parentSeg.sec
            tree.append(parentSec)
            tree = self.__get_parent(parentSec, tree)
        return tree
    
    def convert_vec_refs(self):
        """Convert all the vecRefs into the pickable"""
        pickable_vec_refs = []
        for vecRef in self.vecRefs:
            vecRef.convert_to_pickable()
            pickable_vec_refs.append(vecRef)
        return pickable_vec_refs

    def add_synVecRef(self, synVecRef):
        """Add the synVecRef object to the inner list
        
        :param synVecRef: The synapse Vector Ref to add to the list.
        """
        self.synVecRefs.append(synVecRef)
    
    #### Pylab stuff. Maybe another class?


            
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
                area.plot(self.t, vec, label=sec_name)
            else:
                area.plot(self.t, vec)

        return figure
            
class VecRef(object):
    """Basic class to associate one or more vectors with a section
    """
    def __init__(self, sec):
        """Constructor
        
        :param sec: The section which all the vectors belongs
        
        """
        self.sec_name = sec.name()
        self.sec = sec
        self.pickable = False
        #Dict with all the vecs
        # Key: var Value: Hoc.Vector
        self.vecs = {}
    
    def convert_to_pickable(self):
        """Convert the object into a pickable one:
        
        substistitute the hocVectors with a numpy array
        Set to None the ref for the section. 
        """
        self.pickable = True
        self.sec = None
        for key, vec in self.vecs.iteritems():
            self.vecs[key] = numpy.array(vec)
            
class SynVecRef(object):
    """Class to track all the synapse quantity of interest"""
    
    def __init__(self, chan_type, section_name):
        """Constructor
        
        :param chan_type: The type of the synaptic channel (ampa, nmda,..)
        :type chan_type: ``str``
        :param section_name: The section name where the synapses is attached
        :type section_name: ``str``
        """
        self.chan_type = chan_type
        self.section_name = section_name
        self.syn_vecs = {}
        
    def createVec(self, syn):
        """Create the vector to measure the activity of the synapse
        
        :param syn -  The synapse to record
        """
        
        # Record the stimuls
        self.synVecs["stimul"] = h.Vector()
        syn.netCon.record(synVecs["stimul"]) 
        
        # Record the current into the synaptic chan 
        synVecs["i"] = h.Vector()
        synVecs["i"].record(syn.chan._ref_i)        
        # Record the weight
        synVecs['weight'] = []