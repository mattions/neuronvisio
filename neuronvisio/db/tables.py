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
    vec = Column(PickleType)
    var = Column(Text)
    sec_name = Column(Text)
    details = Column(Text)
         
class SynVectors(Base):
    
    __tablename__ = 'synvectors'
    
    id = Column(Integer, primary_key=True)
    var = Column(Text)
    vec = Column(PickleType)
    sec_name = Column(Text)
    details = Column(Text)
         