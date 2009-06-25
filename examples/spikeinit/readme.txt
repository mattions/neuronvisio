This model is associated with the paper:

A model of spike initiation in neocortical pyramidal neurons 
Z. F. Mainen, J. Joerges, J. R. Huguenard and T. J. Sejnowski 
Neuron 15, 1427-1439 (1995)


Please see 

http://www.cnl.salk.edu/~zach/methods.html

where a full text (postscript format) copy of the paper
and copies of the model for early versions of neuron is available.

This model contains compartmental models of a reconstructed neocortical
neuron with active dendritic currents using NEURON. This paper examines
the paradox that although spikes can back-propagate from the soma into dendrites 
with spike amplitudes maintained in dendrites by voltage-gated channels it rarely
occurs that spikes are initiated in dendrites in these cells. The model suggests
that dendritic channel inactivation and source-load considerations are contributing
factors. See the paper for more details.

This package is written in the NEURON simulation program written by Michael
Hines and available on internet at:
http://www.neuron.yale.edu/


  HOW TO RUN (under NEURON version 5 and higher)
  =========================================

To compile the demo, NEURON and INTERVIEWS must be installed and working on
the machine you are using.

When the spikeinit.zip file is unzipped it creates a spikeinit directory which
contains the hoc and mod NEURON program files.  Change directory to spikeinit.

under UNIX:
===========

Just type "nrnivmodl" to compile the mechanisms
given in the mod files in the  directory.

Execute the first figure demo program by typing:

nrngui demo.hoc

continue below under back to any platform:

under MS WINDOWS (PC):
======================

Press Start button (lower left corner) and then press Programs and then
NEURON and then mknrndll.  Change directory to where the zip file was
unzipped and enter the directory that came with the zip file (spikeinit).
Press the nrnmech.dll button.

You can start the simulation by a double click on
demo.hoc
in windows explorer.

The simulation produces fig 3 from the paper.
