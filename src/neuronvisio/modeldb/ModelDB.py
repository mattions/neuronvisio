#!/bin/env python
import types
import string
import re
import os
import xml.etree.ElementTree
import urllib
import zipfile
import logging 
import subprocess

logger = logging.getLogger(__name__)

HTML_BODY="<body bgcolor='#999999' text='#FFFFFF'>"
HTML_TABLE="<table bgcolor='#FFFFFF' width='100%%' cellspacing='2' cellpadding='2' border='1'>"

class Model(object):
    # Fields
    _model = None
    
    # Constants
    _MODEL_PROPERTIES = [('model_type', 0), ('model_concepts', 0),
                        ('transmitters', 0),('genes', 0), ('receptors', 0), ('brain_regions', 0),
                        ('channels', 0), ('cell_types', 0), ('gap_junctions', 0), 
                        ('implementers', 0),
                        ('simulation_environment', 0)]
    _MODEL_PAGE_LAYOUT = """%(short_name)s|<b>%(title)s</b>
        <b>Description</b>: %(description)s
        <b>Reference</b>: %(reference)s
        <a href='%(url)s'>ModelDB Page</a>|<a href='%(citations)s'>Citations Query</a>|Model #%(model_id)s"""
    _README_NOT_FOUND = "A readme file was not found for this model, try online at ModelDB"
    
    # Initialization
    def __init__(self, model):
        self._model = model

    # Public data accessors
    # Get a mapping of non-empty model properties
    def get_properties(self):
        for (k, s) in self._MODEL_PROPERTIES:
            t=self._model[k]
            t=t.strip()
            if len(t) == 0: # Show only non-empty properties
                continue
            k=k.replace('_', ' ')
            k=k.title()
            yield (k, t)
            
    def get_name(self):
        return self._model['short_name']

    def get_title(self):
        return self._model['title']

    def get_description(self):
        return self._model['description']

    def get_reference(self):
        return self._model['reference']

    def get_url(self):
        return self._model['url']

    def get_id(self):
        return int(self._model['model_id'])

    def get_authors(self):
        return self._model['short_authors']

    def get_year(self):
        return self._model['year']

    # Get the model readme in text
    def get_readme_text(self):
        if self._model.has_key('readme') == False:
            return None
        return self._model['readme']

    # Get the model readme in HTML
    def get_readme_html(self):
        readme = self.get_readme_text()
        if readme == "":
            return self._create_readme_tab(self._README_NOT_FOUND)
        return self._create_readme_tab(readme)

    # Get the model overview
    def get_overview(self):
        return self._create_overview_tab()
    
    # Public operations and manipulations
    # Check if model exists locally
    def exists_locally(self):
        return os.path.isdir(self.get_dir())

    # Open model directory for browsing
    def browse(self):
        if self.exists_locally():
            modelName = self.get_name()
            logger.info("Opening '" + self.get_dir()+"'.")
            self._start_file(self.get_dir())
        else:
            logger.info("Model does not exists locally")

    # Download model file from network
    def download_model(self):
        modelId = self.get_id()
        if os.path.isdir('Models')==False:
            os.mkdir('Models')        
        model_zipped= ('%s.zip') %modelId
        zipFile = os.path.join('Models', model_zipped)
        modelDir = self.get_dir()
        if not os.path.isfile(zipFile):
            if self._model['zip_url']=="":
                logger.info("No zip URL found for '" + self.get_name() + "'")
                return
            else:
                logger.info("Downloading model for '" + self.get_name() + "'")
                self._download_file(self._model['zip_url'], zipFile)
                logger.info("Download complete.")
                # TODO: open model data in tab
                # TODO: recolor, self.tree.SetItemColor(item, wx.Colour(100,10,255))
        else:
            logger.info("Model for '" + self.get_name() + "' already downloaded")
        if not os.path.isdir(modelDir):
            self._extract_model(zipFile, modelDir)
        else:
            logger.info("Model for '" + self.get_name() + "' already extracted")
        return modelDir

    # Get model directory
    def get_dir(self):
        modelId = self.get_id()
        dirName = os.path.join('Models', str(modelId))
        return dirName
    
    def get_tooltip(self):
        "Return the tooltip for the model."
        tooltip = ''
        if self.exists_locally():
            tooltip = 'Model %s downloaded in %s' %(self.get_id(), 
                                                    self.get_dir())
        else: 
            tooltip = 'Model %s has not been downloaded' %self.get_id()
        return tooltip

    # Private implementation methods
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

    # Create the HTML of the readme tab
    def _create_readme_tab(self, readme):
        html = "<html>"
        html = html +HTML_BODY
        html = html + "<p>" + HTML_TABLE
        html = html + "<tr>" + readme + "</tr>"
        html = html + "</table></p>"
        html = html + "</body>"
        html = html + "</html>"
        return html

    # Create the HTML of the overview tab
    def _create_overview_tab(self):
        html = "<html>"
        html = html +HTML_BODY
        html = html + "<table border='0'><tr><td>"
        html = html + "<h1>Model Information</h1>"
        html = html + "<p>" + self._generate_table(self._MODEL_PAGE_LAYOUT, 3) + "</p>"
        html = html + "</td><td>"
        html = html + "<td><h1>Model Properties</h1>"
        html = html + "<p>" + HTML_TABLE
        for k,s in self.get_properties():
            html = html + "<tr><td><strong>" + k + "</strong></td><td>" + s + "</td></tr>"
        html = html + "</table></p>"
        html = html + "</td></tr></table>"
        html = html + "</body>"
        html = html + "</html>"
        return html

    # Create an HTML table from the given table format
    def _generate_table(self, format, cols):
        properties = self._model
        result=HTML_TABLE
        lines=format.split('\n')
        for l in lines:
            a=''
            i=0
            cells=l.split('|')
            v=cols-len(cells)+1
            for c in cells:
                i=i+1
                if (i == len(cells)):
                    a=a+'<td colspan="' + str(v) + '">'+c%properties+'</td>'
                else:
                    a=a+'<td>'+c%properties+'</td>'
            result = result + '<tr>' + a + '</tr>'
        result = result + "</table>"
        return result

    # Open a directory for browsing its content (implementation taken from SO)
    # http://stackoverflow.com/questions/2878712/make-os-open-directory-in-python
    def _start_file(self, filename):
        try:
            # Implementation for Windows
            f=filename.replace('/', '\\')
            os.startfile(f)
        except:
            # Implementation for Linux
            subprocess.Popen(['xdg-open', filename])

