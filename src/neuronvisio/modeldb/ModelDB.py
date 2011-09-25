#!/bin/env python
import types
import string
import re
import os
import xml.etree.ElementTree
import urllib
import zipfile
import logging 

logger = logging.getLogger(__name__)


# TODO: those are general functionality, move to better place
def to_text(t):
    if (type(t) == types.ListType):
        t=string.join(t, ',')
    if (type(t) == types.NoneType):
        t=''
    t=t.strip()
    return t

# Implementation taken from SO
# http://stackoverflow.com/questions/2878712/make-os-open-directory-in-python
def start_file(filename):
    try:
        # Implementation for Windows
        f=filename.replace('/', '\\')
        os.startfile(f)
    except:
        # Implementation for Linux
        subprocess.Popen(['xdg-open', filename])

class Model(object):
    # Fields
    _model = None
    
    # Constants
    _MODEL_PROPERTIES = [('model_type', 0), ('model_concepts', 0),
                        ('transmitters', 0),('genes', 0), ('receptors', 0), ('brain_regions', 0),
                        ('channels', 0), ('cell_types', 0), ('gap_junctions', 0), 
                        ('implementers', 0),
                        ('simulation_environment', 0)]

    # Initialization
    def __init__(self, model):
        self._model = model

    # Public data accessors
    def get_properties(self):
        for (k, s) in self._MODEL_PROPERTIES:
            t=to_text(self._model[k])
            t=t.strip()
            if len(t) == 0: # Show only non-empty properties
                continue
            k=k.replace('_', ' ')
            k=k.title()
            yield (k, t)
            
    def get_name(self):
        return to_text(self._model['short_name'])

    def get_title(self):
        return to_text(self._model['title'])

    def get_description(self):
        return to_text(self._model['description'])

    def get_reference(self):
        return to_text(self._model['reference'])

    def get_url(self):
        return to_text(self._model['url'])

    def get_id(self):
        return to_text(self._model['model_id'])

    def get_authors(self):
        return to_text(self._model['short_authors'])

    def get_year(self):
        return to_text(self._model['year'])

    def get_readme(self):
        if self._model.has_key('readme') == False:
            return None
        return self._model['readme'][0]

    # Public operations and manipulations
    def exists_locally(self):
        return os.path.isdir(self._get_dir())

    def browse(self):
        if self.exists_locally():
            modelName = self.get_name()
            logger.info("Opening '" + self._get_dir()+"'.")
            start_file(self._get_dir())
        else:
            logger.info("Model does not exists locally")
        
    def download_model(self):
        modelId = self.get_id()
        if os.path.isdir('Models')==False:
            os.mkdir('Models')        
        zipFile = 'Models/'+modelId+'.zip'
        modelDir = self._get_dir()
        if not os.path.isdir(modelDir):
            if type(self._model['zip_url'])==types.NoneType:
                logger.info("No zip URL found for '" + self.get_name() + "'")
                return
            else:
                logger.info("Downloading model for '" + self.get_name() + "'")
                self._download_file(self._model['zip_url'][0], zipFile)
                logger.info("Download complete.")
                # TODO: open model data in tab
                # TODO: recolor, self.tree.SetItemColor(item, wx.Colour(100,10,255))
        else:
            logger.info("Model for '" + self.get_name() + "' already downloaded")
        self._extract_model(zipFile, modelDir)
        return modelDir

    # Access the internal dictionary
    def get_dictionary(self):
        return self._model

    # Private implementation methods
    def _get_dir(self):
        modelId = self.get_id()
        dirName = 'Models/'+modelId+'/'
        return dirName
        
    # Download model file from the network
    def _download_file(self, url, filename):
        logger.info("Creating " + filename)
        try:
            s = urllib.urlopen(url)
            f = open(filename, "wb")
            f.write(s.read())
            f.close()
        except Exception as e:
            logger.info("Error downloading file: "+e.message)
            return
        logger.info("Done.")

    # Extract model zip file
    # ModelDB zip files contain trailing garbage which should be removed
    # See 'ZIP end of central directory record' in http://en.wikipedia.org/wiki/ZIP_%28file_format%29
    def _extract_model(self, zipFile, modelDir):
        logger.info("Extracting '" + zipFile + "' into " + modelDir)
        try:
            f = open(zipFile, 'r+b')
            data = f.read()
            pos = data.find('\x50\x4b\x05\x06') # End of central directory signature
            if (pos > 0):
                logger.info("Trancating file at location " + str(pos + 22)+ ".")
                f.seek(pos + 22)                # size of 'ZIP end of central directory record'
                f.truncate()
                f.close()
            zip = zipfile.ZipFile(zipFile, 'r')
            dirs = {}
            for file in zip.namelist():
                dir = file[0:file.find('/')]
                if dirs.has_key(dir)==False:
                    dirs[dir]=0
                else:
                    dirs[dir]=dirs[dir]+1
                zip.extract(file, 'Models')
            zip.close()
            if len(dirs.keys()) == 1:
                os.rename('Models/' + dirs.keys()[0], modelDir)
            else:
                os.mkdir(modelDir)
                for d in dirs:
                    os.rename('Models/' + d, modelDir + d)
        except Exception as e:
            logger.info("Error extracting file: "+str(e.message))
        logger.info("Done.")

#---------------------------------------------------------------------------
class Models():
    # Fields
    _log = None
    _name_re = None   
    _modelList = []
    _modelTree = {}

    # public methods
    def __init__(self):
        self._name_re = re.compile("^\s*(.*)\(((.*)(\d{4}).*)\)")
        path = os.path.split(os.path.abspath(__file__))[0] # base absolute dir 
        self._modelList = self._generate_models_list(os.path.join(path, 'ModelDB.xml'))
        self._modelTree = self._generate_models_tree(self._modelList)        
        
    def get_model_names(self):
        return self._modelTree.keys()

    def has_model(self, modelName):
        return self._modelTree.has_key(modelName)

    def get_model(self, modelName):
        return Model(self._modelTree[modelName])

    def get_field(self, model, field):
        return to_text(self._modelTree[model][field])
    
    """ Returns whether a model contains the search keyword or not. """
    def search(self, name, keyword):
        return self._modelTree[name]['searchable'].find(keyword.lower()) >= 0
       
    # private methods
    def _generate_models_list(self, data):
        models=xml.etree.ElementTree.XML(open(data).read())
        list=[]
        for m in models:
            d={}
            for c in m._children:
                if (len(c._children)>0):
                    d[c.tag]=map((lambda a:a.text), c._children)
                else:
                    d[c.tag]=c.text
            list.append(d)
        return list

    def _generate_models_tree(self, list):
        tree={}
        for m in list:
            search=''
            for s in m.keys():
                search = search + "|" + to_text(m[s])
            m['searchable']=search.lower()
            name=m['name']
            [t, s, a, y]=self._get_title_authors_year_short_name(name)
            m['short_name']=s
            m['title']=t
            m['short_authors']=a
            m['year']=y
            c=to_text(m['citations']).strip()
            if len(c)>0:
                m['citations']=self._MODELDB_BASE_URL + c
            tree[s]=m
        return tree

    def _get_title_authors_year_short_name(self, name):
        m=self._name_re.match(name)
        if m:
            return m.groups()
        else:
            raise Exception("no match in " + name)

    # Constants
    _MODELDB_BASE_URL = 'http://senselab.med.yale.edu/modeldb/'
