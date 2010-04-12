# Author Michele Mattioni
# date Mon Apr 12 11:47:33 BST 2010

"""
Tables used by Neuronvisio
"""

from sqlalchemy import Column, Integer, String, PickleType
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Geometry(Base):
    
    __tablename__ = 'geometry'
    
    id = Column(Integer, primary_key=True)
    neuroml = Column(String)

class Vectors(Base):
    
    __tablename__ = 'vectors'
    
    id = Column(Integer, primary_key=True)
    x = Column(PickleType)
    y = Column(PickleType)
    x_label = Column(String)
    y_label = Column(String)
    sec_name = Column(String)

    def __init__(self, x, y, x_label, y_label, sec_name):
         self.x = x
         self.y = y
         self.x_label = x_label
         self.y_label = y_label
         self.sec_name = sec_name
         