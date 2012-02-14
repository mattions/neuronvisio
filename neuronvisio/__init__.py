#"""
#NeuronVisio is a Graphical User Interface for NEURON simulator enviroment
#
#Copyright (c) 2009, Michele Mattioni
#All rights reserved.
#
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#"""

__authors__ = ['Michele Mattioni <mattioni@ebi.ac.uk>', 
               'Uri Cohen <uri.cohen@alice.nc.huji.ac.il>']
__version__ = '0.8.0.dev'


import os
# this add the commit of to the software version when run from a git repo
try:
    import git
    if git.__version__ == '0.3.1':
        if git.repo.fun.is_git_dir(os.path.join(root, ".git")):
            r = git.Repo(root)
            git_commit = r.head.commit.hexsha
            __version__ = __version__ + ' : ' + git_commit
        raise ImportError
except ImportError:
    pass
