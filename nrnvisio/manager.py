# * Copyright (C) Thu Jul  9 11:08:09 BST 2009 - Michele Mattioni:
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

""":synopsis: Manage the map between vectors and sections
 
"""

from neuron import h
import numpy
import os
import matplotlib

# Checking the variable DISPLAY to decide the backend
if not os.environ.has_key("DISPLAY"):
    matplotlib.use('Agg')
    
import matplotlib.pyplot as plt


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
        and record the given variable.
        
        :param var: The variable to record
        :param sec: The section where to record
        :return: True if the vector is created successfully."""
        
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
                try:
                    vec.record(getattr(sec(0.5), varRef))
                except NameError:
                    print "The variable %s is not present in the section %s" \
                    % (varRef, sec.name())
                    success = False
                else:                                
                    # Adding to the list
                    vecRef = VecRef(sec)
                    vecRef.vecs[var] = vec
                    self.vecRefs.append(vecRef)
                    success = True
        
        return success
    
    def get_vector(self, sec, var):
        """Return the vec that record the var in a given section
        
        :param sec: Section of interest
        :param var: variable recorded by the vector.
        :return: the vector that record the variable var"""
        
        for vecRef in self.vecRefs:
            if vecRef.sec_name == sec.name():
                if vecRef.vecs.has_key(var):
                   return vecRef.vecs[var]
    
    def sum_vector(self, vec1, vec2):
        """Sums two vectors with the same length. The vector are 
        converted in numpy array and then summed together 
        
        :param vec1: First addendum
        :param vec2: Second addendum
        :return: The numpy array sum of the two.
        :rtype: Numpy array
        """
        return numpy.array(vec1) + numpy.array(vec2)
    
    def get_vectors(self, section_list, var):
        """Return a dictionary containing the vector which record the var. The 
        section name is used as key.
        
        :param section_list: The list of the section which is interested
        :param var: The variable of interest
        :return: The dictionary with section name as key and the vector as the value
        :rtype: dictionary
        """
        vecs = {}
        for sec in section_list:
            vec = self.get_vector(sec, var)
            vecs[sec.name()] = (vec)
        return vecs
            
    def add_all_vecRef(self, var):
        """Create the vector for all the section present in the model 
        with the given variable
        :param var: The variable to record"""
        
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
        Using the given section as the last leaf
        
        :param sec: The section that will be used as the last leaf
        :return: The section's tree in a list format"""
        
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
        """Convert all the vecRefs into the pickable
        substistitute the hocVectors with a numpy array
        Set to None the ref for the section.
        """
        
        pickable_vec_refs = []
        for vecRef in self.vecRefs:
            vecRef.pickable = True
            vecRef.sec = None
            for key, vec in vecRef.vecs.iteritems():
                vecRef.vecs[key] = numpy.array(vec)
            pickable_vec_refs.append(vecRef)
        return pickable_vec_refs

    
    def convert_syn_vec_refs(self):
        """Convert the synVecRef into pickable changing the hocVector with 
        a numpy array"""
        pickable_synVecRefs = []
        for synVecRef in self.synVecRefs:
            for key, vec in synVecRef.syn_vecs.iteritems():
                synVecRef.syn_vecs[key] = numpy.array(vec)
                
            pickable_synVecRefs.append(synVecRef)
        return pickable_synVecRefs
    
    def add_synVecRef(self, synapse):
        """Add the synVecRef object to the list
        
        :param synapse: The synapse to record.
        """
        synVecRef = SynVecRef(synapse)
        self.synVecRefs.append(synVecRef)

            
    def plotVecs(self, vecs_dic,legend=True, figure_num=None):
        """Plot the vectors with plt
        
        :param vecs_dic: dictionary with section name as k and the vec obj as value
        :param var: Which variable we are plotting.
        :param legend:  If True the legend is plotted
        :param figure_num: in which figure we want to plot the line
        """
        
        
        if figure_num is not None:
            plt.figure(figure_num)
        else:
            plt.figure()
            
        
        ax  = plt.subplot(111) # One subplot where to draw everything
         
        for key, vec in vecs_dic.iteritems():
            
            plt.plot(self.t, vec, label=key)
            if legend:
                plt.legend()
            
class VecRef(object):
    """Basic class to associate one or more vectors with a section
    """
    def __init__(self, sec):
        """Create a vecRef object which map the section name and the 
        recorded vectors.
        
        :param sec: The section which all the vectors belongs
        
        """
        self.sec_name = sec.name()
        self.sec = sec
        self.pickable = False
        #Dict with all the vecs
        # Key: var Value: Hoc.Vector
        self.vecs = {}
        
            
class SynVecRef(object):
    """Class to track all the synapse quantity of interest"""
    
    def __init__(self, syn):
        """Create a synVecRef object which map the synapse positiona and name 
        and the recorded vectors in it.
        
        :param syn: The synapse to map
        """
        self.chan_type = syn.chan_type
#        print "Creating synVec: syn type %s, synvec type %s" %(syn.chan_type,
#                                                               self.chan_type)
#        print "syn Vectors %s" %syn.syn_vecs
        self.section_name = syn.section.name()
        self.syn_vecs = syn.syn_vecs