#---------------------------------------------------------------------------
class Models():
    # Fields
    _log = None
    _name_re = None   
    _modelList = []
    _modelTree = {}

    # public methods
    # Initialize class, assuming the XML model DB is in the current directory
    def __init__(self):
        self._name_re = re.compile("^\s*(.*)\(((.*)(\d{4}).*)\)")
        path = os.path.split(os.path.abspath(__file__))[0] # base absolute dir 
        self._modelList = self._generate_models_list(os.path.join(path, 'ModelDB.xml'))
        self._modelTree = self._generate_models_tree(self._modelList)        

    # Get all model names
    def get_model_names(self, keyword=""):
        for name in self._modelTree.keys():
            if not keyword or self.search(name, keyword):
                yield name

    # Check if specific model exists
    def has_model(self, modelName):
        return self._modelTree.has_key(modelName)

    # Get specific model
    def get_model(self, modelName):
        return Model(self._modelTree[modelName])

    # Get the value of specific model field
    def get_field(self, model, field):
        return self._modelTree[model][field]
    
    """ Returns whether a model contains the search keyword or not. """
    def search(self, name, keyword):
        return self._modelTree[name]['searchable'].find(keyword.lower()) >= 0
       
    # private methods
    # Generate the models list from the input XML
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

    # Generate the models tree, moving each item into canonical form
    def _generate_models_tree(self, list):
        tree={}
        for m in list:
            search=''
            for s in m.keys():
                search = search + "|" + self._to_text(m[s])
            m['searchable']=search.lower()
            name=m['name']
            [t, s, a, y]=self._get_title_authors_year_short_name(name)
            m['short_name']=s
            m['title']=t
            m['short_authors']=a
            m['year']=y
            c=self._to_text(m['citations'])
            if len(c)>0:
                m['citations']=self._MODELDB_BASE_URL + c
            for k in m.keys():
                m[k]=self._to_text(m[k])
            tree[s]=m
        return tree

    # Parse model short name into arguments
    def _get_title_authors_year_short_name(self, name):
        m=self._name_re.match(name)
        if m:
            return m.groups()
        else:
            raise Exception("no match in " + name)

    # Handle string, none and list values and change them to be stripped string
    def _to_text(self, t):
        if (type(t) == types.ListType):
            t=string.join(t, ',')
        if (type(t) == types.NoneType):
            t=''
        t=t.strip()
        return t

    # Constants
    _MODELDB_BASE_URL = 'http://senselab.med.yale.edu/modeldb/'
