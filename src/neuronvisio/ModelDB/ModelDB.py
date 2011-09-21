#!/bin/env python
import types
import string
import re
import os
import xml.etree.ElementTree
import urllib
import zipfile

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
def StartFile(filename):
    try:
        # Implementation for Windows
        f=filename.replace('/', '\\')
        os.startfile(f)
    except:
        # Implementation for Linux
        subprocess.Popen(['xdg-open', filename])

class Model:
    # Fields
    _model = None
    _log = None

    # Constants
    _modelProperties = [('model_type', 0), ('model_concepts', 0),
                        ('transmitters', 0),('genes', 0), ('receptors', 0), ('brain_regions', 0),
                        ('channels', 0), ('cell_types', 0), ('gap_junctions', 0), 
                        ('implementers', 0),
                        ('simulation_environment', 0)]

    # Initialization
    def __init__(self, model, log):
        self._model = model
        self._log = log

    # Public data accessors
    def getProperties(self):
        for (k, s) in self._modelProperties:
            t=to_text(self._model[k])
            t=t.strip()
            if len(t) == 0: # Show only non-empty properties
                continue
            k=k.replace('_', ' ')
            k=k.title()
            yield (k, t)
            
    def getName(self):
        return self._model['short_name']

    def getTitle(self):
        return self._model['title']

    def getId(self):
        return self._model['model_id'].strip()

    def getReadme(self):
        if self._model.has_key('readme') == False:
            return None
        return self._model['readme'][0]

    # Public operations and manipulations
    def existsLocally(self):
        return os.path.isdir(self.get_dir())

    def browse(self):
        if self.existsLocally():
            modelName = self.getName()
            self._log("Openning '" + self.get_dir()+"'.")
            StartFile(self.get_dir())
        else:
            self._log("Model does not exists locally")
        
    def downloadModel(self):
        modelId = self.getId()
        if os.path.isdir('Models')==False:
            os.mkdir('Models')        
        zipFile = 'Models/'+modelId+'.zip'
        modelDir = self.get_dir()
        if os.path.isdir(modelDir):
            self._log("Model '" + self.getName() + "' already exists locally")
            return            
        if os.path.isfile(zipFile)==False:
            if type(self._model['zip_url'])==types.NoneType:
                self._log("No zip URL found for '" + self.getName() + "'")
                return
            else:
                self._log("Downloading model for '" + self.getName() + "'")
                self.download_file(self._model['zip_url'][0], zipFile)
                self._log("Download complete.")
                # TODO: open model data in tab
                # TODO: recolor, self.tree.SetItemColor(item, wx.Colour(100,10,255))
        else:
            self._log("Model for '" + self.getName() + "' already downloaded")
        self.extract_model(zipFile, modelDir)

    # Private implementation methods
    def get_dir(self):
        modelId = self.getId()
        dirName = 'Models/'+modelId+'/'
        return dirName
        
    # Download model file from the network
    def download_file(self, url, filename):
        self._log("Creating " + filename)
        try:
            s = urllib.urlopen(url)
            f = open(filename, "wb")
            f.write(s.read())
            f.close()
        except Exception as e:
            self._log("Error downloading file: "+e.message)
            return
        self._log("Done.")

    # Extract model zip file
    # ModelDB zip files contain trailing garbage which should be removed
    # See 'ZIP end of central directory record' in http://en.wikipedia.org/wiki/ZIP_%28file_format%29
    def extract_model(self, zipFile, modelDir):
        self._log("Extracting '" + zipFile + "' into " + modelDir)
        try:
            f = open(zipFile, 'r+b')
            data = f.read()
            pos = data.find('\x50\x4b\x05\x06') # End of central directory signature
            if (pos > 0):
                self._log("Trancating file at location " + str(pos + 22)+ ".")
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
            self._log("Error extracting file: "+str(e.message))
            return
        self._log("Done.")

    # Access the internal dictionary
    def get_dictionary(self):
        return self._model

#---------------------------------------------------------------------------
class Models():
    # Fields
    _log = None
    _short_name_re = None   
    _modelList = []
    _modelTree = {}

    # public methods
    def __init__(self, log):
        self._short_name_re = re.compile("^\s*(.*)\((.*)\)")
        self._modelList = self.generate_models_list('ModelDB.xml')
        self._modelTree = self.generate_models_tree(self._modelList)        
        self._log = log
        
    def getModelNames(self):
        return self._modelTree.keys()

    def hasModel(self, modelName):
        return self._modelTree.has_key(modelName)

    def getModel(self, modelName):
        return Model(self._modelTree[modelName], self._log)

    def getField(self, model, field):
        return to_text(self._modelTree[model][field])
    
    """ Returns whether a model contains the search keyword or not. """
    def Search(self, name, keyword):
        return self._modelTree[name]['searchable'].find(keyword.lower()) >= 0
       
    # private methods
    def generate_models_list(self, data):
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

    def generate_models_tree(self, list):
        tree={}
        for m in list:
            search=''
            for s in m.keys():
                search = search + "|" + to_text(m[s])
            m['searchable']=search.lower()
            name=m['name']
            [t, s]=self.get_title_short_name(name)
            m['short_name']=s
            m['title']=t
            c=to_text(m['citations']).strip()
            if len(c)>0:
                m['citations']=self._modeldb_base_url + c
            tree[s]=m
        return tree

    def get_title_short_name(self, name):
        m=self._short_name_re.match(name)
        if m:
            return m.groups()
        else:
            raise Exception("no match in " + name)

    # Constants
    _modeldb_base_url = 'http://senselab.med.yale.edu/modeldb/'
