import numpy as np
from enthought.mayavi import mlab



class Animator(object):
    
    def __init__(self):
        
        self.scalar_active_attribute = None

    def add_scalar_array(self, dataset, tube, scalar_data, scalar_data_name):
        
        # Remove the array if exist
        dataset.point_data.remove_array(scalar_data_name)
        dataset.point_data.update()
        
        # Adding the new scalar
        array_id = dataset.point_data.add_array(scalar_data.T.ravel())
        dataset.point_data.get_array(array_id).name = scalar_data_name
        dataset.point_data.update()
        
        src2 = mlab.pipeline.set_active_attribute(tube, 
                                                  point_scalars=scalar_data_name)
        self.scalar_active_attribute = src2
        lines = mlab.pipeline.surface(src2)
        mlab.scalarbar(lines, title=scalar_data_name)
        #return lines
    
    


        
    
    def change_scalar_array(self, dataset, scalar_data, scalar_data_name):

        dataset.point_data.remove_array(scalar_data_name)
        dataset.point_data.update()
        
        # Adding the new scalar
        array_id = dataset.point_data.add_array(scalar_data.T.ravel())
        dataset.point_data.get_array(array_id).name = scalar_data_name
        dataset.point_data.update()
        mlab.draw()
        #self.scalar_active_attribute.point_scalars_name = scalar_data_name
    

    
    # The tube    
    def draw_tube(self, points, point_scalars='diameter'):
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
    
    my_scalar_name = 'my_scalar_data'
    scalar_data = np.array([0.1,0.3,0.5])
    
    points = mlab.pipeline.scalar_scatter(x, y, z, d/2.0, 
                                          scalars=scalar_data)
    
    dataset = points.mlab_source.dataset
    dataset.point_data.get_array(0).name = 'diameter'
    dataset.lines = np.vstack(edges)
    
    animator = Animator()
    
    tube = animator.draw_tube(points)
    animator.add_scalar_array(dataset, tube, scalar_data, my_scalar_name)
    
    # uncomment the to change the array.
    # the array change, however no difference in the figure.
    # animator.change_scalar_array(dataset, array([1,3,5]), my_scalar_name)
    
    
    
    
    
    