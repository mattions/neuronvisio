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

""":synopsis: Manage the map between vectors and sections"""

from neuron import h
import numpy as np
import os
import tables
import datetime
import matplotlib
import matplotlib.pyplot as plt
import logging
logger = logging.getLogger(__name__)


class Manager(object):
    """The Manager class can be used as a library and imported on cluster 
    simulation. Refer to the online doc for how to save in HDF5 and how to 
    create New Generic Ref.
    """

    def __init__(self):
        
        self.groups = {}
#        self.vecRefs = [] 
#        self.synVecRefs = []
        self.refs = {}
        self.results_root = 'results'
        self.geometry_root = 'geometry'
        self.geometry_node_name = 'geom'        
        # Load the std run for NEURON
        h.load_file("stdrun.hoc")
        
    def add_vecRef(self, var, sec, 
                   time_interval_recording=None, 
                   point_process=None):
        """Add the vecRef to the vec_res list. It takes care to create the vector 
        and record the given variable.
        
        :param var: The variable to record
        :param sec: The section where to record
        :param time_interval_recording: If None, use the dt of Neuron. 
                    Specify which interval to use to record the vectors. 
                    Note the same resolution should apply to the time 
                    vectors.
        :return: True if the vector is created successfully.
        
        """
            
        success = False
        if hasattr(sec, var):
            # Adding the vector only if does not exist
            alreadyPresent=False
            if self.refs.has_key('VecRef'):
                for vecRef in self.refs['VecRef']:
                    if vecRef.sec_name == sec.name():
                        if vecRef.vecs.has_key(var):
                            alreadyPresent = True
                            break
                        else: # Adding a variable to an existing vecRef
                            vec = h.Vector()
                            varRef = '_ref_' + var
                            if time_interval_recording is None:
                                if point_process is not None:
                                    vec.record(point_process, 
                                               getattr(sec(0.5), varRef))
                                else:
                                    vec.record(getattr(sec(0.5), varRef))
                            else:
                                if point_process is not None:
                                    vec.record(point_process,
                                               getattr(sec(0.5), varRef), 
                                               time_interval_recording)
                                else:
                                    vec.record(getattr(sec(0.5), varRef), 
                                               time_interval_recording)
                                    
                            vecRef.vecs[var] = vec
                            alreadyPresent = True
                            success = True
                 
            if not alreadyPresent:
                    
                # Creating the vector
                vec = self.create_record_vector(sec, 
                                                var, 
                                                time_interval_recording)
                                                
                # Adding to the list
                vecRef = VecRef(sec)
                vecRef.vecs[var] = vec
                name = vecRef.__class__.__name__
                if self.groups.has_key('t'):
                    t = self.groups['t']
                else: 
                    t = self.create_time_record(time_interval_recording)
                self.add_ref(vecRef, t)
                success = True
        return success
    
    def add_all_vecRef(self, var, 
                       time_interval_recording=None, 
                       point_process=None):
        """Create the vector for all the section present in the model 
        with the given variable
        :param var: The variable to record"""
        
        done = False
        responses = []
        for sec in h.allsec():
            response = self.add_vecRef(var, 
                                       sec, 
                                       time_interval_recording,
                                       point_process)
            responses.append(response)
        if all(responses) != True:
            logger.warning( "Warning: Some vectors could not be added.")
    
    
    def add_ref(self, generic_ref, x):
        """Add a generic ref to manager.refs dictionary. If a list of the ref of 
        the same type is already present, the `genercref` will be added, otherwise the list
        will be created.
        `x` is the indipendent variable which should be used to when the genericref is 
        plotted from the Neuronvisio UI. 
        
        `generic_ref` -- the ref to add to the manager.ref list
        `x` -- indipendent varialbe use to plot the variable from the genericref"""
        name = generic_ref.group_id
        if self.refs.has_key(name):
            self.refs[name].append(generic_ref)
        else:
            self.refs[name] = [generic_ref]
            self.groups[name] = x
            
    def add_synVecRef(self, synapse):
        """Add the synVecRef object to the list
        
        :param synapse: The synapse to record.
        """
        synVecRef = SynVecRef(synapse.chan_type, synapse.section.name(), 
                              synapse.vecs)
            
        self.add_ref(synVecRef, self.groups['t'])
    
    
    
    def find_point_process(self, sec):
        """Find a point_process in a section if any.
        
        Params:
            sec - Section to search
            
        Return:
            point_process or None if not present.
        """
        mt = h.MechanismType(1)
        total_mech = int(mt.count())
        sec.push()
        pp = None
        for i in range(total_mech):
            pp_type = mt.select(i)
            pp = mt.pp_begin()
            if pp is not None:
                break
            
        h.pop_section()
        return pp

    def create_record_vector(self, sec, var, time_interval_recording):
        """Create the vector which will record the variable
        Will pass the first pointprocess to make sure the recording 
        are thread safe."""
        
        # Getting the first pp if any
        
        point_process = self.find_point_process(sec)
            
        vec = h.Vector()
        varRef = '_ref_' + var
        
        
        try:
            if time_interval_recording:
                if point_process:
                    vec.record(point_process, 
                               getattr(sec(0.5), varRef), 
                               time_interval_recording)
                    logging.info( "Sec: %s has pp: %s" %(sec.name(), point_process))
                else:
                    vec.record(getattr(sec(0.5), varRef), 
                               time_interval_recording)
                    logging.info( "Sec: %s has not pp" %(sec.name()))
            else:
                if point_process:
                    vec.record(point_process, 
                               getattr(sec(0.5), varRef))
                else:
                    vec.record(getattr(sec(0.5), varRef))
                
            
        except NameError:
            logging.error( "The variable %s is not present in the section %s" \
            % (varRef, sec.name()))
        
        h.pop_section()
        return vec
    
    def create_time_record(self, time_interval_recording=None, point_process=None):
        """Create the vector to record time. If not time_interval specified the 
        NEURON default is used."""
        t = h.Vector()
        if time_interval_recording:
            if point_process: 
                t.record(point_process, 
                         h._ref_t, time_interval_recording)
            else:
                t.record(h._ref_t, time_interval_recording)
        else:
            if point_process: 
                t.record(point_process, 
                         h._ref_t)
            else:
                t.record(h._ref_t)
        self.groups['t'] = t
        return t
    

            
    def get_vector(self, sec, var, group='VecRef'):
        """Return the vec that record the var in a given section
        
        :param sec: Section of interest or the name of the section
        :param var: variable recorded by the vector.
        :return: the vector that record the variable var"""
        
        name = sec
        if hasattr(sec, 'name'):
            name = sec.name()
        for ref in self.refs[group]:
                if ref.sec_name == name:
                    if ref.vecs.has_key(var):
                       return ref.vecs[var]
    def get_time(self):
        """Return the vector time associated with the voltage"""
        return self.groups['t']
    
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
        h.pop_section()
        return tree
                
    def plot_vecs(self, vecs_dic, x=None, legend=True, figure_num=None, points=False):
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
            if points:
                if x is None:
                    plt.plot(self.groups['t'], vec, 'o', label=key)
                elif len(x) != len(vec):
                    plt.plot(vec, 'o', label=key)
                    logging.warning("x and y mismatched. Is the %s wrapped in the right baseref? \
                    Plotted vs it's it own length anyway." %key)
                else:
                    plt.plot(x, vec, 'o', label=key)
            else:
                if x is None:
                    plt.plot(self.groups['t'], vec, label=key)
                elif len(x) != len(vec):
                    plt.plot(vec, label=key)
                    s = "x and y mismatched. Is the %s wrapped in the right baseref?\
                     Plotted vs it's it own length anyway." %key
                    logger.info(s)
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
        
    def sanitized_sec(self, sec_name):
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
        return sec
        
    def _save_geom(self, h5file_holder):
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
        geom_group = h5file_holder.createGroup('/', self.geometry_root)
        h5file_holder.createArray(geom_group, self.geometry_node_name, 
                                  [xml_data])
        os.remove(tmp_file)
        
    
    def save_to_hdf(self, filename):
        try:
            self.get_time()
            h5f = tables.openFile(filename, 'w')
            self._save_geom(h5f)
            res = h5f.createGroup('/', self.results_root)
            for group in self.refs:
                self._save_baseRef(self.refs[group], h5f, res)
            h5f.close()
        except KeyError:
            logger.warning("No vectors have been created. The file will not be saved.")
            
        
    def _save_baseRef(self, baseRefs, h5f_holder, base_group):
        """Save the baseRef in the database"""
        
        target_group = ''
        for baseRef in baseRefs:
            baseRefName = baseRef.group_id
            found = False
            
            for group in h5f_holder.walkGroups('/'):
                if group._v_name == baseRefName:
                    target_group = group
                    found = True
                    break
            
            if not found:
                # Creating the group    
                target_group = h5f_holder.createGroup(base_group, 
                                                      baseRefName)
                
                # Saving the time
                key = target_group._v_name
                x_array = None
                if hasattr(self.groups[key], 'to_python'):    
                    x_array = np.array(self.groups[key])
                else: 
                    x_array = self.groups[key]
                    
                h5f_holder.createArray(target_group, 'x', x_array)
            
            section_name = self.sanitized_sec(baseRef.sec_name)
            detail = ''
            if hasattr(baseRef, 'detail'):
                detail = baseRef.detail
            self.save_node(h5f_holder, target_group, section_name, 
                           baseRef.vecs, detail=detail)
    
    def save_node(self, h5file_holder, group_path, section_name, variables, 
                  detail=''):
        """Save a node to the h5file.
        h5file_holder: The holder of the h5file
        group_path: Where in the hierarchy the leaf has to be saved
        section_name: The name of the section which the variables belong to
        variables: The dictionary of the variable
        """
        found = False
        target_group = None
        for group in h5file_holder.walkGroups(group_path):
            if group._v_name == section_name:
                target_group = group
                found = True
                break
        if not found:
            target_group = h5file_holder.createGroup(group_path, 
                                                     section_name)
        tmp_array = np.array(self.groups['t'])
        for var, vec in variables.iteritems():
            if len (vec) != 0 :
                if hasattr(vec, 'to_python'): # Vector to numpy Array
                    if len(tmp_array) == len(vec):
                        vec = vec.to_python(tmp_array) # Swap in place
                    else:
                        vec =  vec.to_python() # Creating a list
                h5file_holder.createArray(target_group, var, 
                                          vec,
                                          title=detail)
        
    def load_from_hdf(self, filename):
        """Load all the results on the hvf in memory"""
        logger.info( "Loading: %s" %filename)
        self._load_geom(filename)
        self._load_allRef(filename)
        
    
    def _load_geom(self, filename):
        """Load the geometry of the model"""
        
        h5f = tables.openFile(filename)
        node = "/%s/%s" %(self.geometry_root, self.geometry_node_name) 
        geom = h5f.getNode(node)
        xml_data = geom[0]  # get the string.
        
        tmp_file = 'temp.xml'
        f = open(tmp_file, 'w')
        f.write(xml_data)
        f.close()
        
