
# import kivy modules for GUI

from kivy.app import App

from kivy.core.window import Window

from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.uix.treeview import TreeView, TreeViewNode
from kivy.uix.recycleview import RecycleView

from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.properties import BooleanProperty
from kivy.properties import NumericProperty
from kivy.properties import ListProperty

from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

# import custom modules

from packages.data_classes.data2D import Data2D
from packages.data_classes.mesh import Mesh

from packages.plot_classes.tangram import Tangram

# import standard modules

import os.path
import numpy

from matplotlib import pyplot

####################################################################
################## panel for a list of mesh ########################

class MeshListPanel(TreeView):

    def __init__(self, **kwargs):
        super(MeshListPanel, self).__init__(**kwargs)
        self.mesh_tracker = {}            # key is mesh name, value is the corresponding MeshBranchNode

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_loadmeshdialog(self):
        self._popup = Popup(title="add a mesh", size_hint=(0.9, 0.9), 
                            content=LoadMeshDialog(load=self.add_mesh, cancel=self.dismiss_popup))
        self._popup.open()

    def add_mesh(self, mesh_name):

        mesh_info = str("nx: "+str(BDT.data_tree[mesh_name]["mesh"].nx)+" , ny: "+str(BDT.data_tree[mesh_name]["mesh"].ny)+
                        "\nixcut: ("+str(BDT.data_tree[mesh_name]["mesh"].ixcut[0])+", "+str(BDT.data_tree[mesh_name]["mesh"].ixcut[1])+
                        ") , iycut: "+str(BDT.data_tree[mesh_name]["mesh"].iycut))

        self.mesh_tracker[mesh_name] = self.add_node(MeshBranchNode(mesh_name = mesh_name))

        self.add_node(MeshInfoNodeNode(mesh_info = mesh_info), parent = self.mesh_tracker[mesh_name])

        GUI.root.data_screen.case_spinner.add_mesh_case(mesh_name)       # automatically add a new mesh_case pertaining to this mesh to the spinner
        BDT.set_current_mesh(mesh_name)                 # set the current mesh to be the newly added one
        BPT.add_plotable_mesh(mesh_name)                 # add to the plotable list of BPT

        self.dismiss_popup()

    def show_load_geomdata_dialog(self, mesh_name):
        BDT.set_current_mesh(mesh_name)
        self._popup = Popup(title="add geometry information", size_hint=(0.8, 0.8), 
                            content=LoadGeomDataDialog(load=self.add_geom_info, cancel=self.dismiss_popup))
        self._popup.open()

    def add_geom_info(self, name_txt, unit_txt):
        self.add_node(GeomInfoNodeNode(data_name = name_txt, data_unit = unit_txt), parent = self.mesh_tracker[BDT.current_mesh])    #self.selected_node.parent_node
        self.dismiss_popup()

#### TreeView nodes ####

class MeshBranchNode(BoxLayout, TreeViewNode):

    mesh_name = StringProperty()   
    pass

class MeshInfoNodeNode(BoxLayout, TreeViewNode):
    mesh_info = StringProperty()        # Have to use a StringProperty here to get around the problem
    pass

class GeomInfoNodeNode(BoxLayout, TreeViewNode):
    data_name = StringProperty()
    data_unit = StringProperty()
    pass

####

#### dialogs as contents for popup ####

class LoadMeshDialog(BoxLayout):
    load = ObjectProperty(None)        # these will be assigned with the proper function upon instantiation
    cancel = ObjectProperty(None)
    message = ObjectProperty(None)

    def tryload(self, mesh_name, filechooser_selection):
        if mesh_name is "" :
            self.message.text = "Enter a name for the mesh!"        # warning message
        elif len(filechooser_selection) is 0 :
            self.message.text = "Choose a .sno mesh file!"        # warning message
        else:
            BDT.add_mesh(mesh_name, filechooser_selection[0])        # read and store the mesh file in the backend
            self.load(mesh_name)        # show the changes in the frontend


class LoadGeomDataDialog(BoxLayout):
    load = ObjectProperty(None)        # these will be assigned with the proper function upon instantiation
    cancel = ObjectProperty(None)
    message = ObjectProperty(None)

    def tryload(self, data_name, data_unit, filechooser_selection):
        if data_name is "" :
            self.message.text = "Enter a name for the data!"        # warning message
        elif data_unit is "" :
            self.message.text = "Enter a unit for the data!"        # warning message
        elif len(filechooser_selection) is 0 :
            self.message.text = "Choose a geometry data file!"        # warning message
        else:
            BDT.add_geometry_data(data_name, data_unit, filechooser_selection[0])
            BPT.add_plotable_geometry_data(data_name)        # add to the list of plotables
            self.load(data_name, data_unit)

####################################################################

####################################################################
################ panel for a list of cases/data ####################

#### simulation case name spinner ####

class CaseSpinner(Spinner):

    def __init__(self, **kwargs):
        super(CaseSpinner, self).__init__(**kwargs)
        self.mesh_cases = {}            # key is mesh name, value is case name

    def add_mesh_case(self, mesh_name):    # called whenever a new mesh is added
        self.mesh_cases[mesh_name] = []    # initiate the case set to empty list, this list is the "values" of the spinner.

    def sync_current_mesh(self):
        self.values = self.mesh_cases[BDT.current_mesh]

    def show_addcasedialog(self):
        self._popup = Popup(title="add a simulation case", size_hint=(0.8, 0.8), 
                            content=AddCaseDialog(load=self.add_case, cancel=self.dismiss_popup))
        self._popup.open()

    def add_case(self, case_name, description):             # this method adds a new case in the current case set (mesh)
        self.mesh_cases[BDT.current_mesh].append(case_name)         # append a case_name (str) to the current/outstanding case set (mesh)

        GUI.root.data_screen.datalist_panel.add_data_set(case_name)
        BDT.set_current_case(case_name)

        self.values = self.mesh_cases[BDT.current_mesh]            # reflect the change, this has to be done after datalist_panel.add_data_set(case_name) since the self.text of the spinner will change and there is an on_text event right after.
        self.text = case_name

        self.dismiss_popup()

    def dismiss_popup(self):
        self._popup.dismiss()

    pass

