# This example comes with NeuronVisio.

# The model is the ported one from the NeuroML website
# http://www.neuroconstruct.org/samples/index.html#Ex6_CerebellumDemo-N101EA

# You need to compile the hoc file before launching it
# $ nrnivmodl 

# Importing Neuronvisio
from neuronvisio.controls import Controls
controls = Controls()

# loading the model
# importing the interview so the GUI does not freeze
# Uncomment this if you want to use also the interview GUI
#import neuron.gui

# Load the script
h.load_file("Ex6_CerebellumDemo.hoc")

# Uncomment, or copy paste in the ipython console to record and run our vectors

# Record the voltage for all the sections
#controls.manager.add_all_vecRef('v')

# Initializing also our vectors
#controls.init()

# Run
#controls.run()