#        import rdxml # This has to go ASAP they fix NEURON install
        h.load_file('celbild.hoc')
        cb = h.CellBuild(0)
        cb.manage.neuroml(tmp_file)
        cb.cexport(1)
        
        os.remove(tmp_file)
    
    def _load_allRef(self, filename):
        """Load the vecref in memory"""
        
         
        h5f = tables.openFile(filename)
        res_group_path = "/%s" %self.results_root
        for group in h5f.iterNodes(where=res_group_path): # Get the type

            # Indipendent var (time for ex)
            x_node = h5f.getNode(group, name='x')
            self.groups[group._v_name] = x_node        
            for group_child in h5f.iterNodes(group): # Get the section name
                if group_child._v_name != 'x':
                    vecs = {}
                    genericRef = None
                    group_ref = group._v_name 
                    sec_name = group_child._v_name
                     
                    if group_ref == 'VecRef':
                        self.groups['t'] = self.groups[group_ref]
                        # Create vecRef
                        nrn_sec = eval('h.' + sec_name)
                        genericRef = VecRef(nrn_sec)
                        
                    else:
                        genericRef = BaseRef() # Creating a genericRef
                        genericRef.sec_name = sec_name
                        
                    genericRef.group_id = group_ref
                    
                    if self.refs.has_key(group_ref):
                        self.refs[group_ref].append(genericRef)
                    else:
                        self.refs[group_ref] = [genericRef]
                    
                    vecs ={}   
                    for node in h5f.iterNodes(where= group_child, 
                                              classname='Array'):
                        
                        vecs[node._v_name] = node
                        genericRef.vecs = vecs
                        genericRef.detail = node._v_title

    def get_distance(self, sections, base_sec):
        """Return a dictionary with section names as keys and 
        distance from base_sec to specified point as value in microns
        
        param:
         secs: list of section which distance need to be calculated
         base_sec: section from where the distance should be measured from."""
         
        distance_sec = {}
        for sec in sections:
            tree = self.get_tree(sec)
            distance = self._get_distance_in_tree(tree)
            distance -= base_sec.L
            distance_sec[sec.name()] = distance
        return distance_sec
    
    def _get_distance_in_tree(self, tree):
        """Calculate the distance in the tree adding the length of all the sections """
        dist = 0
        for sec in tree:
            dist += sec.L
        return dist
    
    def create_3d_grid(self, distance_dic, time, variable_dic):
        """Create the 3 grid (X,Y,Z) uses to plot wireframe or surface 3D 
        
        :param: distance_dic - dictionary with sections' names as key and 
        distance as a value
        :param: time - Time array
        :param: variable_dic - dictionary with sections' names as key and 
        array as value
        
        :rtype: tuple (X,Y,Z) numpy array"""
        # create a grid
        X_time, Y_distance = np.meshgrid(time, distance_dic.values())
        Z_variable = X_time*0
        xn, yn = X_time.shape 
        sec_names = distance_dic.keys()
        # xk iter on distance
        for xk in range(xn):
            # yk on time. It's the reverse of the grid.
            for yk in range(yn):
                var_array = variable_dic[sec_names[xk]]
                Z_variable[xk, yk] =  var_array[yk]
                
        return (X_time, Y_distance, Z_variable)
    
    def plot3D(self, sections, base_sec, var):
        """Wrap up module to plot in three Dimensions the voltage the distance and the time 
        :param: sections - list of section to consider
        :param: base_sec - section used as a starting pooint for the distance
        :param: var - variable to plot """
        
        # I know it's not suggested to import here, but this is pretty new 
        # module for matplotlib and this method is 
        # hardely executed.
        
        from mpl_toolkits.mplot3d import Axes3D
        from matplotlib import cm
        
        dist = self.get_distance(sections, base_sec)
        vecs = self.get_vectors(sections, var)
        X, Y, Z = self.create_3d_grid(dist, self.groups['t'], vecs)
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        surf = ax.plot_surface(X, Y, Z,  rstride=10, cstride=10, cmap=cm.jet,
                               linewidth=0, antialiased=False)
        fig.colorbar(surf, shrink=0.5, aspect=5)
        return fig
        #plt.show()


            
