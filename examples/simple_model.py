# This example comes with NeuronVisio.

# Importing the NeuronVisio
import nrnVisio

# Importing hoc interpreter
from neuron import h

# simple model
soma = h.Section()
dend1 = h.Section()
dend2 = h.Section()
soma.diam = 10
dend1.diam = 3
dend2.diam = 3  
dend1.connect(soma)
dend2.connect(soma)
