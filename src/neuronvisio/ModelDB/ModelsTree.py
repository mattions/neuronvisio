#!/bin/env python

class ModelsTree:
	_treeList = []
	
	def __init__(self, models):
		names = models.getModelNames()
		self._treeList.append(('Recent Additions/Updates', []))
		self._treeList.append(('Local Models', []))
		self._treeList.append(('Marked Models', []))
		self._treeList.append(('Models (' + str(len(names)) + ')', names))
	
	def getTree(self):
		return self._treeList
