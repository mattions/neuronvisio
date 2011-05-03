import numpy as np
from enthought.mayavi import mlab

x=np.array([0,-1,2])
y=np.array([0,-3,-5])
z=np.array([0,0,-1])
d=np.array([3,2,1])
var_data=np.array([0.1,0.3,0.5])
edges=np.vstack([[0,1],[0,2]])

points = mlab.pipeline.scalar_scatter(x, y, z, d/2.0)
dataset = points.mlab_source.dataset
dataset.point_data.get_array(0).name = 'diameter'
dataset.lines = np.vstack(edges)

array_id = dataset.point_data.add_array(var_data.T.ravel())
dataset.point_data.get_array(array_id).name = 'var_data'
dataset.point_data.update()

# The tube
src = mlab.pipeline.set_active_attribute(points, point_scalars='diameter')
stripper = mlab.pipeline.stripper(src)
tube = mlab.pipeline.tube(stripper, tube_sides = 6, tube_radius = 1)
tube.filter.capping = True
tube.filter.use_default_normal = False
tube.filter.vary_radius = 'vary_radius_by_absolute_scalar'

src2 = mlab.pipeline.set_active_attribute(tube, point_scalars='var_data')
lines = mlab.pipeline.surface(src2)