class AddCaseDialog(BoxLayout):
    load = ObjectProperty(None)        # these will be assigned with the proper function upon instantiation
    cancel = ObjectProperty(None)
    message = ObjectProperty(None)

    def tryload(self, case_name, description):
        if case_name is "" :
            self.message.text = "MUST enter a case name!"
        else:
            BDT.add_case(case_name)
            BPT.add_plotable_case(case_name)        # add a case to the list of plotables
            self.load(case_name, description)

####

#### panel for a list of data pertaining to each simulation case ####

class DataListPanel(RecycleView):

    def __init__(self, **kwargs):
        super(DataListPanel, self).__init__(**kwargs)
        self.SOLPSdata_sets = {"": []}             # key is case name, value is option for "data" of RecycleView. When a new mesh is added, spinner text will change to "", so need to have a [] as recycleview data otherwise error.

    def add_data_set(self, case_name):
        self.SOLPSdata_sets[case_name] = []

    def sync_current_case(self):
        self.data = self.SOLPSdata_sets[BDT.current_case]

    def show_adddatadialog(self):
        self._popup = Popup(title="add simulation data from this case", size_hint=(0.9, 0.9), 
                            content=AddSOLPSDataDialog(load=self.add_data, cancel=self.dismiss_popup))
        self._popup.open()

    def add_data(self, data_name, data_unit, is_popup_open):
        self.SOLPSdata_sets[BDT.current_case].append({"data_name": data_name, "data_unit": data_unit})
        self.data = self.SOLPSdata_sets[BDT.current_case]
        if is_popup_open is True:
            self.dismiss_popup()
        else:
            pass

    def dismiss_popup(self):
        self._popup.dismiss()

class DataItem(BoxLayout):        # viewclass of the above recycleview
    data_name = StringProperty()
    data_unit = StringProperty()

class AddSOLPSDataDialog(BoxLayout):
    load = ObjectProperty(None)        # these will be assigned with the proper function upon instantiation
    cancel = ObjectProperty(None)
    message = ObjectProperty(None)

    def tryload(self, data_name, data_unit, filechooser_selection):
        if data_name is "" :
            self.message.text = "Enter a name for the data!"        # warning message
        elif data_unit is "" :
            self.message.text = "Enter a unit for the data!"        # warning message
        elif len(filechooser_selection) is 0 :
            self.message.text = "Choose a simulation data file!"        # warning message
        else:
            BDT.add_simulation_data(data_name, data_unit, filechooser_selection[0])
            BPT.add_plotable_simulation_data(data_name)
            self.load(data_name, data_unit, True)

####################################################################


####################################################################
################## panel for data calculator #######################

class Calculator(BoxLayout):
    type_indicator = ObjectProperty(None)
    cal_var_name = ObjectProperty(None)        # use "var" instead of "data" to indicate data array calculated in this app
    cal_var_unit = ObjectProperty(None)
    cal_var_formula = ObjectProperty(None)
    is_show = BooleanProperty(False)

    def clear_inputs(self):
        self.cal_var_name.text = ""
        self.cal_var_formula.text = ""
        self.cal_var_formula.text = ""
        self.type_indicator.is_geomesh_type.trigger_action(duration=0.1)        # have to use this to trigger a button action event
#        self.type_indicator.is_geomesh_type.active = True        # since setting it to True will not set the other one to False. kivy bug.

    def show_hide(self):
        self.is_show = not self.is_show
        if self.is_show is True:
            self.size_hint_x = 1
            self.opacity = 1
        else:
            self.size_hint_x = 0
            self.opacity = 0

class CalculationVarableType_RadioButton(BoxLayout):
    is_geometry_variable = BooleanProperty(True)
    is_simulation_variable = BooleanProperty(False)
    is_geomesh_type = ObjectProperty(None)

    pass

####################################################################


class DataScreen(Screen):
    meshlist_panel = ObjectProperty(None)        # "kivy property names must start with a lowercase letter" fuck ya.
    case_spinner = ObjectProperty(None)
    datalist_panel = ObjectProperty(None)
    add_case_button = ObjectProperty(None)

####################################################################
####################################################################

####################################################################
####################################################################

class PlotScreen(Screen):
    plot_tabs_binder = ObjectProperty(None)
    pass

####################################################################

class PlotTabsBinder(TabbedPanel):

    def __init__(self, **kwargs):
        super(PlotTabsBinder, self).__init__(**kwargs)
        self.tabs = {}            # key is index, use index(won't change) rather than plot_name(may change) to track each plot.

    def show_addtab_dialog(self):
        self._popup = Popup(title="create a new plot", size_hint=(0.4, 0.4), 
                            content=AddTabDialog(load=self.add_tab, cancel=self.dismiss_popup))
        self._popup.open()

    def add_tab(self, plot_name, plot_type):

        BPT.add_plot(plot_type)

        self.tabs[BPT.current_plot] = {}
#        self.tabs[BPT.count]["plot_name"] = plot_name        # there is actually no need for a "plot_name" variable, use ["plot_tab"].text
        self.tabs[BPT.current_plot]["plot_type"] = plot_type

#        if plot_type is "2d_quad":
#            self.tabs[plot_name]["plot_tab"] = PlotTab(plot_name)
#        else:
#            pass                # later will add other types of plots.

        self.tabs[BPT.current_plot]["plot_tab"] = PlotTab(plot_name, plot_type, BPT.current_plot)    # track each tab
        self.add_widget(self.tabs[BPT.current_plot]["plot_tab"])
        self.switch_to(self.tabs[BPT.current_plot]["plot_tab"])

        self.dismiss_popup()

    def dismiss_popup(self):
        self._popup.dismiss()

    def try_addsubplot(self):    # reason for this detour is to determine whether there is a tab or not, if no tab created nothing done.

        if bool(self.tabs) :    # True if nonempty, False if empty # Empty dictionaries evaluate to False in Python
            self.tabs[BPT.current_plot]["plot_tab"].plot_desk.figaxes_panel.axes_list_subpanel.show_addsubplot_dialog()
        else:
            pass

    pass

