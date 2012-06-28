Network example visualized with Neuronvisio
===========================================

This directory contains the [Cerebellum example] (http://www.neuroconstruct.org/samples/index.html#Ex6_CerebellumDemo-N101EA) in two forms:

- the generated hoc from [neuroConstruct] (http://www.neuroconstruct.org)
- the Network NeuroML (Level 3, version 1.8)

note: This model is only for demonstration of networks visualization, and 
it should be not used as starting point to develop new model, because the channels
value are not verified.

To run the hoc version
----------------------

    cd hoc
    
start an ipython session

    ipython 
    
and then load the main.py

    run main.py

Before every run you need to clear the compiled mod files.


To run the NeuroML
------------------

you can load the NeuroML with

    neuronvisio Ex6_Cerebellum_networks.xml

makes sure the path to Ex6_Cerebellum_networks.xml is complete

