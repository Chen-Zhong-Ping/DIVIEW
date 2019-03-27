
import numpy

from matplotlib.collections import QuadMesh

class StainedGlass2DQuad:

    def __init__(self, axes):

        self.axes = axes

    def draw_from_scratch(self, mesh, data, tangram, ix_region, iy_region):

        # this method is called if it is drawn for the first time or redrawn with changes in mesh or regions.

        self.axes.clear()

        if ix_region is "outer_divertor":
            self.draw_outer_divertor(mesh, data, tangram, iy_region)
        else:
            pass

        self.axes.set_aspect('equal')
        pass

    def draw_outer_divertor(self, mesh, data, tangram, iy_region):

        # first get the mesh collection
        if iy_region is "both":

            plot_data = numpy.transpose(data.IyIx[:, mesh.ixcut[1]:])

            # be careful, here quadmesh is drawn using IxIy order!
            coord = numpy.array(mesh.GridPoint_IxIy[mesh.ixcut[1]:])
            self.stainedglass = QuadMesh(mesh.ny + 1, mesh.nx + 1 - mesh.ixcut[1], coord)

        else:
            pass

        # set linewidth and edgecolor for the mesh frame
        self.set_frame(0.1, (0, 0, 0, 1))

        # then fill with color
        self.paint_glass(plot_data, tangram)

        # add the collection to the axes
        self.axes.add_collection(self.stainedglass)


    def set_frame(self, linewidth, edgecolor):

        # this method can be used to make simple modifications to the linewidth and edgecolor without a complete redrawn from scratch

        self.stainedglass.set_linewidth(linewidth)
        self.stainedglass.set_edgecolor(edgecolor)

    def paint_glass(self, plot_data, tangram):

        # this method can be used whenever data or colorcode is changed, to make simple modifications to the fill color without a complete redrawn from scratch

        colors = tuple(tangram.map2color(x) for x in numpy.ravel(plot_data))
        self.stainedglass.set_facecolor(colors)


