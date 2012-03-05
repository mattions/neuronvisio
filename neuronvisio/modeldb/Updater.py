#!/bin/env python
import urllib2
import time
import logging
import xml.dom.minidom
import re
import types
import codecs
import os.path
from BeautifulSoup import BeautifulSoup

logger = logging.getLogger(__name__)

# This class allows updating a ModelDB local store from the online site.
# 
# It also offer a stand-alone main() which update the ModelDB.xml file
# from current directory.
class ModelDBUpdater:
	# Constants
	_BASE_URL = 'http://senselab.med.yale.edu/modeldb/'
	_START_URLS = ["http://senselab.med.yale.edu/modeldb/ModelList.asp?id=1882"]
	_DOWNLOAD_DELAY = 1
	_ID_REGEX = re.compile("ShowModel\.asp\?model=(\d*)")
	_NAME_REGEX = re.compile("^\s*(.*)\(((.*)(\d{4}).*)\)")
	
	# Private variables
	_last_download_time = 0
	_xml_file = ""
	_existing_items = {}
	_dom = None

	# Initialize an updater for a file with local ModelDB content
	def __init__(self, xml_file):
		self._xml_file = xml_file
		# Create the file if it does not exist
		if os.path.isfile(xml_file)==False:
			f=codecs.open(xml_file, "w", encoding='utf-8')
			f.write('<?xml version="1.0" ?><items/>'.decode('utf-8'))
			f.close()
		# Read the file into dom
		logger.info("Reading %s..."%xml_file)
		self._dom = xml.dom.minidom.parse(xml_file)
		# Create a list of available id-s
		items=self._dom.childNodes[0]
		ids=items.getElementsByTagName('model_id')
		for i in ids:
			id = i.childNodes[0].toxml().strip()
			self._existing_items[id] = True
		logger.info("Got %d models locally"%len(self._existing_items.keys()))

	# Update models XML file from online content
	def update(self):
		# Get online items and compare them to the local items
		online = self.get_online_items()
		logger.info("Got %d online items"%len(online))	
		new_ones = self.get_new_items(online)
		logger.info("Got %d new items"%len(new_ones))
		# Add an item to the dom for each new item
		for i in new_ones.keys():
			u=new_ones[i]['url']
			v=self.parse_item(u)
			new_item = self._dom.createElement('item')
			for k in v.keys():
				name = self._dom.createElement(k)
				if type(v[k]) == types.ListType:
					# Create a node named after the key with childrens named 'value' for each value
					for val in v[k]:
						value = self._dom.createElement('value')
						value.appendChild(self._dom.createTextNode(self._get_text(val)))
						name.appendChild(value)
					# "The most common shortcoming of BeautifulStoneSoup is that it  doesn't know about
					# self-closing tags" so we need to add empty content in them
					if len(v[k])==0:
						name.appendChild(self._dom.createTextNode(u""))
				else:
					name.appendChild(self._dom.createTextNode(self._get_text(v[k])))
				new_item.appendChild(name)
			self._dom.childNodes[0].appendChild(new_item)
		self.update_xml()
		return new_ones

	# Compare existing items to online ones
	def get_new_items(self, online_items):
		online_ids = online_items.keys()
		new_items = {}
		for i in online_items:
			if self._existing_items.has_key(i)==False:
				new_items[i]=online_items[i]
				logger.info("New item %d %s"%(int(i), new_items[i]['name']))
		return new_items

	# Find all online items 
	def get_online_items(self):
		results = {}
		for u in self._START_URLS:
			list_data = self._get_url(u)
			soup = BeautifulSoup(list_data)
			for i in soup('tr'):
				if i.td.a==None or i.td.a.string==None:
					logger.warn("Ignoring empty item: %s"%i)
				else:
					# Filter only idems which have a valid id and name
					# This prevents collecting place-holders for yet-to-be-published items
					m=self._ID_REGEX.match(i.td.a['href'])
					n=self._NAME_REGEX.match(i.td.a.string)
					if not m:
						logger.warn("Ignoring bad model link: '%s'"%i.td.a['href'])
					elif not n:
						logger.warn("Ignoring bad model name: '%s'"%i.td.a.string)
					else:
						id = m.groups()[0]
						url = self._BASE_URL + i.td.a['href']
						name = i.td.a.string
						map = {'url':url, 'name':name, 'id':id}
						results[id] = map
		return results

	# Write DOC back into XML file
	def update_xml(self):
	    f = codecs.open(self._xml_file, "w", encoding='utf-8')
	    xml=self._dom.toxml(encoding="utf-8")
	    soup = BeautifulSoup(xml)
	    try:
	    	f.write(soup.prettify().decode('utf-8')) 
	    	f.close()
	    except IOError:
	    	logger.error("Not able to write the file: %s" % self._xml_file)

	# Parse a ModelDB model page and extract an item dictionary	
	def parse_item(self, url):
		data=self._get_url(url)

		# Extract main items from the page
		soup = BeautifulSoup(data)
		table1 = soup.find('table', {'id': 'Table1'})
		table2 = soup.find('table', {'id': 'Table2'})
		table3 = soup.find('table', {'id': 'Table3'})
		if table1 == None or table2 == None or table3 == None:
			exit("Could not find a mandatory table")
		rows = table1.findAll('tr', {}, False)
		if rows == None:
			exit("Could not find model details")
		props = table2.findAll('tr', {}, False)
		if props == None:
			exit("Could not find model properties")
		files = table3.findAll('tr', {}, False)
		if files == None:
			exit("Could not find model files")
		
		item={}		
		item['url']=url.encode('utf-8')
		
		# Model details
		item['name'] = rows[0].th.string
		if item['name'] == None:
			exit("Could not find mandatory field: name")
		item['model_id'] = rows[1].th.contents[2]
		if item['name'] == None:
			exit("Could not find mandatory field: name")
		item['description'] = self._html_to_text(rows[2].td.contents)
		if item['description'] == None:
			exit("Could not find mandatory field: description")
		item['reference'] = self._html_to_text(rows[2].td.contents[3:])
		if rows[2].td.em != None and rows[2].td.em.a != None:
			item['article'] = rows[2].td.em.a['href']
		if rows[2].td.small != None and rows[2].td.small.a != None:
			item['pubmed'] = rows[2].td.small.a['href']
		item['citations'] = rows[3].td.a['href']

		# Model properties
		item['model_type'] = self._list_to_text(props[0].findAll('td', {}, False)[1]('a'))
		item['brain_regions'] = self._list_to_text(props[1].findAll('td', {}, False)[1]('a'))
		item['cell_types'] = self._list_to_text(props[2].findAll('td', {}, False)[1]('a'))
		item['channels'] = self._list_to_text(props[3].findAll('td', {}, False)[1]('a'))
		item['gap_junctions'] = self._list_to_text(props[4].findAll('td', {}, False)[1]('a'))
		item['receptors'] = self._list_to_text(props[5].findAll('td', {}, False)[1]('a'))
		item['genes'] = self._list_to_text(props[6].findAll('td', {}, False)[1]('a'))
		item['transmitters'] = self._list_to_text(props[7].findAll('td', {}, False)[1]('a'))
		item['simulation_environment'] = self._list_to_text(props[8].findAll('td', {}, False)[1]('a'))
		if item['simulation_environment'] == None:
			exit("Could not find mandatory field: simulation_environment")
		item['model_concepts'] = self._list_to_text(props[9].findAll('td', {}, False)[1]('a'))
		item['implementers'] = self._list_to_text(props[10].findAll('td', {}, False)[1]('a'))

		# Model files
		links = files[0].td.div.findAll('a', None, False)
		zip_url=links[0]['href']
		item['zip_url']=zip_url
		if item['zip_url'] == None:
			exit("Could not find mandatory field: zip_url")
		readme = files[1].findAll('td', None, False)[1]
		item['readme']=readme.renderContents().decode('utf-8')
		if item['readme'] == None:
			exit("Could not find mandatory field: readme")
		return item

	# Download data from URL with appropriate delays
	def _get_url(self, url):
		# Delay the download by some time, if needed
		time_since_download = time.time() - self._last_download_time
		if time_since_download  < self._DOWNLOAD_DELAY:
			s = self._DOWNLOAD_DELAY - time_since_download
			logger.debug("Sleeping for %0.2f seconds"%s)
			time.sleep(s)
			
		# Perform the actual download
		logger.info("Reading %s"%url)
		data = urllib2.urlopen(url).read()
		self._last_download_time = time.time()		
		return data

	# Extract text from a contents list, concatanating the text of the items into a single string
	def _html_to_text(self, h):
		t=u""
		for i in h:
			if type(i).__name__=='NavigableString':
				t=t+i
			elif i.string != None:
				t=t+i.string
			else:
				logger.debug("No text extracted from %s"%str(i))
		return t

	# Extract text from a list, returning a list of strings
	def _list_to_text(self, l):
		v=[]
		for i in l:
			v.append(self._html_to_text(i))
		return v
	
	# Extract text from BeautifulStoneSoup node into a string
	def _get_text(self, node):
		if type(node).__name__ == 'NavigableString':
			return node.string
		elif type(node).__name__ == 'NavigableUnicodeString':
			return node.string
		elif type(node) == types.StringType:
			return unicode(node, 'utf-8')
		elif type(node) == types.UnicodeType:
			return node
		elif node == None:
			# See the comment above about the shortcoming of BeautifulStoneSoup
			return u""
		return node.renderContents()
