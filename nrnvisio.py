#!/usr/bin/env python
# Author Michele Mattioni
# Fri Apr  9 11:35:29 BST 2010

"""Main script to start Neuronvisio"""

from neuronvisio.controls import Controls
import sys


if __name__ == '__main__':
    
    controls = Controls()
    if len(sys.argv) == 2:
        controls.load_hdf(sys.argv[1])
    
         