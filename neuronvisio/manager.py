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
import numpy as np
import os
import cPickle
import datetime
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(autoflush=False)

except ImportError:
    print "Sqlalchemy not installed. Please install it from \
    http://www.sqlalchemy.org/"


import matplotlib
import matplotlib.pyplot as plt


from db.tables import Base, Geometry, Vectors, SynVectors

class Manager(object):
    """The Manager class is used to manage all the vecRef, to create them 
    and retrieve the information
    
    """


    def __init__(self):
        
        self.vecRefs = [] 
        self.synVecRefs = []
        self.indipendent_variables = {}
        self.Vectors_Group_Label = 'Vectors'
        self.SynVectors_Group_Label = "SynVectors"
        self.t = None # Var to track the time Vector
        self.stims = []
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
            self.indipendent_variables[self.Vectors_Group_Label] = self.t
            
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
        return np.array(vec1) + np.array(vec2)
    
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
                vecRef.vecs[key] = np.array(vec)
            pickable_vec_refs.append(vecRef)
        return pickable_vec_refs

    
    def convert_syn_vec_refs(self):
        """Convert the synVecRef into pickable changing the hocVector with 
        a numpy array"""
        pickable_synVecRefs = []
        for synVecRef in self.synVecRefs:
            for key, vec in synVecRef.syn_vecs.iteritems():
                synVecRef.syn_vecs[key] = np.array(vec)
                
            pickable_synVecRefs.append(synVecRef)
        return pickable_synVecRefs
    
    def add_synVecRef(self, synapse):
        """Add the synVecRef object to the list
        
        :param synapse: The synapse to record.
        """
        synVecRef = SynVecRef(synapse.chan_type, synapse.section.name(), 
                              synapse.syn_vecs)
        
        self.synVecRefs.append(synVecRef)
        print "adding syn chan: %s, len synvecREfs: %d" %(synapse.chan_type,
                                                          len (self.synVecRefs))

            
    def plotVecs(self, vecs_dic, x=None, legend=True, figure_num=None):
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
            if x is None:
                plt.plot(self.t, vec, label=key)
            else:
                plt.plot(x, vec, label=key)
            if legend:
                plt.legend(loc=0)

    def create_new_dir(self, prefix="./", root="Sims"):
        """
            Create the directory where to put the simulation
        """
        self.dirRoot = os.path.join(prefix, root)
        
        today = datetime.date.today()
        free = False
        index = 0
        
        dirDate = today.strftime("%d-%m-%Y")
        
        dirComp = os.path.join(self.dirRoot, dirDate)
        dir = os.path.join(dirComp, "Sim_" + str(index))
        while not free :
            if os.path.exists(dir):
                index = index + 1
                simNum = "Sim_" + str(index)
                dir = os.path.join(dirComp, simNum )
            else:
                free = True
                os.makedirs(dir)
        return dir

    def _store_synvectors(self, session):
        """Store the Vectors in the database"""
        
        records = []
        
        # Storing the time
        t = np.array(self.t)
        
        # Saving time
        record = Vectors(vec=t, var='t', sec_name=None)
        records.append(record)
        
        pickable_synVecRefs = self.convert_syn_vec_refs()
        
        for syn_vec_ref in pickable_synVecRefs:
            for var in syn_vec_ref.syn_vecs.keys():
                vec = syn_vec_ref.syn_vecs[var]
                sec_name = self._sanitized_sec(syn_vec_ref.sec_name)
                record = SynVectors(var=var,
                                    vec=vec,
                                    sec_name=sec_name,
                                    chan_type=syn_vec_ref.chan_type
                                    )
                records.append(record)
        print 'Saving SynVecRef'
        session.add_all(records)
        session.flush()
        
    def _store_vectors(self, session):
        """Store the Vectors in the database"""
        
        records = []
        
        # Storing the time
        t = np.array(self.t)
        
        # Saving time
        record = Vectors(vec=t, var='t', sec_name=None)
        records.append(record)
        
        # Vec Ref
        pickable_vec_refs = self.convert_vec_refs()
        for vec_ref in pickable_vec_refs:
            for var in vec_ref.vecs.keys():
                vec = vec_ref.vecs[var]
                sec_name_neuroMl_accepted = self._sanitized_sec(vec_ref.sec_name)
                record = Vectors(vec=vec, var=var,
                                 sec_name=sec_name_neuroMl_accepted)
                records.append(record)

        session.add_all(records)
        session.flush()
        
    def _sanitized_sec(self, sec_name):
        """Sanitize the neuroML """
        import re
        split = sec_name.split('.') # Getting rid of the Cell name
        sec = ''
        name = ''
        if len(split) == 1:
            sec = split[0]
        elif len(split) == 2: 
            name = split[1]
            m = re.match ('(\w+)\[(\d+)\]', name)
            if m:
                sec = m.group(1) +'_'+ m.group(2)
                
            else:
                sec = name
        print "original: %s, sanitized: %s" %(sec_name, sec)
        return sec
        
    def _store_geom(self, session):
        """Store the NeuroML in the geometry table"""
        
        # writing the NeuroML model
        h.define_shape() # We need the 3D points
        
        h.load_file('mview.hoc')
        modelView = h.ModelView(0)
        modelXml = h.ModelViewXML(modelView)
        tmp_file = 'temp.xml'
        modelXml.xportLevel1(tmp_file)
        
        xml_data = ''
        with open(tmp_file, 'r') as f:
            xml_data = f.read()
        
        geom = Geometry(neuroml=xml_data)
        session.add(geom)
        session.flush()
        
        os.remove(tmp_file)
        
        
    def store_in_db(self, filename):
        """Store the simulation results in a database"""
        db_path = 'sqlite:////' + os.path.abspath(filename)
        
        engine = create_engine(db_path, echo=False)
        Session.configure(bind=engine)
        Base.metadata.create_all(engine)
        session = Session()
        
        self._store_geom(session)
        self._store_vectors(session)
        self._store_synvectors(session)
        session.commit()
    
    def _load_vecRef(self, session):
        """Load the vecref in memory"""
        
        for record in session.query(Vectors).filter(Vectors.var=='t'):
            self.t = record.vec
            self.indipendent_variables[self.Vectors_Group_Label] = self.t
        
        vecRefs = []
        for vec, var, sec_name in session.query(Vectors.vec, 
                                                  Vectors.var,
                                                  Vectors.sec_name):
            
            if sec_name != None:
                
                found = False
                
                # Check if the vecREf exists.
                # If it does we add the variable vec to the vecs dict
                # otherwise we create a new one.
                
                for vecRef in vecRefs:
                    if vecRef.sec_name == sec_name:
                        found = True
                        break
                if found:
                    vecRef.vecs[var] = vec
                    continue #Move to next record
                else: 
                    nrn_sec = eval('h.' + sec_name)        
                    vecRef = VecRef(nrn_sec)
                    vecRef.vecs[var] = vec
                
                vecRefs.append(vecRef)
                
        for sec in h.allsec():
            for vecRef in vecRefs:
                if sec.name() == vecRef.sec_name:
                    vecRef.sec = sec
                    break
        self.vecRefs = vecRefs
    
    def _load_synVec(self, session):
        """Load the SynVec in memory if they exist"""
        
        
        for record in session.query(SynVectors).filter(SynVectors.var=='t'):
            self.t = record.vec
            # Create Plotter here TODO
            self.indipendent_variables[self.SynVectors_Group_Label] = self.t
        
        synVecRefs = []
        
        for vec, var, sec_name in session.query(SynVectors.vec, 
                                                  SynVectors.var,
                                                  SynVectors.sec_name,
                                                  SynVectors.chan_type):
            if sec_name != None:               
                for synVecRef in synVecRefs:
                    if synVecRef.sec_name == sec_name:
                        if synVecRef.chan_type == chan_type:
                            found = True
                            break
                if found:
                    synVecRef.syn_vecs[var] = vec
                    continue #Move to next record
                else:
                    nrn_sec = eval('h.' + sec_name)
                    syn_vecs = {}
                    syn_vecs[var] = vec
                    synVecRef = SynVecRef(chan_type, sec_name, syn_vecs)        
                    
                
                synVecRefs.append(synVecRef)
                    
            self.synVecRefs = synVecRefs
                
