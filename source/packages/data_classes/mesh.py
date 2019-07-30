
class Mesh:
    
    def __init__(self, sno_file = None):
        
        self.RxBtor = None
        self.nx = None
        self.ny = None
        self.ncut = None
        self.ixcut = None
        self.iycut = None
        
        self.CellIndex1D_IyIx = []
        self.FieldRatio_IyIx = []
        self.CellCenter_IyIx = []
        self.GridPoint_IyIx = []    # this one is (ny+2)x(nx+2)
        self.CellVertices_IyIx = []
        
        self.CellIndex1D_IxIy = []
        self.FieldRatio_IxIy = []
        self.CellCenter_IxIy = []
        self.GridPoint_IxIy = []    # this one is (nx+2)x(ny+2)
        self.CellVertices_IxIy = []
        
        self.read_sno(sno_file)
        
    def read_sno(self, sno_file):
        
        if sno_file is None:
            pass
        
        else:
            # open the mesh file
            lines = []
            with open(sno_file, 'rt') as input_file :
                for line in input_file :
                    lines.append(line)
                    
            # read constants
            self.RxBtor = float((lines[3].replace('=',' ').split())[1])
            self.nx = int((lines[4].replace('=',' ').split())[1]) + 1    # adjust to 0-based indices, the poloical cell index runs 0:nx , totalling nx+1 cells
            self.ny = int((lines[5].replace('=',' ').split())[1]) + 1    # adjust to 0-based indices, the radial cell index runs 0:ny , totalling ny+1 cells
            self.ncut = int((lines[6].replace('=',' ').split())[1])
            self.ixcut = (int((lines[7].replace('=',' ').split())[1]) + 1, int((lines[7].replace('=',' ').split())[2]) + 1)    # adjust to 0-based cell indices to the right/east of the cuts
            self.iycut = int((lines[8].replace('=',' ').split())[1]) + 1    # adjust to 0-based cell index to the up/north of the separatrix
            
            # read mesh

            # first treat rows (flux surfaces) iy = 0 ~ ny-1
            iline = 12
            for iy in range(self.ny) :
                
                cellIndex1DIx = []
                fieldRatioIx = []
                centerIx = []
                southwestIx = []
                verticesIx = []
                
                for ix in range(self.nx + 1) :
                    
                    cellIndex1DIx.append(ix + iy*(self.nx + 1))
        
                    lineparse = lines[iline].replace('=',' ').replace('(',' ').replace(',',' ').replace(')',' ').replace(':',' ').split()
                    northwest = (float(lineparse[4]), float(lineparse[5]))
                    northeast = (float(lineparse[6]), float(lineparse[7]))
        
                    lineparse = lines[iline + 1].replace('=',' ').replace('(',' ').replace(',',' ').replace(')',' ').split()
                    fieldRatioIx.append(float(lineparse[2]))
                    centerIx.append((float(lineparse[3]), float(lineparse[4])))
        
                    lineparse = lines[iline + 2].replace('(',' ').replace(',',' ').replace(')',' ').split()
                    southwestIx.append((float(lineparse[0]), float(lineparse[1])))
                    southeast = (float(lineparse[2]), float(lineparse[3]))
        
                    verticesIx.append((southwestIx[-1], southeast, northeast, northwest))
        
                    iline += 4
            
                southwestIx.append(southeast)    # at the end of each iy iteration, append the grid point on the east boundary to the flux surface
                
                self.CellIndex1D_IyIx.append(cellIndex1DIx)
                self.FieldRatio_IyIx.append(fieldRatioIx)
                self.CellCenter_IyIx.append(centerIx)
                self.GridPoint_IyIx.append(southwestIx)
                self.CellVertices_IyIx.append(verticesIx)
                
            # then the last row is the north boundary cells, iy = ny, treat it separately
            # need to clear out the temp lists used in the above loops.
            cellIndex1DIx = []
            fieldRatioIx = []
            centerIx = []
            southwestIx = []
            verticesIx = []

            northwest = []
            for ix in range(self.nx + 1) :

                cellIndex1DIx.append(ix + self.ny*(self.nx + 1))    # notice iy = ny now!

                lineparse = lines[iline].replace('=',' ').replace('(',' ').replace(',',' ').replace(')',' ').replace(':',' ').split()
                northwest.append((float(lineparse[4]), float(lineparse[5])))
                northeast = (float(lineparse[6]), float(lineparse[7]))

                lineparse = lines[iline + 1].replace('=',' ').replace('(',' ').replace(',',' ').replace(')',' ').split()
                fieldRatioIx.append(float(lineparse[2]))
                centerIx.append((float(lineparse[3]), float(lineparse[4])))

                lineparse = lines[iline + 2].replace('(',' ').replace(',',' ').replace(')',' ').split()
                southwestIx.append((float(lineparse[0]), float(lineparse[1])))
                southeast = (float(lineparse[2]), float(lineparse[3]))

                verticesIx.append((southwestIx[-1], southeast, northeast, northwest[-1]))

                iline += 4

            southwestIx.append(southeast)    # append the grid point on the east boundary to the flux surface
            northwest.append(northeast)    # append the grid point on the east boundary to the flux surface

            self.CellIndex1D_IyIx.append(cellIndex1DIx)
            self.FieldRatio_IyIx.append(fieldRatioIx)
            self.CellCenter_IyIx.append(centerIx)
            self.GridPoint_IyIx.append(southwestIx)
            self.GridPoint_IyIx.append(northwest)    # adding the north boundary
            self.CellVertices_IyIx.append(verticesIx)
            
            # make a transpose copy
            self.CellIndex1D_IxIy = tuple(zip(*self.CellIndex1D_IyIx))
            self.FieldRatio_IxIy = tuple(zip(*self.FieldRatio_IyIx))
            self.CellCenter_IxIy = tuple(zip(*self.CellCenter_IyIx))
            self.GridPoint_IxIy = tuple(zip(*self.GridPoint_IyIx))    # this one is (nx+2)x(ny+2)
            self.CellVertices_IxIy = tuple(zip(*self.CellVertices_IyIx))
