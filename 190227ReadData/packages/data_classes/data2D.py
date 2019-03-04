
class Data2D:
    
    def __init__(self, mesh_obj, data2D_file):
        
        if mesh_obj.nx is None or mesh_obj.ny is None :
            print("the mesh object is empty, please read a mesh file first")
        
        else:
            import numpy
            textarray = numpy.loadtxt(data2D_file, skiprows=1)
            self.IyIx = textarray[:, 3].reshape((mesh_obj.ny + 1, mesh_obj.nx + 1), order='C')
