#!/usr/bin/env python

# example helloworld.py readapt for visual

import pygtk
pygtk.require('2.0')
import gobject
gobject.threads_init()
import gtk
import visual

class HelloWorld(object):
    
    def launch_visual_window(self, widget, data=None):
        print "Lauching visual window"
        gobject.idle_add(visual.cylinder())
        print "Window Launched"

    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        print "destroy signal occurred"
        gtk.main_quit()

    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(10)


    
        # Creates a new button with the label "Hello World".
        self.button = gtk.Button("Launch Visual Window")
        
        self.button.connect("clicked", self.launch_visual_window, None)

        self.button.connect_object("clicked", gtk.Widget.destroy, self.window)
        
        # This packs the button into the window (a GTK container).
        self.window.add(self.button)
    
        # The final step is to display this newly created widget.
        self.button.show()
    
        # and the window
        self.window.show()

    def main(self):
        # All PyGTK applications must have a gtk.main(). Control ends here
        # and waits for an event to occur (like a key press or mouse event).
        gtk.main()

# If the program is run directly or passed as an argument to the python
# interpreter then create a HelloWorld instance and show it
if __name__ == "__main__":
    hello = HelloWorld()
    hello.main()

