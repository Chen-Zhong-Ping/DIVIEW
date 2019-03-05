
# import kivy modules for GUI

from kivy.app import App

from kivy.core.window import Window

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner

from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.properties import BooleanProperty

from kivy.uix.treeview import TreeView, TreeViewNode
from kivy.uix.recycleview import RecycleView


# import custom modules

from packages.data_classes.data2D import Data2D
from packages.data_classes.mesh import Mesh


# import standard modules

import os.path
import numpy


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

        GUI.root.case_spinner.add_mesh_case(mesh_name)       # automatically add a new mesh_case pertaining to this mesh to the spinner
        BDT.set_current_mesh(mesh_name)                 # set the current mesh to be the newly added one

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
            self.load(data_name, data_unit)

####################################################################
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

        GUI.root.datalist_panel.add_data_set(case_name)
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
            self.load(case_name, description)

####

#### panel for a list of data pertaining to each simulation case ####

class DataListPanel(RecycleView):

    def __init__(self, **kwargs):
        super(DataListPanel, self).__init__(**kwargs)
#        self.data = []
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
            self.load(data_name, data_unit, True)

####################################################################
####################################################################


####################################################################
################## panel for data calculator #######################

class Calculator(BoxLayout):
    type_indicator = ObjectProperty(None)
    cal_var_name = ObjectProperty(None)        # use "var" instead of "data" to indicate data array calculated in this app
    cal_var_unit = ObjectProperty(None)
    cal_var_formula = ObjectProperty(None)

    def clear_inputs(self):
        self.cal_var_name.text = ""
        self.cal_var_formula.text = ""
        self.cal_var_formula.text = ""
        self.type_indicator.is_geomesh_type.trigger_action(duration=0.1)        # have to use this to trigger a button action event
#        self.type_indicator.is_geomesh_type.active = True        # since setting it to True will not set the other one to False. kivy bug.


class CalculationVarableType_RadioButton(BoxLayout):
    is_geometry_variable = BooleanProperty(True)
    is_simulation_variable = BooleanProperty(False)
    is_geomesh_type = ObjectProperty(None)

    pass

####################################################################
####################################################################



####################################################################
####################################################################

class FrontEndGUI(BoxLayout):
    meshlist_panel = ObjectProperty(None)        # "kivy property names must start with a lowercase letter" fuck ya.
    case_spinner = ObjectProperty(None)
    datalist_panel = ObjectProperty(None)

    pass

class PrototypeApp(App):
    title = "ScreenManager prototype"
    bdt = ObjectProperty(None)
    def build(self):
        self.bdt = BDT            # for reference to the BDT from inside .kv file
        return FrontEndGUI()

class BackendDataTracker:

    def __init__(self):
        self.current_mesh = None         # indicator of the current mesh (i.e. current set of cases)
        self.current_case = None
        self.data_tree = {}        # use a dictionary hierarchy to store and track all the simulation data

    def set_current_mesh(self, mesh_name):
        self.current_mesh = mesh_name
        GUI.root.case_spinner.sync_current_mesh()

    def set_current_case(self, case_name):
        self.current_case = case_name
        GUI.root.datalist_panel.sync_current_case()

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
        self.data_tree[self.current_mesh]["geom_var_ref"][data_name] = self.data_tree[self.current_mesh][data_name]["data2D_IyIx"]  # update refdict

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

            GUI.root.meshlist_panel.add_geom_info(var_name, unit)    # make the change appear in GUI

        else:
            self.data_tree[self.current_mesh][self.current_case][var_name] = {}
            self.data_tree[self.current_mesh][self.current_case][var_name]["data2D_IyIx"] = eval(formula, {**self.data_tree[self.current_mesh]["geom_var_ref"], ** self.data_tree[self.current_mesh][self.current_case]["simu_var_ref"]})    # evaluate the formula, with references using combination of the geom_var_ref and simu_var_ref dictionaries.

            self.data_tree[self.current_mesh][self.current_case]["simu_var_ref"][var_name] = self.data_tree[self.current_mesh][self.current_case][var_name]["data2D_IyIx"]    # update the refdict

            GUI.root.datalist_panel.add_data(var_name, unit, False)    # make the change appear in GUI
        pass

BDT = BackendDataTracker()        # reference to the backend data handling

Window.size = (1200, 600)        # set the initial window size upon launching

GUI = PrototypeApp()            # reference to the frontend GUI, from inside this .py script
GUI.run()                # this has to be the last line, once App.run() is called, the session enters the GUI and we go from there.


#if __name__ == "__main__":        # this has to be at the end
#    PrototypeApp().run()
#    running_app= App.get_running_app()
#    GUI = running_app.root