class AddTabDialog(BoxLayout):
    load = ObjectProperty(None)        # these will be assigned with the proper function upon instantiation
    cancel = ObjectProperty(None)
    message = ObjectProperty(None)

    def tryload(self, plot_name, polt_type):
        if plot_name is "" :
            self.message.text = "Enter a name for the plot!"        # warning message
        else:
            self.load(plot_name, polt_type)        # plot_name, polt_type
    pass

class PlotTab(TabbedPanelItem):

    def __init__(self, plot_name, plot_type, plot_index, **kwargs):
        super(PlotTab, self).__init__(**kwargs)
        self.text = plot_name
        self.plot_index = plot_index        # use index(won't change) rather than plot_name(may change) to track each plot
#        self.add_widget(PlotDesk(plot_type, index))        # had to do this to correctly pass the index, for some reason can't make it work in kv file

        # step1: initiallize a plot_desk:
        if plot_type in ("2d_quad", "2d_tria"):
            self.plot_desk = PlotDesk_2d()
        else:
            pass    # will add 1d_line type later

        # setp2: set a first look of plot_desk after after initiallization
        # KiVyTrick: set property's first appearence after initiallization
        self.plot_desk.figaxes_panel.fig_name_button.text = plot_name    # text of the fig_name_button, first appearence have to do it here
        self.plot_desk.figaxes_panel.axes_list_subpanel.set_viewclass(plot_type)    # choose a viewclass for the recycleview

        # step3: add the widget
        self.add_widget(self.plot_desk)

    pass

##################################################

class PlotDesk_2d(BoxLayout):

    figaxes_panel = ObjectProperty(None)
    figdixplay_panel = ObjectProperty(None)
    colorbar_panel = ObjectProperty(None)        # this won't be in the 1d plot desk

#    def __init__(self, plot_type, **kwargs):
#        super(PlotDesk, self).__init__(**kwargs)
#        self.index = index        # use index(won't change) rather than plot_name(may change) to track each plot


#        if plot_type is "2d_quad":
#            self.add_widget(FigAxesPanel_2d_quad(index = index, size_hint_x = 0.15))            # had to do this to correctly pass the index
#            self.add_widget(FigDisplayPanel(index = index, size_hint_x = 0.7))
#            self.add_widget(ColorBarPanel_2d(index = index, size_hint_x = 0.15))
#        elif plot_type is "2d_tria":
#            pass
#        else:
#            pass

    pass

####

########
########
########
########  This block looks generic to all types of plots. Simply needs to choose the viewclass of the AxesListSubPanel based on plot_type

class FigAxesPanel(BoxLayout):
#    index = NumericProperty()
    fig_name_button = ObjectProperty(None)
    axes_list_subpanel = ObjectProperty(None)

    def show_changename_dialog(self):
        self._popup = Popup(title="rename the plot", size_hint=(0.3, 0.3), 
                            content=ChangeNameDialog(load=self.change_name, cancel=self.dismiss_popup))
        self._popup.open()

    def change_name(self, new_name):

#        GUI.root.plot_screen.plot_tabs_binder.tabs[BPT.current_plot]["plot_name"] = new_name    # update the name in tracker
        GUI.root.plot_screen.plot_tabs_binder.tabs[BPT.current_plot]["plot_tab"].text = new_name    # update the name of the tab
        self.fig_name_button.text = new_name        # update the name appear on the name button itself

#        BPT.plots[self.index]["plot_name"] = mew_name
#        BPT.plots[self.index]["plot_tab"].text = mew_name

        self.dismiss_popup()

    def dismiss_popup(self):
        self._popup.dismiss()

    pass

class ChangeNameDialog(BoxLayout):    # change name of the figure/tab this looks generic to all plot_types
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    rename_button = ObjectProperty(None)

    def tryload(self, new_name):
        if new_name is "":
            self.rename_button.text = "enter a name!"
        else:
            self.load(new_name)
        pass

####

class AxesListSubPanel(RecycleView):

# it turns out you can not set property values during initiallization! KiVyTrick.
#    def __init__(self, **kwargs):
#        super(AxesListSubPanel, self).__init__(**kwargs)
#        if GUI.root.plot_screen.plot_tabs_binder.tabs[BPT.current_plot]["plot_type"] is "2d_quad":
#            self.viewclass.set("SubPlotItem_2d_quad")
#        else:
#            pass    # will add other types later

# you have to set property values after initiallization if you want to "dynamically" do it in the python file rather than "statically" in kv file. So in this case define a function to choose the value for the AliasProperty viewclass, and call this function after initiallization.

    def set_viewclass(self, plot_type):
        if plot_type is "2d_quad":
            self.viewclass = "SubPlotItem_2d_quad"
        elif plot_type is "2d_tria":
            pass
        else:
            pass    # will add 1d_line type later


    def show_addsubplot_dialog(self):
        self._popup = Popup(title="Add a subplot", size_hint=(0.3, 0.5), pos_hint = {'top': 0.95}, 
                            content=AddSubplotDialog(load = self.update_subplot_list, cancel = self.dismiss_popup))
        self._popup.open()

    def update_subplot_list(self):
        self.data = BPT.plots[BPT.current_plot]["AxesList_settings"]
        self.refresh_from_data()        # has to manually trigger this event, if only the content is modified but len(data) is unchanged.
        self.dismiss_popup()

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_modifysubplot_dialot(self, plot_type, axes_index):

        if plot_type is "2d_quad":
            self._popup = Popup(title="Modify subplot", size_hint=(0.6, 0.8), pos_hint = {'top': 0.95}, 
                            content=ModifySubplotDialog_2d_quad(load = self.update_subplot_list, cancel = self.dismiss_popup, modify_index = axes_index, try_delete = self.show_deletesubplot_dialog))
            self._popup.open()
        elif plot_type is "2d_tria":
            pass
        else:
            pass

    def show_deletesubplot_dialog(self, axes_index):
        self.dismiss_popup()
        self._popup = Popup(title="Delete subplot", size_hint=(0.3, 0.5), pos_hint = {'top': 0.95}, 
                            content=DeleteSubplotDialog(load = self.update_subplot_list, cancel = self.dismiss_popup, delete_index = axes_index))
        self._popup.open()

    pass


