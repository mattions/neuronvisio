"""
This example comes with NeuronVisio.
Cell model taken from the paper:

NEURON and Python
Hines et al.
Frontiers in Neuroinformatics 
(2009)
DOI 10.3389/neuro.11/001.2009 

"""

from itertools import chain

# Importing Neuronvisio
from neuronvisio.controls import Controls
controls = Controls()

# Importing the hoc interpreter
from neuron import h

# topology
soma = h.Section(name='soma')
apical = h.Section(name='apical')
basilar = h.Section(name='basilar')
axon = h.Section(name='axon')

apical.connect(soma, 1, 0)
basilar.connect(soma , 0, 0)
axon.connect(soma, 0, 0)

# geometry      
soma.L = 30    
soma.nseg = 1 
soma.diam = 30
                                                                          
apical.L = 600                       
apical.nseg = 23                     
apical.diam = 1                      
                                     
basilar.L = 200
basilar.nseg = 5                  
basilar.diam = 2
                
                                       
axon.L = 1000                         
axon.nseg = 37                       
axon.diam = 1                        
                                     
# biophysics
for sec in h.allsec(): 
     sec.Ra = 100      
     sec.cm = 1         

soma.insert('hh')                  
                                   
                                   
apical.insert('pas')           
                                   
basilar.insert('pas')                   
                                   
for seg in chain (apical, basilar ):
     seg.pas.g = 0.0002             
     seg.pas.e = -65                

axon.insert('hh')                  


# --------------------- Instrumentation ---------------------
# synaptic input
syn = h.AlphaSynapse(0.5, sec=soma)
syn.onset = 0.5
syn.gmax = 0.05
syn.e = 0
