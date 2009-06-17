# Michele Mattioni
# Thu May 21 11:46:55 BST 2009

import visual
import visual.graph
from neuron import h
import threading
import gtk

class Visio():
    
    def __init__(self):

        self.scene = visual.display(title="nrnVisio")
        self.cyl2sec = {}
        self.vecRefs = []
        self.selectedCyl = None # Used for storing the cyl when picked
        self.selectedCylColor = (0,0,1) #blue
        self.defaultColor = (1,1,1) #light gray
        self.h = h # Link to the neuron interpreter
        self.t = None # Var to track the time Vector

        
        
    def getVec(self,sec, var=None):
        """Return the vecs that record given a section
        
        param: 
            sec - Section of interest
            var - if None return all the vectors that record in that section
            as a list, otherwise return the vector that record the variable var"""
        vecsSection = [] 
        for vecRef in self.vecRefs:
            if vecRef.sec == sec:
                if var is None:
                    vecsSection.append(vecRef.vec)
                elif var == vecRef.var:
                    return vecRef.vec
        
        return vecsSection
                        
    
    def pickSection(self):
        while(True):
            if self.scene.mouse.clicked:
                 m = self.scene.mouse.getclick()
                 loc = m.pos
                 picked = m.pick
                 if picked:
                     
                     # unselect the old one
                    if self.selectedCyl is not None:
                        self.selectedCyl.color = self.defaultColor
                    
                    picked.color = self.selectedCylColor
                    self.selectedCyl = picked
                    sec = self.cyl2sec[picked]
                    return sec
                     
                     #print "Section: %s Name: %s" %(sec, sec.name())
    
    
    
    def createVector(self, var):
        sec = self.pickSection()
        vecNotPresent = True
        for vecRef in self.vecRefs:
            print "Searched: var %s, sec %s.\tCurrent var: %s sec: %s" %(var, sec, vecRef.var, vecRef.sec) 
            if vecRef.var == var and vecRef.sec == sec:
                  vecNotPresent = False
                  break
        if vecNotPresent:      
            vec = h.Vector()
            varRef = '_ref_' + var
            vec.record(getattr(sec(0.5), varRef))
            vecRef = VecRef(var, vec, sec)
            self.vecRefs.append(vecRef)
        return sec     

    def plotVector(self, tPoints, varPoints):
        funct = visual.graph.gcurve()
        try:
             for i in range(int (tPoints.size() )):
                 curve.plot(pos=(tPoints[i], varPoints[i]))
        except LookupError:
            print "At least one of the vector seems to be empty.\n\
            Please run the simulation first"
        
        return funct
                       
    def retrieveCoordinate(self, sec):
        coords = {}
        sec.push()
        coords['x0'] = h.x3d((h.n3d()- h.n3d()))
        coords['x1'] = h.x3d((h.n3d()- 1))
        coords['y0'] = h.y3d((h.n3d()- h.n3d()))
        coords['y1'] = h.y3d((h.n3d()- 1))
        coords['z0'] = h.z3d((h.n3d()- h.n3d()))
        coords['z1'] = h.z3d((h.n3d()- 1))
        h.pop_section()
        return coords
        
    
    def drawSection(self, sec):
        coords = self.retrieveCoordinate(sec)
        x_ax = coords['x1'] -coords['x0']
        y_ax = coords['y1'] -coords['y0']
        z_ax = coords['z1'] -coords['z0']
        cyl = visual.cylinder(pos=(coords['x0'],coords['y0'],coords['z0']), 
                          axis=(x_ax,y_ax,z_ax), radius=sec.diam/2)
        
        self.cyl2sec[cyl] = sec
    
    def visualizeSectionPotential(self):
        pass
    
    
    def findSecs(self, secList, secName):
        selectedSec = None
        for sec in secList:
            if hasattr(sec, "head"): # it's a spine
                spines_attr = ["head","neck","psd"]
                for attr in spines_attr:
                    #print attr, sec.__dict__[attr].name(), secName    
                    if sec.__dict__[attr].name() == secName:
                        selectedSec = sec
                        print "Found sec %s, spine %s" %(sec.__dict__[attr].name(), sec.id)
                        break
            else: # Normal secion
            
                if sec.name() == secName:
                    selectedSec = sec
                    break
        if selectedSec is None:
            return ""    
            
        return selectedSec
    
    def drawModel(self):
        drawn = False
        # Hide all the old objects
        for obj in self.scene.objects:
            obj.visible = False
        
        # Draw the new one
        h.define_shape()
        for sec in h.allsec():
            self.drawSection(sec)
            drawn = True # Assigned every time. Didn't find a way to test if there is a sec
             
        return drawn
            
    
    def dragModel(self):
        pick = None # no object picked out of the scene yet
        
        while True:
            if self.scene.mouse.events:
                m1 = self.scene.mouse.getevent() # get event
                if m1.drag and m1.pick : # if touched a cylinder
                    drag_pos = m1.pickpos # where on the cylinder
                    pick = m1.pick # pick now true (not None)
                elif m1.drop and not m1.drag: # released at end of drag
                    pick = None # end dragging (None is false)
                    break # Out of the loop.
            if pick:
                # project onto xy plane, even if scene rotated:
                new_pos = self.scene.mouse.project(normal=(0,0,1))
                
                if new_pos != drag_pos: # if mouse has moved
                    # offset for where the ball was clicked:
                    offset = new_pos - drag_pos
                    # For all the object
                    for obj in self.scene.objects:
                            obj.pos += offset
                            drag_pos = new_pos # New drag pos start is the new pos
                            
    def addVecRef(self, var, sec):
        """Add a vecRef in the list. It takes care to create the vector
        
        :param: 
        var - The variable to record
        sec - The section where to record
        
        return success"""
        success = False
        if hasattr(sec, var):
            # Adding the vector only if does not exist
            alreadyPresent=False
            for vecRef in self.vecRefs:
                if vecRef.sec.name() == sec.name():
                    if vecRef.vecs.has_key(var):
                        alreadyPresent = True
                        break
             
            if not alreadyPresent:
                
                # Creating the vector
                vec = h.Vector()
                varRef = '_ref_' + var
                vec.record(getattr(sec(0.5), varRef))
                
                # Adding to the list
                vecRef = VecRef(sec)
                vecRef.vecs[var] = vec
                self.vecRefs.append(vecRef)
                success = True
        
        return success
    
    def addAllVecRef(self, var):
        """Create the vector for all the section with the given variable"""
        done = False
        responses = []
        for sec in h.allsec():
            response = self.addVecRef(var, sec)
            responses.append(response)
        # If all the responses are False it means we already
        # created all the vecs and we are done    
        if any(responses) == False: #all False we're done
            done = True
        return done
                
        

class VecRef(object):
    """Basic class to associate one or more vectors with a section"""
    def __init__(self, sec):
        # section
        self.sec = sec
        #Dict with all the vecs
        # Key: var Value: Hoc.Vector
        self.vecs = {}
        
        
    def info(self):
        print "Var: %s Vec: %s SecName: %s" %(self.var, self.vec, self.sec.name())
    