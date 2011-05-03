import numpy as np
from enthought.mayavi import mlab

def add_scalar_array(tube, scalar_data, scalar_data_name):
    array_id = dataset.point_data.add_array(scalar_data.T.ravel())
    dataset.point_data.get_array(array_id).name = scalar_data_name
    dataset.point_data.update()
    src2 = mlab.pipeline.set_active_attribute(tube, 
                                              point_scalars=scalar_data_name)
    lines = mlab.pipeline.surface(src2)
    mlab.scalarbar(lines, title=scalar_data_name)
    return lines

def update_scalar_array(lines, scalar_data, scalar_data_name):
    lines.mlab_source.dataset.point_data.get_array_name(scalar_data_name)

# The tube    
def draw_tube(points, point_scalars='diameter'):
    src = mlab.pipeline.set_active_attribute(points, 
                                             point_scalars=point_scalars)
    stripper = mlab.pipeline.stripper(src)
    tube = mlab.pipeline.tube(stripper, tube_sides = 6, tube_radius = 1)
    tube.filter.capping = True
    tube.filter.use_default_normal = False
    tube.filter.vary_radius = 'vary_radius_by_absolute_scalar'
    return tube



if __name__ == '__main__':
    x=np.array([0,-1,2])
    y=np.array([0,-3,-5])
    z=np.array([0,0,-1])
    d=np.array([3,2,1])
    edges=np.vstack([[0,1],[0,2]])
    
    points = mlab.pipeline.scalar_scatter(x, y, z, d/2.0)
    dataset = points.mlab_source.dataset
    dataset.point_data.get_array(0).name = 'diameter'
    dataset.lines = np.vstack(edges)
    scalar_data = np.array([0.1,0.3,0.5])
    
    tube = draw_tube(points)
    my_scalar_name = 'my_scalar_data'
    lines = add_scalar_array(tube, scalar_data, my_scalar_name)
    
    
    
    
    
    
    