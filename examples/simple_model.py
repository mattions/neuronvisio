# Importing the NeuronVisio

import nrnVisio

# creating the gtk2 window and startin the thread.
controls = nrnVisio.Controls()
controls.start() 

# handy h interpreter
h = controls.visio.h

# Kiddy model
soma = h.Section()
dend1 = h.Section()
dend2 = h.Section()
soma.diam = 10
dend1.diam = 3
dend2.diam = 3  
dend1.connect(soma)
dend2.connect(soma)
