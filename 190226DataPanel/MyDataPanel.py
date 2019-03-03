
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.popup import Popup

from kivy.properties import ObjectProperty
from kivy.properties import StringProperty

from kivy.uix.treeview import TreeView, TreeViewNode

from kivy.uix.recycleview import RecycleView

from kivy.uix.spinner import Spinner

import os.path


# import custom modules

from packages.data_classes.data2D import Data2D
from packages.data_classes.mesh import Mesh



####################################################################
################## panel for a list of mesh ########################

class MeshListPanel(TreeView):

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_loadmeshdialog(self):
        self._popup = Popup(title="add a mesh", size_hint=(0.9, 0.9), 
                            content=LoadMeshDialog(load=self.add_mesh, cancel=self.dismiss_popup))
        self._popup.open()

    def add_mesh(self, mesh_name, mesh_file):

#        self.add_node(MeshInfoNodeNode(), parent=self.add_node(MeshBranchNode(mesh_name = os.path.basename(mesh_file))))    # so  in fact I can call a method and use its return value as kwarg in an outer method

#        GUI.root.case_spinner.add_mesh_case(os.path.basename(mesh_file))       # automatically add a new mesh_case pertaining to this mesh to the spinner
#        BDT.set_current_mesh(os.path.basename(mesh_file))                 # set the current mesh to be the newly added one

        self.add_node(MeshInfoNodeNode(), parent=self.add_node(MeshBranchNode(mesh_name = mesh_name)))

        GUI.root.case_spinner.add_mesh_case(mesh_name)       # automatically add a new mesh_case pertaining to this mesh to the spinner
        BDT.set_current_mesh(mesh_name)                 # set the current mesh to be the newly added one

        self.dismiss_popup()

    def show_load_data_dialog(self):
        self._popup = Popup(title="add geometry information", size_hint=(0.9, 0.9), 
                            content=LoadDataDialog(load=self.add_geom_info, cancel=self.dismiss_popup))
        self._popup.open()

    def add_geom_info(self, name_txt, unit_txt):
        self.add_node(GeomInfoNodeNode(data_name = name_txt, data_unit = unit_txt), parent=self.selected_node.parent_node)
        self.dismiss_popup()

#### TreeView nodes ####

class MeshBranchNode(BoxLayout, TreeViewNode):

    mesh_name = StringProperty()        # you can use it directly as kwarg upon instantiation like MeshBranchNode(mesh_name = "sometext") so you don't need the following initialization

#    def __init__(self, text, **kwargs):
#        super(MeshBranchNode, self).__init__(**kwargs)
#        self.mesh_name = text
   
    pass

class MeshInfoNodeNode(BoxLayout, TreeViewNode):
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
            self.message.text = "Enter a name for the mesh!"
        elif len(filechooser_selection) is 0 :
            self.message.text = "Choose a mesh file!"
        else:
            self.load(mesh_name, filechooser_selection[0])


class LoadDataDialog(BoxLayout):
    load = ObjectProperty(None)        # these will be assigned with the proper function upon instantiation
    cancel = ObjectProperty(None)

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
        self._popup = Popup(title="add a simulation case", size_hint=(0.9, 0.9), 
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
                            content=AddDataDialog(load=self.add_data, cancel=self.dismiss_popup))
        self._popup.open()

    def add_data(self, data_name, data_unit):
        self.SOLPSdata_sets[BDT.current_case].append({"data_name": data_name, "data_unit": data_unit})
        self.data = self.SOLPSdata_sets[BDT.current_case]

        self.dismiss_popup()

        pass

    def dismiss_popup(self):
        self._popup.dismiss()

class DataItem(BoxLayout):        # viewclass of the above recycleview
    data_name = StringProperty()
    data_unit = StringProperty()

class AddDataDialog(BoxLayout):
    load = ObjectProperty(None)        # these will be assigned with the proper function upon instantiation
    cancel = ObjectProperty(None)

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
        pass


BDT = BackendDataTracker()        # reference to the backend data handling

GUI = PrototypeApp()            # reference to the frontend GUI, from inside this .py script
GUI.run()                # this has to be the last line, once App.run() is called, the session enters the GUI and we go from there.


#if __name__ == "__main__":        # this has to be at the end
#    PrototypeApp().run()
#    running_app= App.get_running_app()
#    GUI = running_app.root
