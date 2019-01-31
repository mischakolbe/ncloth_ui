"""
ToDo:

- PySide2: github.com/mottosso/Qt.py  AND  fredrikaverpil.github.io/2016/07/25/dealing-with-maya-2017-and-pyside2/
"""
import collections

from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets

from maya import cmds
import pymel.core as pm

import MIcon
reload(MIcon)


class MapTypeComboBox(QtWidgets.QComboBox):
    __item_styles = {
        "none": "color: rgb(200, 200, 200)",
        "vertex": "color: rgb(108, 178, 223); font: bold",
        "texture_inactive": "color: rgb(211, 68, 58)",
        "texture_active": "color: rgb(150, 215, 118); font: bold",
    }

    __modes = collections.OrderedDict([
        ("none", "None"),
        ("vertex", "Vert"),
        ("texture", "Text"),
    ])

    def __init__(self, parent, map_type_mode=0, *args, **kwargs):
        super(MapTypeComboBox, self).__init__(*args, **kwargs)
        # Initialize values
        self.texture_node = ""
        self.parent = parent

        self.setContentsMargins(0, 0, 0, 0)

        # Initialize basic look
        # self.setFixedSize(55, 20)
        self.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.currentIndexChanged.connect(self.set_chosen_item_color)

        # Add a custom context menu to the QComboBox
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        item_font = QtGui.QFont()
        item_font.setBold(False)
        # Add all modes to the dropDown menu
        for i, menu_item in enumerate(self.__modes.values()):
            self.addItem(menu_item, i)
            # Make sure list items are always normal (not bold) and white
            self.setItemData(i, item_font, QtCore.Qt.FontRole)
            self.setItemData(i, QtGui.QBrush(QtGui.QColor(255, 255, 255)), QtCore.Qt.TextColorRole)

        # Set the mode to what is currently in the scene
        self.setCurrentIndex(int(map_type_mode))

    def set_chosen_item_color(self):
        """
        Set color according to selected item
        """
        if self.currentText() == self.__modes["none"]:
            self.setStyleSheet(self.__item_styles["none"])
        elif self.currentText() == self.__modes["vertex"]:
            self.setStyleSheet(self.__item_styles["vertex"])
        else:
            if cmds.objExists(self.texture_node + ".outAlpha"):
                self.setStyleSheet(self.__item_styles["texture_active"])
            else:
                self.setStyleSheet(self.__item_styles["texture_inactive"])

    def show_context_menu(self, pos):
        context_menu = QtWidgets.QMenu()
        if self.currentText() == self.__modes["texture"]:
            # Add an input textField to specify the texture node
            texture_node_field = QtWidgets.QLineEdit(self.texture_node)
            texture_node_field.textChanged.connect(self.update_texture_node)

            # Add the textField to the menu
            texture_node_action = QtWidgets.QWidgetAction(context_menu)
            texture_node_action.setDefaultWidget(texture_node_field)
            context_menu.addAction(texture_node_action)

            # Add a button to clear the textField
            context_menu.addAction("Clear", texture_node_field.clear)

            context_menu.addSeparator()

        vertex_paint_icon = MIcon.MIcon("visible")
        context_menu.addAction(vertex_paint_icon, "VertexPaint", self.paint_vertex_map)

        context_menu.exec_(self.mapToGlobal(pos))

    def update_texture_node(self, text):
        self.texture_node = text
        self.set_chosen_item_color()

    def paint_vertex_map(self, open_tool_options=True):
        # Important to add:
        # - Select node (mesh) to be painted on
        # - Set map type in Maya to "vertex"!

        # Make sure the MapTypeComboBox item selected is vertex
        self.setCurrentIndex(self.__modes.keys().index('vertex'))

        # Switch to the nCloth painting tool
        if open_tool_options:
            pm.mel.artAttrNClothToolScript(3, self.parent.attr_name)
        else:
            pm.mel.artAttrNClothToolScript(4, self.parent.attr_name)


class SolverDisplayComboBox(QtWidgets.QComboBox):
    __item_styles = {
        "off": "color: rgb(200, 200, 200)",
        "active": "color: rgb(255, 231, 0); font: bold",
    }

    # For nCloth: All   -   For nRigid: Only [Off, Collision Thickness]
    __modes = collections.OrderedDict([
        ("off", "Off"),
        ("collision", "Collision Thickness"),
        ("selfCollision", "Self Collision Thickness"),
        ("stretchLinks", "Stretch Links"),
        ("bendLinks", "Bend Links"),
        ("weighting", "Weighting"),
    ])

    def __init__(self, parent, map_type_mode=0, *args, **kwargs):
        super(SolverDisplayComboBox, self).__init__(*args, **kwargs)
        # Initialize values
        self.texture_node = ""
        self.parent = parent

        self.setContentsMargins(0, 0, 0, 0)

        self.currentIndexChanged.connect(self.set_chosen_item_color)

        item_font = QtGui.QFont()
        item_font.setBold(False)
        # Add all modes to the dropDown menu
        for i, menu_item in enumerate(self.__modes.values()):
            self.addItem(menu_item, i)
            # Make sure list items are always normal (not bold) and white
            self.setItemData(i, item_font, QtCore.Qt.FontRole)
            self.setItemData(i, QtGui.QBrush(QtGui.QColor(255, 255, 255)), QtCore.Qt.TextColorRole)

        # Set the mode to what is currently in the scene
        self.setCurrentIndex(int(map_type_mode))

    def set_chosen_item_color(self):
        """
        Set color according to selected item
        """
        if self.currentText() == self.__modes["off"]:
            self.setStyleSheet(self.__item_styles["off"])
        else:
            self.setStyleSheet(self.__item_styles["active"])
