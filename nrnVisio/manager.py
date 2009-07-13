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

class Manager(object):
    '''
    The Manager class is used to manage all the vecRef, to create them 
    and retrieve the information
    '''


    def __init__(self):
        '''
        Initialize the vecRef list
        '''
        self.vec_refs = []
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
        success = False
        if hasattr(sec, var):
            # Adding the vector only if does not exist
            alreadyPresent=False
            for vecRef in self.vec_refs:
                if vecRef.sec_name == sec.name():
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
                self.vec_refs.append(vecRef)
                success = True
        
        return success
    
    def get_vector(self, sec, var):
        """Return the vec that record the var in a given section
        
        param: 
            sec - Section of interest
            var - variable recorded by the vector.
            
            return - the vector that record the variable var"""
        for vecRef in self.vecRefs:
            if vecRef.sec == sec:
                if vecRef.vecs.has_key(var):
                   return vecRef.vecs[var]
    
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
        "Return the minimal tree of section \
        Using the given section as the last leave"
        tree = []
        tree.append(sec)
        tree = self.__get_parent(sec, tree)
        return tree
    
    def __get_parent(self, sec, tree):
        "Recursive function used to create the tree list of section"
        sec.push()
        secRef = h.SectionRef()
        if secRef.has_parent():
            parentSeg = secRef.parent()
            parentSec = parentSeg.sec
            tree.append(parentSec)
            tree = self.__get_parent(parentSec, tree)
        return tree

class VecRef(object):
    """Basic class to associate one or more vectors with a section"""
    def __init__(self, sec):
        # section
        self.sec_name = sec.name()
        #Dict with all the vecs
        # Key: var Value: Hoc.Vector
        self.vecs = {}