class BaseRef(object):
    """Base Ref class. Subclass it to create your own ref."""
    
    def __init__(self):
        """Initialize the attribute for the baseRef with empty string none"""
        
        self.sec_name = ''
        self.detail = ''
        self.vecs = {}
        self.group_id = self.__class__.__name__
    
    def __str__(self):
        s = "section: %s, detail: %s, vars recorded: %s" %(self.sec_name, 
                                                              self.detail, 
                                                              self.vecs.keys())
        return s
                
class VecRef(BaseRef):
    """Specialized class for HocVectors class to associate one or more vectors with a section
    """
    def __init__(self, sec):
        """Create a vecRef object which map the section name and the 
        recorded vectors.
        
        :param sec: The section which all the vectors belong
        """
        
        BaseRef.__init__(self)
        self.sec_name = sec.name()
        self.sec = sec
        self.pickable = False
        #Dict with all the vecs
        # Key: var Value: Hoc.Vector
        self.vecs = {}
        
        
    def __str__(self):
        return "section: %s, vars recorded: %s" %(self.sec_name, 
                                                  self.vecs.keys())
            
class SynVecRef(BaseRef):
    """Class to track all the synapse quantity of interest"""
    
    def __init__(self, chan_type=None, section_name=None, vecs=None):
        """Create a synVecRef object which map the synapse position and name 
        and the recorded vectors in it.
        
        :param chan_type: The channel in the synapse
        :param section_name: Name of the section where the synapse is
        :param vecs: Dictionary with the synapse vecs
        """
        BaseRef.__init__(self)
        self.detail = chan_type
        self.sec_name = section_name
        self.vecs = vecs

    def __str__(self):
        return "section: %s, chan_type: %s, \
        vars recorded: %s" %(self.sec_name, self.detail, self.vecs.keys())
        