class AddSubplotDialog(BoxLayout):    # add an axes to the figure, add an recycleview item to the AxesListSubPanel, looks generic as well.
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    message = ObjectProperty(None)

    def tryload(self, mesh_name, case_name, data_name, axes_name):
        if mesh_name is "":
            self.message.text = "must choose a mesh"
        elif case_name is "":
            self.message.text = "must choose a case"
        elif data_name is "":
            self.message.text = "must choose a data"
        elif axes_name is "":
            self.message.text = "enter a name for the subplot"
        else:
            BPT.add_subplot(axes_name, mesh_name, case_name, data_name)
            self.load()
            pass
    pass


class DeleteSubplotDialog(BoxLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    delete_index = NumericProperty()

    def delete_axes(self):
        BPT.delete_subplot(self.delete_index)
        self.load()

########
########
########
########

####  # 2d_quad special #

class SubPlotItem_2d_quad(BoxLayout):    # view class of AxesListSubPanel if plot_type is 2d_quad
    # use selection at creation
    axes_name = StringProperty()
    mesh_name = StringProperty()
    case_name = StringProperty()
    data_name = StringProperty()

    axes_index = NumericProperty()     # use this to track each item, too bad RecycleView does not provide such function directly

    # use default value at creation
    ix_region = StringProperty()        # poloidal cell index range
    iy_region = StringProperty()        # radial cell index range
    is_mesh_overlay = BooleanProperty()
    axes_x_min = NumericProperty()        # plot range in meters for 2d plots
    axes_x_max = NumericProperty()
    axes_y_min = NumericProperty()
    axes_y_max = NumericProperty()
    pos_axes_left = NumericProperty()    # position of axes on canvas
    pos_axes_bottom = NumericProperty()
    pos_axes_width = NumericProperty()
    pos_axes_height = NumericProperty()  # BE CAREFUL! custom properties name should not conflict the built in keywords!
    pos_axes_z = NumericProperty()

    pass

class ModifySubplotDialog_2d_quad(BoxLayout):    # dialog to modify parameters for an axes/subplot for 2d_quad plot_type
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    modify_index = NumericProperty()
    message = ObjectProperty(None)
    try_delete = ObjectProperty(None)

    def tryload(self, axes_name, mesh_name, case_name, data_name, ix_region, iy_region, is_mesh_overlay, axes_x_min, axes_x_max, axes_y_min, axes_y_max, pos_axes_left, pos_axes_bottom, pos_axes_width, pos_axes_height, pos_axes_z):
        if axes_name is "":
            self.message.text = "subplot name must not be empty"
        elif "" in {axes_x_min, axes_x_max, axes_y_min, axes_y_max, pos_axes_left, pos_axes_bottom, pos_axes_width, pos_axes_height, pos_axes_z}:
            self.message.text = "must fill all input slots for parameters"
        else:
            BPT.modify_subplot(self.modify_index, "2d_quad", axes_name, mesh_name, case_name, data_name, ix_region, iy_region, is_mesh_overlay, axes_x_min, axes_x_max, axes_y_min, axes_y_max, pos_axes_left, pos_axes_bottom, pos_axes_width, pos_axes_height, pos_axes_z)
#            print("modify_index: "+str(self.modify_index))
            self.load()

####  # end of 2d_quad special #

##################################

class ColorbarPanel_2d(BoxLayout):        # this looks generic to both 2d types
    colorcodesubpanel = ObjectProperty(None)

    def show_set_colorbar_dialog(self):
        self._popup = Popup(title="set colorbar", size_hint=(0.25, 0.5), 
                            content=SetColorbarDialog(add_bin=self.show_add_bin_dialog, import_colorbar=self.show_import_colorbar_dialog, save_colorbar=self.show_save_colorbar_dialog, update_settings=self.show_colorbarsettings_dialog, cancel=self.dismiss_popup))
        self._popup.open()
        pass

    def show_add_bin_dialog(self):
        self.dismiss_popup()
        self._popup = Popup(title="add bin", size_hint=(0.25, 0.35), 
                            content=AddBinDialog(load=self.update_colorcodesubpanel, cancel=self.dismiss_popup))
        self._popup.open()

    def update_colorcodesubpanel(self):
        self.colorcodesubpanel.update_colorbar()
        self.dismiss_popup()
        pass

    def show_import_colorbar_dialog(self):
        self.dismiss_popup()
        self._popup = Popup(title="import colorbar file", size_hint=(0.25, 0.45), 
                            content=ImportColorbarDialog(load=self.update_colorcodesubpanel, cancel=self.dismiss_popup))
        self._popup.open()
        pass

    def show_save_colorbar_dialog(self):
        self.dismiss_popup()
        self._popup = Popup(title="save colorbar to file", size_hint=(0.2, 0.25), 
                            content=SaveColorbarDialog(cancel=self.dismiss_popup))
        self._popup.open()
        pass

    def show_colorbarsettings_dialog(self):
        self.dismiss_popup()
        self._popup = Popup(title="colorbar settings", size_hint=(0.35, 0.4), 
                            content=ColorbarSettingsDialog(cancel=self.dismiss_popup))
        self._popup.open()

#    def update_colorbar_settings(self):
#        self.dismiss_popup()

    def dismiss_popup(self):
        self._popup.dismiss()

    pass

class SetColorbarDialog(BoxLayout):
    add_bin = ObjectProperty(None)
    import_colorbar = ObjectProperty(None)
    save_colorbar = ObjectProperty(None)
    update_settings = ObjectProperty(None)
    cancel = ObjectProperty(None)
    pass

class AddBinDialog(BoxLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    message = ObjectProperty(None)

    def tryload(self, bin_value, color_r, color_g, color_b, color_a):
        if "" in {bin_value, color_r, color_g, color_b, color_a}:
            self.message.text = "must fill all slots!"
        elif 0 <= float(color_r) <= 1 and 0 <= float(color_g) <= 1 and 0 <= float(color_b) <= 1 and 0 <= float(color_a) <= 1 :
            BPT.add_colorbar_bin(float(bin_value), (float(color_r), float(color_g), float(color_b), float(color_a)))
            self.load()
        else:
            self.message.text = "color code must be in [0, 1]"

    pass

class ImportColorbarDialog(BoxLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    message = ObjectProperty(None)

    def tryload(self, cb_file_selection):
        if len(cb_file_selection) == 0:
            self.message.text = "no file selected"
        else:
            BPT.import_colorbar(cb_file_selection[0])
            self.load()

class SaveColorbarDialog(BoxLayout):
    cancel = ObjectProperty(None)
    message = ObjectProperty(None)

    def tryload(self, file_name):
        if file_name is "":
            self.message.text = "file name cannot be empty"
        elif len(BPT.plots[BPT.current_plot]["Colorbar"]["tangram"].bin) == 0:
            self.message.text = "colorbar is empty, nothing done"
        else:
            BPT.plots[BPT.current_plot]["Colorbar"]["tangram"].write_colorbar(file_name+".cb")
            self.cancel()
    pass

class ColorbarSettingsDialog(BoxLayout):
    cancel = ObjectProperty(None)
    message = ObjectProperty(None)

    def tryload(self, cb_left, cb_bottom, cb_width, cb_height, cb_z, is_show):
        if "" in {cb_left, cb_bottom, cb_width, cb_height, cb_z}:
            self.message.text = "must fill all slots!"
        elif 0 <= float(cb_left) <= 1 and 0 <= float(cb_bottom) <= 1 and 0 <= float(cb_width) <= 1 and 0 <= float(cb_height) <= 1 :
            BPT.update_colorbar_settings_on_fig(float(cb_left), float(cb_bottom), float(cb_width), float(cb_height), int(cb_z), is_show)
            self.cancel()
        else:
            self.message.text = "pos & size must be in [0, 1]"
    pass

class ColorCodeSubpanel(RecycleView):

    def update_colorbar(self):
        self.data = [*BPT.plots[BPT.current_plot]["Colorbar"]["RecycleViewData"]] # PYTHON!: this is a shallow copy.
        self.data.reverse()         # you can do reverse() without changing the original list but keep in mind modifying a mutable item affects the original list as well! 

    def show_changebin_dialog(self, bin_index, original_color, original_bin_value_str):
        if bin_index == 0:
            self.show_changecolor_dialog(bin_index, original_color, False)
        else:
            self._popup = Popup(title="change bin/color", size_hint=(0.25, 0.4), 
                            content=ChangeBinDialog(change_color=self.show_changecolor_dialog, change_bin_value=self.show_changebinvalue_dialog, cancel=self.dismiss_popup, bin_index = bin_index, original_color = original_color, original_bin_value_str = original_bin_value_str))
            self._popup.open()

    def show_changecolor_dialog(self, bin_index, original_color, is_popup_open):
        if is_popup_open is True:        # when bin_index == 0 bypass ChangeBinDialog and go to ChangeColorDialog directly
            self.dismiss_popup()
        else:
            pass
        self._popup = Popup(title="change color", size_hint=(0.35, 0.25), 
                            content=ChangeColorDialog(load=self.update_no_sort, cancel=self.dismiss_popup, color_bin_index = bin_index, original_color = original_color))
        self._popup.open()

    def show_changebinvalue_dialog(self, bin_index, original_bin_value_str):
        self.dismiss_popup()
        print(bin_index)
        self._popup = Popup(title="change bin value", size_hint=(0.2, 0.25), 
                            content=ChangeBinValueDialog(update_no_sort=self.update_no_sort, update_sort=self.update_colorbar, cancel=self.dismiss_popup, value_bin_index = bin_index - 1, original_value_str = original_bin_value_str))
        self._popup.open()

    def update_no_sort(self):
        self.refresh_from_data()
        self.dismiss_popup()

    def dismiss_popup(self):
        self._popup.dismiss()

    pass


class ColorCodeBin(BoxLayout):        # view class of ColorCodeSubpanel
    bin_index = NumericProperty()     # use this to track each item, too bad RecycleView does not provide such function directly
    bin_value_str = StringProperty()
    bin_color = ListProperty()

class ChangeBinDialog(BoxLayout):
    change_color = ObjectProperty(None)
    change_bin_value = ObjectProperty(None)
    cancel = ObjectProperty(None)
    bin_index = NumericProperty()
    original_color = ListProperty()
    original_bin_value_str = StringProperty()

class ChangeColorDialog(BoxLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    color_bin_index = NumericProperty()
    message =  ObjectProperty(None)
    original_color = ListProperty()

    def tryload(self, color_r, color_g, color_b, color_a):
        if "" in {color_r, color_g, color_b, color_a}:
            self.message.text = "must fill all slots!"
        elif 0 <= float(color_r) <= 1 and 0 <= float(color_g) <= 1 and 0 <= float(color_b) <= 1 and 0 <= float(color_a) <= 1 :
            BPT.change_color(self.color_bin_index, (float(color_r), float(color_g), float(color_b), float(color_a)))
            self.load()
        else:
            self.message.text = "color code must be in [0, 1]"

class ChangeBinValueDialog(BoxLayout):
    update_no_sort = ObjectProperty(None)
    update_sort = ObjectProperty(None)
    cancel = ObjectProperty(None)
    value_bin_index = NumericProperty()
    original_value_str =  StringProperty()
    message =  ObjectProperty(None)

    def tryload(self, new_binvalue_str):
        if new_binvalue_str is "":
            self.message.text = "bin value can't be empty"
        else:
            is_sorted = BPT.change_bin_value(self.value_bin_index, float(new_binvalue_str))
            if is_sorted is False:
                self.update_no_sort()
            elif is_sorted is True:
                self.update_sort()
                self.cancel()         # to close the popup, don't bother changing ColorCodeSubpanel.update_colorbar() anymore
            else:
                self.message.text = "bin value already exists"
                pass

###################################################

class FigDisplayPanel(BoxLayout):

    def __init__(self, **kwargs):
        super(FigDisplayPanel, self).__init__(**kwargs)

        self.fig_canvas = FigureCanvasKivyAgg(BPT.plots[BPT.current_plot]["Figure"])
        self.add_widget(self.fig_canvas)

    def draw_figure(self):

        if BPT.plots[BPT.current_plot]["Colorbar"]["is_changed"] == True :
            BPT.plots[BPT.current_plot]["Colorbar"]["tangram"].draw_colorbar("vertical")
        else:
            pass

        self.fig_canvas.draw()

    pass

####################################################################
####################################################################
#################### custom small widgets ##########################

class FloatInput(TextInput):
    pass

################ end of custom small widgets #######################
####################################################################
####################################################################

####################################################################
####################################################################

# class FrontEndGUI(BoxLayout):
#    meshlist_panel = ObjectProperty(None)        # "kivy property names must start with a lowercase letter" fuck ya.
#    case_spinner = ObjectProperty(None)
#    datalist_panel = ObjectProperty(None)

class FrontEndGUI(ScreenManager):
    data_screen = ObjectProperty(None)
    plot_screen = ObjectProperty(None)
    pass

class PrototypeApp(App):
    title = "DIVIEW prototype"
    bdt = ObjectProperty(None)    # do I need this line ???????????????????????????
    def build(self):
        self.bdt = BDT            # for reference to the BDT from inside .kv file
        self.bpt = BPT            # for reference to the BPT from inside .kv file
        return FrontEndGUI()

###################################################

class BackendDataTracker:

    def __init__(self):
        self.current_mesh = None         # indicator of the current mesh (i.e. current set of cases)
        self.current_case = None
        self.data_tree = {}        # use a dictionary hierarchy to store and track all the simulation data

    def set_current_mesh(self, mesh_name):
        self.current_mesh = mesh_name
        GUI.root.data_screen.case_spinner.sync_current_mesh()
        GUI.root.data_screen.add_case_button.text = mesh_name + " / add a case"

    def set_current_case(self, case_name):
        self.current_case = case_name
        GUI.root.data_screen.datalist_panel.sync_current_case()

    def add_mesh(self, mesh_name, mesh_file):
        self.data_tree[mesh_name] = {}        # add a new branch indexed by the mesh name
        self.data_tree[mesh_name]["mesh"] = Mesh(sno_file = mesh_file)        # the mesh object
        self.data_tree[mesh_name]["mesh_file"] = mesh_file        # keep track of the file
        self.data_tree[mesh_name]["geom_var_ref"] = {"np": numpy}        # dictionary for geometric variable reference used in calculator

    def add_geometry_data(self, data_name, data_unit, data_file):
        self.data_tree[self.current_mesh][data_name] = {}        # add a geometry data under the mesh branch
        self.data_tree[self.current_mesh][data_name]["data2D_IyIx"] = Data2D(mesh_obj = self.data_tree[self.current_mesh]["mesh"], data2D_file = data_file).IyIx
        self.data_tree[self.current_mesh][data_name]["data_unit"] = data_unit
        self.data_tree[self.current_mesh][data_name]["data_file"] = data_file
        self.data_tree[self.current_mesh]["geom_var_ref"][data_name] = self.data_tree[self.current_mesh][data_name]["data2D_IyIx"]  # update refdict for calculator

    def add_case(self, case_name):
        self.data_tree[self.current_mesh][case_name] = {}        # add a new case branch indexed by the case name under the mesh name
        self.data_tree[self.current_mesh][case_name]["simu_var_ref"] = {}    # dictionary for simulation variable reference used in calculator

    def add_simulation_data(self, data_name, data_unit, data_file):
        self.data_tree[self.current_mesh][self.current_case][data_name] = {}        # add a simulation data under the case under mesh branch
        self.data_tree[self.current_mesh][self.current_case][data_name]["data2D_IyIx"] = Data2D(mesh_obj = self.data_tree[self.current_mesh]["mesh"], data2D_file = data_file).IyIx
        self.data_tree[self.current_mesh][self.current_case][data_name]["data_unit"] = data_unit
        self.data_tree[self.current_mesh][self.current_case][data_name]["data_file"] = data_file
        self.data_tree[self.current_mesh][self.current_case]["simu_var_ref"][data_name] = self.data_tree[self.current_mesh][self.current_case][data_name]["data2D_IyIx"]        # update refdict


    def add_calculation_var(self, var_name, unit, formula, is_geomesh_type):

        if is_geomesh_type is True:
            self.data_tree[self.current_mesh][var_name] = {}        # add a geometry data under the mesh branch
            self.data_tree[self.current_mesh][var_name]["data2D_IyIx"] = eval(formula, self.data_tree[self.current_mesh]["geom_var_ref"])    # evaluate the formula, with references using the geom_var_ref dictionary.
            self.data_tree[self.current_mesh][var_name]["data_unit"] = unit
            self.data_tree[self.current_mesh][var_name]["formula"] = formula

            self.data_tree[self.current_mesh]["geom_var_ref"][var_name] = self.data_tree[self.current_mesh][var_name]["data2D_IyIx"]  # update refdict

            GUI.root.data_screen.meshlist_panel.add_geom_info(var_name, unit)    # make the change appear in GUI

        else:
            self.data_tree[self.current_mesh][self.current_case][var_name] = {}
            self.data_tree[self.current_mesh][self.current_case][var_name]["data2D_IyIx"] = eval(formula, {**self.data_tree[self.current_mesh]["geom_var_ref"], ** self.data_tree[self.current_mesh][self.current_case]["simu_var_ref"]})    # evaluate the formula, with references using combination of the geom_var_ref and simu_var_ref dictionaries.

            self.data_tree[self.current_mesh][self.current_case]["simu_var_ref"][var_name] = self.data_tree[self.current_mesh][self.current_case][var_name]["data2D_IyIx"]    # update the refdict

            GUI.root.data_screen.datalist_panel.add_data(var_name, unit, False)    # make the change appear in GUI
        pass

###############################
###############################

class BackendPlotTracker:

    def __init__(self):
        self.current_plot = None         # indicator of the current plot tab, an integer

        self.plots = {}        # use a dictionary to store and track all the plots
        self.count = 0        # the number of total plot tabs have been added

        self.plotables = {}    # providing list of data (names) can be ploted in the add subplot dialog

#### rule of separation: let the plot_screen keep track of the GUI widgets as its children, while BPT tracks the numbers and strings for plotting
    #### use numbers as keys in the dictionary to track figs and axes, since the names can change.

    def add_plot(self, plot_type):

        self.current_plot = self.count    # must update the current_plot index first!

        self.plots[self.count] = {}    # add a dict to BPT.plots, tracks all settings pertaining to this figure

        self.plots[self.count]["Figure"] = pyplot.figure()
        self.plots[self.count]["AxesList"] = []    # a list of Axes not including the colorbar axes

        self.plots[self.count]["AxesList_settings"] = []    # this list will be the AxesListSubPanel(Recycleview) data

        if plot_type in {"2d_quad", "2d_tria"}:
            self.plots[self.count]["Colorbar"] = {} # track everything related to the colorbar
            self.plots[self.count]["Colorbar"]["tangram"] = Tangram(self.plots[self.count]["Figure"].add_axes((0.85, 0.05, 0.3, 0.9)))    # instantiate a color code mapping, add an colorbar axes to the figure and assign it to the class instance variable (see tangram.py)
            self.plots[self.count]["Colorbar"]["RecycleViewData"] = [{"bin_index": 0, "bin_value_str": "", "bin_color": (0, 0, 0, 1)}]    # ColorCodeSubpanel(RecycleView) data
            self.plots[self.count]["Colorbar"]["Position_on_Figure"] = {"left": 0.85, "bottom": 0.05, "width": 0.3, "height": 0.9, "z": 1, "is_show": True}
            self.plots[self.count]["Colorbar"]["is_changed"] = False

            # add a special colorbar axes to the figure
#            self.plots[self.count]["Colorbar"]["Axes"] = self.plots[self.count]["Figure"].add_axes((0.85, 0.1, 0.3, 0.9))
#            self.plots[self.count]["Colorbar"]["Axes"].set_axis_off()

        else:
            pass

        self.count += 1

    
    def set_current_plot(self, index):
        self.current_plot = index
#        print("index: "+str(self.current_plot))


    ######## Related to the AxesListSubpanel ########

    def add_subplot(self, axes_name, mesh_name, case_name, data_name):

        ## use input values for the following, universal for all types of plots
        # plot data related, use the keys to find the data in BDT
        self.plots[self.current_plot]["AxesList_settings"].append({})
        self.plots[self.current_plot]["AxesList_settings"][-1]["axes_name"] = axes_name
        self.plots[self.current_plot]["AxesList_settings"][-1]["mesh_name"] = mesh_name
        self.plots[self.current_plot]["AxesList_settings"][-1]["case_name"] = case_name
        self.plots[self.current_plot]["AxesList_settings"][-1]["data_name"] = data_name

        # this "axes_index" key will let the RecycleView "data" to track each item, the viewclass has a corresponding NumericProperty
        self.plots[self.current_plot]["AxesList_settings"][-1]["axes_index"] = len(self.plots[self.current_plot]["AxesList_settings"]) - 1

        ## set default values for the following
        # axes setting related

        # for 2d_quad type
        if GUI.root.plot_screen.plot_tabs_binder.tabs[self.current_plot]["plot_type"] is "2d_quad":
            self.plots[self.current_plot]["AxesList_settings"][-1]["ix_region"] = "full"        # poloidal cell index range
            self.plots[self.current_plot]["AxesList_settings"][-1]["iy_region"] = "both"        # radial cell index range
            self.plots[self.current_plot]["AxesList_settings"][-1]["is_mesh_overlay"] = False
        else:
            pass

        # for both 2d types
        if GUI.root.plot_screen.plot_tabs_binder.tabs[self.current_plot]["plot_type"] in {"2d_quad", "2d_tria"}:
            self.plots[self.current_plot]["AxesList_settings"][-1]["axes_x_min"] = 0.0               # plot range in meters
            self.plots[self.current_plot]["AxesList_settings"][-1]["axes_x_max"] = 1.0
            self.plots[self.current_plot]["AxesList_settings"][-1]["axes_y_min"] = -1.0
            self.plots[self.current_plot]["AxesList_settings"][-1]["axes_y_max"] = 1.0
            self.plots[self.current_plot]["AxesList_settings"][-1]["pos_axes_left"] = 0.05                # position of axes on canvas
            self.plots[self.current_plot]["AxesList_settings"][-1]["pos_axes_bottom"] = 0.05
            self.plots[self.current_plot]["AxesList_settings"][-1]["pos_axes_width"] = 0.8
            self.plots[self.current_plot]["AxesList_settings"][-1]["pos_axes_height"] = 1.0
            self.plots[self.current_plot]["AxesList_settings"][-1]["pos_axes_z"] = 0
        else:
            pass

        ## append a matplotlib Axes to the list of Axes
        self.plots[self.current_plot]["AxesList"].append(self.plots[self.current_plot]["Figure"].add_axes((0.05, 0.05, 0.8, 1)))

# GUI.root.plot_screen.plot_tabs_binder.tabs[self.current_plot]["plot_tab"].plot_desk.figdixplay_panel.

    def modify_subplot(self, modify_index, plot_type, axes_name, mesh_name, case_name, data_name, ix_region, iy_region, is_mesh_overlay, axes_x_min, axes_x_max, axes_y_min, axes_y_max, pos_axes_left, pos_axes_bottom, pos_axes_width, pos_axes_height, pos_axes_z):

        self.plots[self.current_plot]["AxesList_settings"][modify_index]["axes_name"] = axes_name
        self.plots[self.current_plot]["AxesList_settings"][modify_index]["mesh_name"] = mesh_name
        self.plots[self.current_plot]["AxesList_settings"][modify_index]["case_name"] = case_name
        self.plots[self.current_plot]["AxesList_settings"][modify_index]["data_name"] = data_name

        if plot_type is "2d_quad":
            self.plots[self.current_plot]["AxesList_settings"][modify_index]["ix_region"] = ix_region        # poloidal cell index range
            self.plots[self.current_plot]["AxesList_settings"][modify_index]["iy_region"] = iy_region        # radial cell index range
            self.plots[self.current_plot]["AxesList_settings"][modify_index]["is_mesh_overlay"] = is_mesh_overlay
        else:
            pass

        if plot_type in {"2d_quad", "2d_tria"}:
            self.plots[self.current_plot]["AxesList_settings"][-1]["axes_x_min"] = float(axes_x_min)
            self.plots[self.current_plot]["AxesList_settings"][-1]["axes_x_max"] = float(axes_x_max)
            self.plots[self.current_plot]["AxesList_settings"][-1]["axes_y_min"] = float(axes_y_min)
            self.plots[self.current_plot]["AxesList_settings"][-1]["axes_y_max"] = float(axes_y_max)
            self.plots[self.current_plot]["AxesList_settings"][-1]["pos_axes_left"] = float(pos_axes_left)
            self.plots[self.current_plot]["AxesList_settings"][-1]["pos_axes_bottom"] = float(pos_axes_bottom)
            self.plots[self.current_plot]["AxesList_settings"][-1]["pos_axes_width"] = float(pos_axes_width)
            self.plots[self.current_plot]["AxesList_settings"][-1]["pos_axes_height"] = float(pos_axes_height)
            self.plots[self.current_plot]["AxesList_settings"][-1]["pos_axes_z"] = int(pos_axes_z)
        else:
            pass

    def delete_subplot(self, axes_index):

        ## update the RecycleView data
        del self.plots[self.current_plot]["AxesList_settings"][axes_index]

        # update the axes_index property of each RecycleView item to match the corresponding index in the list
        for i in range(len(self.plots[self.current_plot]["AxesList_settings"])):
            self.plots[self.current_plot]["AxesList_settings"][i]["axes_index"] = i

        ## remove the axes from the fiture in matplotlib
        self.plots[self.current_plot]["Figure"].delaxes(self.plots[self.current_plot]["AxesList"][axes_index])

        # delete the axes from the list
        del self.plots[self.current_plot]["AxesList"][axes_index]

    #### adding the list of plotables whenever a new mesh/case/data is added through the data screen
    #### have not decided whether this should be separate by plot_type, do not see necessity

    def add_plotable_mesh(self, mesh_name):
        self.plotables[mesh_name] = {}        # use same mesh_name to link between BPT.plotables and BDT.data_tree
        self.plotables[mesh_name]["mesh_geometry"] = []    # a list of plotable geometric quantities independent of simulation. "mesh_geometry" same level as case names.
        self.plotables[mesh_name]["mesh_geometry"].append("mesh")

    def add_plotable_geometry_data(self, data_name):
        self.plotables[BDT.current_mesh]["mesh_geometry"].append(data_name)

    def add_plotable_case(self, case_name):
        self.plotables[BDT.current_mesh][case_name] = []    # same level as "mesh_geometry". a list of plotable simulation data

    def add_plotable_simulation_data(self, data_name):
        self.plotables[BDT.current_mesh][BDT.current_case].append(data_name)

    ####

    ######## related to ColorBar panel ########

    def add_colorbar_bin(self, bin_value, bin_color):       
        self.plots[self.current_plot]["Colorbar"]["tangram"].add_bin(bin_value, bin_color)
        self.update_colorbar_view_data()
        self.plots[self.current_plot]["Colorbar"]["is_changed"] = True

    def update_colorbar_view_data(self):
        self.plots[self.current_plot]["Colorbar"]["RecycleViewData"] = [{"bin_index": 0, "bin_value_str": "", "bin_color": self.plots[self.current_plot]["Colorbar"]["tangram"].color[0]}] + [{"bin_index": i+1, "bin_value_str": str(self.plots[self.current_plot]["Colorbar"]["tangram"].bin[i]), "bin_color": self.plots[self.current_plot]["Colorbar"]["tangram"].color[i+1]} for i in range(len(self.plots[self.current_plot]["Colorbar"]["tangram"].bin))]

    def import_colorbar(self, cb_file):
        self.plots[self.current_plot]["Colorbar"]["tangram"].read_colorbar(cb_file)
        self.update_colorbar_view_data()
        self.plots[self.current_plot]["Colorbar"]["is_changed"] = True

    def change_color(self, bin_index, new_color):
        self.plots[self.current_plot]["Colorbar"]["tangram"].color[bin_index] = new_color
        self.plots[self.current_plot]["Colorbar"]["RecycleViewData"][bin_index]["bin_color"] = new_color
        self.plots[self.current_plot]["Colorbar"]["is_changed"] = True

    def change_bin_value(self, value_bin_index, new_binvalue):
        is_sorted = self.plots[self.current_plot]["Colorbar"]["tangram"].change_bin_value(value_bin_index, new_binvalue)
        self.plots[self.current_plot]["Colorbar"]["is_changed"] = True
        if is_sorted is False:
            self.plots[self.current_plot]["Colorbar"]["RecycleViewData"][value_bin_index+1]["bin_value_str"] = str(new_binvalue)
            return False
        elif is_sorted is True:
            self.update_colorbar_view_data()
            return True
        else:
            return None

    def update_colorbar_settings_on_fig(self, left, bottom, width, height, z, is_show):
        self.plots[self.current_plot]["Colorbar"]["Position_on_Figure"] = {"left": left, "bottom": bottom, "width": width, "height": height, "z": z, "is_show": is_show}

        self.plots[self.current_plot]["Colorbar"]["tangram"].axes.set_position((left, bottom, width, height))
        self.plots[self.current_plot]["Colorbar"]["tangram"].axes.set_zorder(z)

        # since it is only the axes position changing not the content, so no need to redraw the colorbar, does not need the following
#        self.plots[self.current_plot]["Colorbar"]["is_changed"] = True
     

###############################

BDT = BackendDataTracker()        # reference to the backend data handling

BPT = BackendPlotTracker()        # reference to the backend plot tracker

Window.size = (1200, 600)        # set the initial window size upon launching

GUI = PrototypeApp()            # reference to the frontend GUI, from inside this .py script
GUI.run()                # this has to be the last line, once App.run() is called, the session enters the GUI and we go from there.

