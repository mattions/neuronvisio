#!/bin/env python
import types

HTML_BODY="<body bgcolor='#999999' text='#FFFFFF'>"
HTML_TABLE="<table bgcolor='#94A5BD' width='100%%' cellspacing='0' cellpadding='0' border='1'>"

# TODO: those are general functionality, move to better place
def generate_table(format, properties, cols):
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

class ModelPages:        
    def DefaultReadmeTab(self):
        return self.create_readme_tab(self._mainReadme)

    def CreateReadmeTab(self, model):
        if (type(model.getReadme()) == types.NoneType):
            readme = self._mainReadme
        else:
            readme = model.getReadme()
        return self.create_readme_tab(readme)

    def DefaultOverviewTab(self):
        return self._mainOverview
    
    def CreateOverviewTab(self, model):
        html = "<html>"
        html = html +HTML_BODY
        html = html + "<h1>Model Information</h1>"
        html = html + "<p>" + generate_table(self._modelPageHeader, model.get_dictionary(), 3) + "</p>"
        html = html + "<h1>Model Properties</h1>"
        html = html + "<p>" + HTML_TABLE
        for k,s in model.getProperties():
            html = html + "<tr><td>" + k + "</td><td>" + s + "</td></tr>"
        html = html + "</table></p>"
        html = html + "</body>"
        html = html + "</html>"
        return html

    def create_readme_tab(self, readme):
        html = "<html>"
        html = html +HTML_BODY
        html = html + "<p>" + HTML_TABLE
        html = html + "<tr>" + readme + "</tr>"
        html = html + "</table></p>"
        html = html + "</body>"
        html = html + "</html>"
        return html

    _modelPageHeader="""%(short_name)s|<b>%(title)s</b>
    <b>Description</b>: %(description)s
    <b>Reference</b>: %(reference)s
    <a href='%(url)s'>ModelDB Page</a>|<a href='%(citations)s'>Citations Query</a>|Model #%(model_id)s"""
    _mainReadme = """<td>
    <p> This tab will contain model README file. </p>
    </td>"""
    _noReadme = """<td>
    <p> Error!<br/> README not found</p>
    </td>"""
    _mainOverview = "<html>" + HTML_BODY + HTML_TABLE + "<tr><td>"\
    """<h2>NeuroCircuit 0.1</h2>

    <p> Welcome.
    <p> NeuroCircuit allows you to <b>easily find</b> models of neurons and
    neuron networks from ModelDB, browse <b>model propeties</b> and <b>mark</b>
    models of choise so you can come back to them later.
    <p> Then it allows <b>downloading</b> model files to a local directory
    where you may <b>visualize</b> them using Neuronvision or <b>compile</b> and
    even <b>run</b> them using NEURON.
    </td><tr></table></body><html>"""
