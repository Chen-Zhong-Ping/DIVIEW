
import numpy

from matplotlib.collections import QuadMesh

class StainedGlass2DQuad:

    def __init__(self, axes):

        self.axes = axes

    def draw_from_scratch(self, mesh, data, tangram, ix_region, iy_region, linewidth, edgecolor):

        # this method is called if it is drawn for the first time or redrawn with changes in mesh or regions.

        self.axes.clear()

        # if a region is not drawn, it will be None. This is reset everytime this method is called for a complete redrawn
        self.stainedglass = {"inner_divertor": None, "outer_divertor": None, "core": None}

        # first get the mesh collection
        if ix_region is "inner_divertor":
            self.draw_inner_divertor(mesh, iy_region)
        elif ix_region is "outer_divertor":
            self.draw_outer_divertor(mesh, iy_region)
        elif ix_region is "core":
            self.draw_core(mesh, iy_region)
        else:    # "full" draw the whole thing
            self.draw_inner_divertor(mesh, iy_region)
            self.draw_outer_divertor(mesh, iy_region)
            self.draw_core(mesh, iy_region)

        # set linewidth and edgecolor for the mesh frame
        self.set_frame(linewidth, edgecolor)

        # then fill with color
        self.paint_glass(mesh, data, tangram, iy_region)

        self.axes.set_aspect('equal')


    def draw_outer_divertor(self, mesh, iy_region):

        # be careful, here quadmesh is drawn using IxIy order!
        outer_divertor_grid_IxIy = numpy.array(mesh.GridPoint_IxIy[mesh.ixcut[1]:])

        # get the mesh collection
        if iy_region is "both":

            coord = outer_divertor_grid_IxIy
            self.stainedglass["outer_divertor"] = QuadMesh(mesh.ny + 1, mesh.nx + 1 - mesh.ixcut[1], coord)

        elif iy_region is "SOL":

            coord = outer_divertor_grid_IxIy[:, mesh.iycut:, :]    # you can not do multi-dimensional slicing in Python, have to slice on numpy array
            self.stainedglass["outer_divertor"] = QuadMesh(mesh.ny + 1 - mesh.iycut, mesh.nx + 1 - mesh.ixcut[1], coord)

        else:   # "PFR"

            coord = outer_divertor_grid_IxIy[:, : mesh.iycut + 1, :]
            self.stainedglass["outer_divertor"] = QuadMesh(mesh.iycut, mesh.nx + 1 - mesh.ixcut[1], coord)


        # add the collection to the axes
        self.axes.add_collection(self.stainedglass["outer_divertor"])

    def draw_inner_divertor(self, mesh, iy_region):

        inner_divertor_grid_IxIy = numpy.array((*mesh.GridPoint_IxIy[:mesh.ixcut[0]], (*mesh.GridPoint_IxIy[mesh.ixcut[1]][:mesh.iycut], *mesh.GridPoint_IxIy[mesh.ixcut[0]][mesh.iycut:])))    # has to concatinate two sections to make the last radial surface.

        if iy_region is "both":

            coord = inner_divertor_grid_IxIy
            self.stainedglass["inner_divertor"] = QuadMesh(mesh.ny + 1, mesh.ixcut[0], coord)

        elif iy_region is "SOL":

            coord = inner_divertor_grid_IxIy[:, mesh.iycut:, :]
            self.stainedglass["inner_divertor"] = QuadMesh(mesh.ny + 1 - mesh.iycut, mesh.ixcut[0], coord)

        else: # "PFR"
            coord = inner_divertor_grid_IxIy[:, : mesh.iycut + 1, :]
            self.stainedglass["inner_divertor"] = QuadMesh(mesh.iycut, mesh.ixcut[0], coord)

        self.axes.add_collection(self.stainedglass["inner_divertor"])

    def draw_core(self, mesh, iy_region):

        core_grid_IxIy = numpy.array((*mesh.GridPoint_IxIy[mesh.ixcut[0]:mesh.ixcut[1]], (*mesh.GridPoint_IxIy[mesh.ixcut[0]][:mesh.iycut], *mesh.GridPoint_IxIy[mesh.ixcut[1]][mesh.iycut:])))

        if iy_region is "both":

            coord = core_grid_IxIy
            self.stainedglass["core"] = QuadMesh(mesh.ny + 1, mesh.ixcut[1] - mesh.ixcut[0], coord)

        elif iy_region is "SOL":

            coord = core_grid_IxIy[:, mesh.iycut:, :]
            self.stainedglass["core"] = QuadMesh(mesh.ny + 1 - mesh.iycut, mesh.ixcut[1] - mesh.ixcut[0], coord)

        else: # "PFR"

            coord = core_grid_IxIy[:, : mesh.iycut + 1, :]
            self.stainedglass["core"] = QuadMesh(mesh.iycut, mesh.ixcut[1] - mesh.ixcut[0], coord)

        self.axes.add_collection(self.stainedglass["core"])


    def set_frame(self, linewidth, edgecolor):

        # this method can be used to make simple modifications to the linewidth and edgecolor without a complete redrawn from scratch

        for ix_region, frame in self.stainedglass.items():
            if frame is None:
                pass
            else:
                frame.set_linewidth(linewidth)
                frame.set_edgecolor(edgecolor)

    def paint_glass(self, mesh, data, tangram, iy_region):

        # this method can be used whenever data or colorcode is changed, to make simple modifications to the fill color without a complete redrawn from scratch
        # the loop will go through all 3 ix_regions, so the option ix_region = "full" is also taken care of.

        for ix_region, frame in self.stainedglass.items():

            if frame is None:    # skip the regions not to be drawn
                pass

            elif ix_region is "outer_divertor":
                if iy_region is "both":
                    plot_data = numpy.transpose(data.IyIx[:, mesh.ixcut[1]:])
                elif iy_region is "SOL":
                    plot_data = numpy.transpose(data.IyIx[mesh.iycut:, mesh.ixcut[1]:])
                else:    # "PFR"
                    plot_data = numpy.transpose(data.IyIx[:mesh.iycut, mesh.ixcut[1]:])
                    
                colors = tuple(tangram.map2color(x) for x in numpy.ravel(plot_data))
#                self.stainedglass["outer_divertor"].set_facecolor(colors)
                frame.set_facecolor(colors)

            elif ix_region is "inner_divertor":
                if iy_region is "both":
                    plot_data = numpy.transpose(data.IyIx[:, :mesh.ixcut[0]])
                elif iy_region is "SOL":
                    plot_data = numpy.transpose(data.IyIx[mesh.iycut:, :mesh.ixcut[0]])
                else:    # "PFR"
                    plot_data = numpy.transpose(data.IyIx[:mesh.iycut, :mesh.ixcut[0]])

                colors = tuple(tangram.map2color(x) for x in numpy.ravel(plot_data))
                frame.set_facecolor(colors)

            else:    # "core"
                if iy_region is "both":
                    plot_data = numpy.transpose(data.IyIx[:, mesh.ixcut[0]:mesh.ixcut[1]])
                elif iy_region is "SOL":
                    plot_data = numpy.transpose(data.IyIx[mesh.iycut:, mesh.ixcut[0]:mesh.ixcut[1]])
                else:    # "PFR"
                    plot_data = numpy.transpose(data.IyIx[:mesh.iycut, mesh.ixcut[0]:mesh.ixcut[1]])

                colors = tuple(tangram.map2color(x) for x in numpy.ravel(plot_data))
                frame.set_facecolor(colors)
