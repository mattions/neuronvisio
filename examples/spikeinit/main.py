# This example comes with NeuronVisio.

# Importing the NeuronVisio
import nrnVisio

# Importing hoc interpreter
from neuron import h

# loading the model
# importing the interview so the GUI does not freeze
# Uncomment this if you use the interview GUI
#import neuron.gui

# Load the script
h.load_file("demo.hoc")

## Insert an IClamp
st = h.IClamp(0.5, sec=h.soma)
st.amp = 0.25
st.delay = 3
st.dur = 40