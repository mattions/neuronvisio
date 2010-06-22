**************************************
Saving and loading simulations' reults
**************************************


HDF structure
=============

Neuronvisio stores simulation's results using the hdf_ standard, using PyTables_  This is very handy 
when you simulation takes a long time to run and you want to inspect again the results, 
without re-run it.

.. _hdf: http://www.hdfgroup.org/
.. _PyTables: http://www.pytables.org

The file has a structure shown in the following images

.. image:: images/hdf_neuronvisio_0.5_structure.png
    :scale: 30
    
The Refs is the data structure used by Neuronvisio. The `VecRef` is the specialized one. It is possible to add more 
Ref subclassing the :class:`manager.BaseRef`.

Using the manager object to store the results of your simulation
----------------------------------------------------------------

This is a quick example how to save the simulation in neuronvisio::
    
    # Model geometry already instantiated. 
    #   
    from neuronvisio.manager import Manager
    manager = Manager()
    manager.add_all_vecRef('v') # Adding vector for the variable v
    
    # file where to save the results
    filename = 'storage.h5'
    # Saving the vectors
    manager.save_to_hdf(filename)
    
If you run a lot of simulations you want maybe to run the same script but without rewriting 
the same results. Manager has a nice method to help you called create_new_dir::
    
    saving_dir = manager.create_new_dir() # Create a new dir per Simulation, ordered by Day.
    hdf_name = 'storage.h5'
    filename = os.path.join(saving_dir, hdf_name)
    # Saving the vectors
    manager.save_to_hdf(filename)

Loading a previous simulation
-----------------------------

To load the results of a simulation you can start neuronvisio giving the path_to_the_hdf_file::

    $ nrnvisio path/to/storage.h5
    
or you can just start neuronvisio and use the Load button::

    $ nrnvisio

Saving your variables in storage.h5 and use Neuronvisio to plot them 
====================================================================

To be able to save your own variable you need to subclass the BaseRef and then add the to the manager.

To subclass the BaseRef just create a class::

    from neuronvisio.manager import BaseRef 
    
    class MyRef(BaseRef):
        
        def __init__(self, sec_name=None, vecs=None, detail=None):
            
            BaseRef.__init__(self)
            self.sec_name = sec_name
            self.vecs = vecs
            self.detail = detail


Then you can create it::

    myRef = MyRef(sec_name=sec_name, 
                  vecs=vecs,
                  detail=detail)
        
sec_name should be the name of the section, vecs is a dictionary with the variable name as key and a 
python_list as value. A numpy array or an HocVector is also accepted.

After that you can add to the manager using the `manager.add_ref` which takes two arg:

    - the myRef object
    - the x variable.
    
The x variable is the independent one which will be used to plot the from the Neuronvisio graphical interface. If you don't have
a time to supply, but you want to use the one from NEURON directly, you can use the `manager.groups['t']` which will return an array::
 
    manager.add_ref(timeseriesRef, x)

All together is::

    class MyRef(BaseRef):
    
        def __init__(self, sec_name=None, vecs=None, detail=None):
            
            BaseRef.__init__(self)
            self.sec_name = sec_name
            self.vecs = vecs
            self.detail = detail
    
    
    myRef = MyRef(sec_name=sec_name, 
              vecs=vecs,
              detail=detail)
    manager.add_ref(myRef, x)
                  
Then you just need to save the file normally::
    
    filename = 'storage.h5'
    # Saving the vectors
    manager.save_to_hdf(filename)

When you reload the simulation you will have your variables back        

.. image:: images/Neuronvisio_Refs.png