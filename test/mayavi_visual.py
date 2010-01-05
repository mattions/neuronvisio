from enthought.mayavi import mlab
from enthought.tvtk.tools import visual
# Create a figure
f = mlab.figure(size=(500,500))
# Tell visual to use this as the viewer.
visual.set_viewer(f)

# Even sillier animation.
cyl = visual.Cylinder(pos=(0.,0.,0.), radius=8, length=10)
cyl2 = visual.Cylinder(pos=(8.,0.,0.,), axis=(0.,4.,5.), radius=4, length=13)
cyl3 = visual.Cylinder(pos=(-4.,0.,0.))


