
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.popup import Popup

from kivy.properties import ObjectProperty
from kivy.properties import StringProperty

from kivy.uix.treeview import TreeView, TreeViewNode

from kivy.uix.recycleview import RecycleView

from kivy.uix.spinner import Spinner

import os.path




####################################################################
################## panel for a list of mesh ########################

class MeshListPanel(TreeView):

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_loadmeshdialog(self):
        self._popup = Popup(title="add a mesh", size_hint=(0.9, 0.9), 
                            content=LoadMeshDialog(load=self.add_mesh, cancel=self.dismiss_popup))
        self._popup.open()

    def add_mesh(self, mesh_file):
#        newmeshnode = self.add_node(MeshBranchNode(mesh_name))
#        self.add_node(MeshInfoNodeNode(), parent=newmeshnode)
        self.add_node(MeshInfoNodeNode(), parent=self.add_node(MeshBranchNode(mesh_name = os.path.basename(mesh_file))))    # so  in fact I can call a method and use its return value as kwarg in an outer method

        running_app= App.get_running_app()
        running_app.root.case_spinner.add_mesh_case(os.path.basename(mesh_file))        # add a new cases set pertaining to this mesh

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
        self.current_mesh = ""         # indicator of the current mesh (i.e. current set of cases)

    def add_mesh_case(self, mesh_name):    # called whenever a new mesh is added
        self.mesh_cases[mesh_name] = []    # initiate the case set to empty list, this list is the "values" of the spinner.
        self.choose_mesh_case(mesh_name)

    def choose_mesh_case(self, mesh_name):
        self.current_mesh = mesh_name              # update the current case flag
        self.values = self.mesh_cases[mesh_name]    # reflect the update

    def show_addcasedialog(self):
        self._popup = Popup(title="add a simulation case", size_hint=(0.9, 0.9), 
                            content=AddCaseDialog(load=self.add_case, cancel=self.dismiss_popup))
        self._popup.open()

    def add_case(self, case_name, description):     # this methond adds a new case in the current case set (mesh)
        self.mesh_cases[self.current_mesh].append(case_name)     # append a case_name (str) to the current/outstanding case set (mesh)
        self.values = self.mesh_cases[self.current_mesh]    # reflect the change
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
        self.SOLPSdata_sets = {}
        self.current_case = ""

    def add_data_set(self, case_name):
        self.SOLPSdata_sets[case_name] = []
        self.current_case = case_name


####################################################################
####################################################################

class InitialScreen(BoxLayout):
    meshlist_panel = ObjectProperty(None)        # "kivy property names must start with a lowercase letter" fuck ya.
    case_spinner = ObjectProperty(None)
    pass

class PrototypeApp(App):
    title = "ScreenManager prototype"
    def build(self):
        return InitialScreen()

if __name__ == "__main__":
    PrototypeApp().run()
