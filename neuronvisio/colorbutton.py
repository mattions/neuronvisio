"""
colorbutton.py

A tool button that enables the user to select colors using a color dialog.

Copyright (C) 2007 David Boddie <david@boddie.org.uk>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class ColorButton(QToolButton):

    __pyqtSignals__ = ("colorChanged(QColor)")
    
    def __init__(self, parent = None):
    
        QToolButton.__init__(self, parent)
        self.connect(self, SIGNAL("clicked()"), self.chooseColor)
        self._color = QColor()
    
    def chooseColor(self):
    
        rgba, valid = QColorDialog.getRgba(self._color.rgba(), self.parentWidget())
        if valid:
            color = QColor.fromRgba(rgba)
            self.setColor(color)
    
    def color(self):
    
        return self._color
    
    @pyqtSignature("QColor")
    def setColor(self, color):
    
        if color != self._color:
            self._color = color
            self.emit(SIGNAL("colorChanged(QColor)"), self._color)
            pixmap = QPixmap(16, 16)
            pixmap.fill(color)
            self.setIcon(QIcon(pixmap))
    
    color = pyqtProperty("QColor", color, setColor)
