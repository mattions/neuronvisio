# Author Michele Mattioni
# date Mon Apr 12 11:47:33 BST 2010

"""
Tables used by Neuronvisio
"""

from sqlalchemy import Column, Integer, Text, PickleType
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Geometry(Base):
    
    __tablename__ = 'geometry'
    
    id = Column(Integer, primary_key=True)
    neuroml = Column(Text)

class Vectors(Base):
    
    __tablename__ = 'vectors'
    
    id = Column(Integer, primary_key=True)
    x = Column(PickleType)
    y = Column(PickleType)
    x_label = Column(Text)
    y_label = Column(Text)
    sec_name = Column(Text)

    def __init__(self, x, y, x_label, y_label, sec_name):
        
         self.x = x
         self.y = y
         self.x_label = x_label
         self.y_label = y_label
         self.sec_name = sec_name
         