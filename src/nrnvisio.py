#!/usr/bin/env python
# Author Michele Mattioni
# Fri Apr  9 11:35:29 BST 2010

"""Main script to start Neuronvisio.

It creates a IPython shell and loads neuronvisio inside it."""


if __name__ == '__main__':

    # Duplicate code, 'cause IPython returns a function if called outside the 
    # try block. Could be imporved if a better way comes up.
    cell1 = "import sys"
    cell2 = "from neuronvisio.controls import Controls"
    cell3 = "controls = Controls()"
    cell4 = "controls.load(sys.argv[1]"

    try:
        ipshell = get_ipython()
        ipshell.run_cell(cell1)
        ipshell.run_cell(cell2)
        ipshell.run_cell(cell3)
        if len(sys.argv) == 2:
            ipshell.run_cell(cell4)
        
    except NameError:
        from IPython.frontend.terminal.embed import InteractiveShellEmbed
        ipshell = InteractiveShellEmbed()
        ipshell.run_cell(cell1)
        ipshell.run_cell(cell2)
        ipshell.run_cell(cell3)
        if len(sys.argv) == 2:
            ipshell.run_cell(cell4)
        ipshell()

    else:
        # Define a dummy ipshell() so the same code doesn't crash inside an
        # interactive IPython
        def ipshell(): pass
