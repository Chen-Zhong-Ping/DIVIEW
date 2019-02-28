
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.popup import Popup

from kivy.properties import ObjectProperty
from kivy.properties import StringProperty

from kivy.uix.treeview import TreeView, TreeViewNode

import os.path

# from kivy.uix.button import Button


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


class InitialScreen(BoxLayout):
    meshlist_panel = ObjectProperty(None)        # "kivy property names must start with a lowercase letter" fuck ya.
    pass

class PrototypeApp(App):
    title = "TreeView prototype"
    def build(self):
        return InitialScreen()

if __name__ == "__main__":
    PrototypeApp().run()
