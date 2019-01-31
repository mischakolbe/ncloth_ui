from PySide import QtCore
from PySide import QtGui

from shiboken import wrapInstance

from maya import cmds
import maya.OpenMayaUI as omui
from ui import widgets
reload(widgets)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)


class MapTypeComboBox(QtGui.QComboBox):
    __item_styles = {
        "none": "color: rgb(200, 200, 200)",
        "vertex": "color: rgb(108, 178, 223); font: bold",
        "texture_inactive": "color: rgb(211, 68, 58)",
        "texture_active": "color: rgb(150, 215, 118); font: bold",
    }

    __modes = {
        "none": "None",
        "vertex": "Vert",
        "texture": "Text",
    }

    def __init__(self, map_type_mode=0, *args, **kwargs):
        super(MapTypeComboBox, self).__init__()
        # Initialize values
        self.texture_node = ""

        # Initialize basic look
        self.setFixedSize(55, 20)
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
        context_menu = QtGui.QMenu()
        if self.currentText() == self.__modes["texture"]:
            # Add an input textField to specify the texture node
            texture_node_field = QtGui.QLineEdit(self.texture_node)
            texture_node_field.textChanged.connect(self.update_texture_node)

            # Add the textField to the menu
            texture_node_action = QtGui.QWidgetAction(context_menu)
            texture_node_action.setDefaultWidget(texture_node_field)
            context_menu.addAction(texture_node_action)

            # Add a button to clear the textField
            context_menu.addAction("Clear", texture_node_field.clear)

        context_menu.exec_(self.mapToGlobal(pos))

    def update_texture_node(self, text):
        self.texture_node = text
        self.set_chosen_item_color()


class TestUI(QtGui.QMainWindow):

    def __init__(self, parent=maya_main_window(), *args, **kwargs):
        super(TestUI, self).__init__(parent, *args, **kwargs)

        self.create_ui()

    def create_ui(self):
        """
        Create the UI
        """
        self.setWindowTitle("TestUI")
        self.setMinimumWidth(300)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.central_widget = QtGui.QWidget()
        self.central_widget.setObjectName("central_widget")
        self.setCentralWidget(self.central_widget)

        # Create main layout. Everything goes within this main layout within the central widget
        self.central_layout = QtGui.QVBoxLayout(self.central_widget)
        self.setLayout(self.central_layout)
        self.central_layout.setAlignment(QtCore.Qt.AlignTop)
        self.central_layout.setSpacing(0)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setObjectName("central_layout")
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


        # self.combo = QtGui.QComboBox(self)
        # self.combo.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.combo.customContextMenuRequested.connect(self.showMenu)

        self.test_buttonA = MapTypeComboBox(2)
        self.test_buttonB = MapTypeComboBox(2)

        # self.test_button.clicked.connect(self.do_magic)

        # Add to central layout
        self.central_layout.addWidget(self.test_buttonA)
        self.central_layout.addWidget(self.test_buttonB)



    def do_magic(self):
        print "ASS"


def launch_ui():

    ui = TestUI()
    ui.show()