#        
#        sql_stm = """SELECT * from SynVectors"""
#        synVecs_exist = False 
#        try:
#            cursor.execute(sql_stm)
#            synVecs_exist = True
#        except sqlite3.Error, e:
#            # No synVectors
#            synVecs_exist = False
#        
#        if synVecs_exist:
#            synVecRefs = []
#            for row in cursor:
#                # vecrRef
#                sec_name = str(row[2])
#                
#                if sec_name != 'NULL':
#                    
#                    var = str(row[0])
#                    chan_type = str(row[1])
#                    array = cPickle.loads(str(row[3]))                
#                    found = False
#                    
#                    # Check if the vecREf exists.
#                    # If it does we add the variable vec to the vecs dict
#                    # otherwise we create a new one.
#                    
#                    for synVecRef in synVecRefs:
#                        if synVecRef.sec_name == sec_name:
#                            if synVecRef.chan_type == chan_type:
#                                found = True
#                                break
#                    if found:
#                        synVecRef.syn_vecs[var] = array
#                        continue #Move to next record
#                    else:
#                        nrn_sec = eval('h.' + sec_name)
#                        syn_vecs = {}
#                        syn_vecs[var] = array
#                        synVecRef = SynVecRef(chan_type, sec_name, syn_vecs)        
#                        
#                    
#                    synVecRefs.append(synVecRef)
#                    
#            self.synVecRefs = synVecRefs
            
    def _load_geom(self, session):
        """Select the NeuroML from the table, write it to a tmp file and then load into NEURON"""
        
        xml_data = ''
        for neuroml, in session.query(Geometry.neuroml):
            xml_data = str(neuroml)
        
        
        print type(xml_data)
        tmp_file = 'temp.xml'
        f = open(tmp_file, 'w')
        f.write(xml_data)
        f.close()
        
        import rdxml # This has to go ASAP they fix NEURON install
        h.load_file('celbild.hoc')
        cb = h.CellBuild(0)
        cb.manage.neuroml(tmp_file)
        cb.cexport(1)
        
        os.remove(tmp_file)
        
        
    def load_db(self, path_to_sqlite):
        """Loads the database in the Neuronvisio structure"""
        db_path = 'sqlite:////' + path_to_sqlite
        engine = create_engine(db_path, echo=False)
        Session.configure(bind=engine)
        Base.metadata.create_all(engine)
        session = Session()
        # Loading the geometry
        self._load_geom(session)
         
#        # Loading the VecRef
        self._load_vecRef(session)
#        
#        # Loading the SynVec
        #self._load_synVec(session)
        
            
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
        
        
    def __str__(self):
        return "section: %s, vars recorded: %s" %(self.sec_name, 
                                                  self.vecs.keys())
            
class SynVecRef(object):
    """Class to track all the synapse quantity of interest"""
    
    def __init__(self, chan_type, section_name, syn_vecs):
        """Create a synVecRef object which map the synapse position and name 
        and the recorded vectors in it.
        
        :param chan_type: The channel in the synapse
        :param sectiona_name: Name of the section where the synapse is
        :param syn_vecs: Dictionary with the synapse vecs
        """
        self.chan_type = chan_type
#        print "Creating synVec: syn type %s, synvec type %s" %(syn.chan_type,
#                                                               self.chan_type)
#        print "syn Vectors %s" %syn.syn_vecs
        self.sec_name = section_name
        self.syn_vecs = syn_vecs

    def __str__(self):
        return "section: %s, chan_type: %s, \
        vars recorded: %s" %(self.sec_name, self.chan_type, self.syn_vecs.keys())
        