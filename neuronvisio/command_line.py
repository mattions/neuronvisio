"""Module to handle commandline beahviour"""

import sys

def _load_neuronvisio(ipshell):
    """General method to load neuronvisio specific code. 
    params:
        ipshell - IPython interactive shell, obtained either from the current 
                  session, or created ad hoc."""

    ipshell.run_cell("import sys")
#     ipshell.run_cell("from neuron import h; h('nrn_load_dll(\"$(NEURONHOME)/stdrun.hoc\")')")
    ipshell.run_cell("from neuronvisio.controls import Controls")
    ipshell.run_cell("controls = Controls()")
    if len(sys.argv) == 2:
        ipshell.run_cell("controls.load(sys.argv[1])")
    return ipshell


def main_neuronvisio():
    try: 
        # check if inside an ipython session
        # Not need to launch ipshell() at the end, 'cause already running
        ipshell = get_ipython() 
        ipshell = _load_neuronvisio(ipshell)
        
        
    except NameError: 
        # Not IPython running, create an ad hoc ipshell and launching.
        from IPython.terminal.embed import InteractiveShellEmbed
        ipshell = InteractiveShellEmbed(display_banner=False)
        ipshell = _load_neuronvisio(ipshell)
        ipshell()

    else:
        # Define a dummy ipshell() so the same code doesn't crash inside an
        # interactive IPython
        def ipshell(): pass

def main_model_updater():
    """Updates the ModelDB.xml in the current location"""

    import os
    import logging
    
    import neuronvisio.modeldb
    from neuronvisio.modeldb.Updater import ModelDBUpdater
    
    h = logging.StreamHandler(sys.stderr)
    h.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(h)
    logging.getLogger().setLevel(logging.INFO)
    
    # Update models
    path_to_module_dir = neuronvisio.modeldb.__path__[0]
    print path_to_module_dir
    path_to_file = os.path.join(path_to_module_dir, 'ModelDB.xml')    
    updater = ModelDBUpdater(path_to_file)
    updater.update()