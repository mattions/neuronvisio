# This example comes with NeuronVisio.

# In this example we show how to load a model written in hoc with neruonvisio and explore
# it.

# The model that I choose is: 
# A model of spike initiation in neocortical pyramidal neurons 
# Z. F. Mainen, J. Joerges, J. R. Huguenard and T. J. Sejnowski 
# Neuron 15, 1427-1439 (1995)

# From the original demo I deleted the synapses and the interview panel for clarity.


# You need to compile the hoc file before launching it
# $ nrnivmodl 

# Importing Neuronvisio
from neuronvisio.controls import Controls
controls = Controls()

# Importing hoc interpreter
from neuron import h

# loading the model
# importing the interview so the GUI does not freeze
# Uncomment this if you want to use also the interview GUI
#import neuron.gui

# Load the script
h.load_file("demo.hoc")


## Insert an IClamp
st = h.IClamp(0.5, sec=h.soma)
st.amp = 0.25
st.delay = 3
st.dur = 40
