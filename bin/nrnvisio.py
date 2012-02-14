#!/usr/bin/env python
# Author Michele Mattioni
# Fri Apr  9 11:35:29 BST 2010

"""Main script to start Neuronvisio.

It creates a IPython shell and loads neuronvisio inside it."""

def load_neuronvisio(ipshell):
    """General method to load neuronvisio specific code. 
    params:
        ipshell - IPython interactive shell, obtained either from the current 
                  session, or created ad hoc."""

    ipshell.run_cell("import sys")
    ipshell.run_cell("from neuronvisio.controls import Controls")
    ipshell.run_cell("controls = Controls()")
    if len(sys.argv) == 2:
        ipshell.run_cell("controls.load(sys.argv[1])")
    return ipshell

if __name__ == '__main__':

    try: 
        # check if inside an ipython session
        # Not need to launch ipshell() at the end, 'cause already running
        ipshell = get_ipython() 
        ipshell = load_neuronvisio(ipshell)
        
        
    except NameError: 
        # Not IPython running, create an ad hoc ipshell and launching.
        from IPython.frontend.terminal.embed import InteractiveShellEmbed
        ipshell = InteractiveShellEmbed()
        ipshell = load_neuronvisio(ipshell)
        ipshell()

    else:
        # Define a dummy ipshell() so the same code doesn't crash inside an
        # interactive IPython
        def ipshell(): pass
