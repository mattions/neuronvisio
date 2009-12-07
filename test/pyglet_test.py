from __future__ import absolute_import
from visual import *
import visual.graph
import pyglet.window
import sys, threading

class VisualThread:
    def __init__(self):
        self.displays = []
        self.started = 0
    def add(self, display):
        self.displays.append( display )
        if not self.started:
            self.started = 1
            threading.Thread( target = self.go ).start()
    def remove(self, display):
        self.displays.remove( display )
    def go(self):
        while 1:
            displays = list( self.displays )
            interval = self.paint_displays( displays )
            time.sleep(interval)

    def paint_displays(self, displays):
        # This is basically render_manager::paint_displays; perhaps we should
        # expose that to python?
        if not displays: return .030

        for d in displays:
            d.update()
        
        start = time.time()
        for d in displays:
            d.paint()
        paint = time.time() - start

        for d in displays:
            d.swap()
        swap = time.time() - (start+paint)

        interval = max(.005, paint - swap)
        return interval

class display ( cvisual.display_kernel ):
    _thread = VisualThread()
    _window = None
    
    def __init__(self, **keywords):
        self._buttons = [False]*3
        cvisual.display_kernel.__init__(self)
        haslights = False
        
        for kw in keywords:
            if (kw == 'lights'):
                haslights = True
            setattr(self, kw, keywords[kw])
            
        print "Keywords passed to display %s" %keywords
#        if not haslights:
#            light( pos=cvisual.vector(0.22, 0.44, 0.88).norm(), color=0.8,
#                   local=0, display=self)
#            light( pos=cvisual.vector(-0.88, -0.22, -.44).norm(), color=0.3,
#                   local=0, display=self)
        self.select()
    def select(self):
        cvisual.display.set_selected(self)
    def _activate( self, a ):
        self._activated = a
        if a:
            self._thread.add( self )

    def _create(self):
        self._window = pyglet.window.Window(width = int(self.width), height = int(self.height),
                                            resizable=True,
                                            caption = self.title)
        if self.x >= 0 and self.y >= 0:
            self._window.set_location( int(self.x+5), int(self.y+30) )

        self._report_resize()

        for evt in dir(self):
            if evt.startswith("_on_"):
                setattr(self._window, evt[1:], getattr(self, evt))

    def _destroy(self):
        self._thread.remove( self )
        self._window.close()
        self._window = None
        self.report_closed()

    def update(self):
        if not self._activated:
            self._destroy()
            return
        if not self._window: self._create()
        self._window.dispatch_events()
        
    def paint(self):
        if not self._window: return
        self._window.switch_to()
        self.render_scene()

    def swap(self):
        if not self._window: return
        self._window.flip()

    def _report_resize(self):
        vx, vy = self._window.get_location()
        vw, vh = self._window.get_size()

        # todo: actually figure out the window's position and size
        wx, wy, ww, wh = vx,vy,vw,vh

        self.report_resize(wx, wy, ww, wh, vx, vy, vw, vh)
    def _on_move(self, x, y):
        self._report_resize()
    def _on_resize(self, width,height):
        self._report_resize()

    def _on_close(self):
        self._destroy()
        if self.exit:
##            print "Closing program"
            import os
            os._exit(0)  # todo: less drastic method?

    def _report_mouse_state(self, x, y):
        self.report_mouse_state( self._buttons, x, int(self.height-y), [], False )

    _mb_map = { pyglet.window.mouse.LEFT : 0, pyglet.window.mouse.RIGHT : 1, pyglet.window.mouse.MIDDLE : 2 }
    def _on_mouse_press(self, x,y, button, modifiers):
        self._buttons[self._mb_map[button]] = 1
        self._report_mouse_state(x, y)
    def _on_mouse_release(self, x,y, button, modifiers):
        self._buttons[self._mb_map[button]] = 0
        self._report_mouse_state(x, y)
    def _on_mouse_motion(self, x,y,dx,dy):
        self._report_mouse_state(x,y)
    def _on_mouse_drag(self, x,y,dx,dy,buttons,modifiers):
        self._report_mouse_state(x,y)
    _on_mouse_enter = _report_mouse_state
    _on_mouse_leave = _report_mouse_state

    def _getProcAddress(self, name):
        import ctypes
        if hasattr( pyglet.gl, "lib_glx" ) and pyglet.gl.lib_glx.pyglet.gl.lib_glx._have_getprocaddress:
            ptr = pyglet.gl.lib_glx.pyglet.gl.lib_glx.glXGetProcAddressARB(name)
        elif hasattr( pyglet.gl, "lib_wgl" ):
            ptr = pyglet.gl.lib_wgl.wglGetProcAddress(name)
        elif hasattr( pyglet.gl, "lib_agl" ):
            try:
                ptr = getattr(pyglet.gl.lib_agl.gl_lib, name)
            except AttributeError,e:
                return 0
        else:
            return 0
        ptr = ctypes.cast( ptr, ctypes.c_void_p ).value or 0
        return ptr

scene = display()

visual.graph.display = display
visual.graph.scene = scene
