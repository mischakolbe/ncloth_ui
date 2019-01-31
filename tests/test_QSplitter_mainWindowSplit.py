from PySide import QtCore
from PySide import QtGui

from shiboken import wrapInstance

from maya import cmds
import maya.OpenMayaUI as omui

from ..ui import MAttributeHolder
reload(MAttributeHolder)
from ..ui import MButton
reload(MButton)
from ..ui import MTreeView
reload(MTreeView)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)


class MainWidget(QtGui.QWidget):

    def __init__(self, left_top_widget, left_bot_widget=None, right_widget=None, *args, **kwargs):
        super(MainWidget, self).__init__(*args, **kwargs)

        self.left_top_widget = left_top_widget
        self.left_bot_widget = left_bot_widget
        self.right_widget = right_widget

        self._init_main_widget()

    def _init_main_widget(self):
        self.setContentsMargins(0, 0, 0, 0)

        hbox = QtGui.QHBoxLayout(self)
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)

        # Widget that should be added to main hbox layout
        top_widget = self.left_top_widget

        if self.left_bot_widget is not None:
            self.left_splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
            self.left_splitter.addWidget(self.left_top_widget)
            self.left_splitter.addWidget(self.left_bot_widget)
            top_widget = self.left_splitter

        if self.right_widget is not None:
            self.main_splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
            self.main_splitter.addWidget(top_widget)
            self.main_splitter.addWidget(self.right_widget)
            top_widget = self.main_splitter

        hbox.addWidget(top_widget)


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

        b1 = QtGui.QPushButton("ASS tl")
        b2 = QtGui.QPushButton("ASS bl")
        b3 = QtGui.QPushButton("ASS r")

        view = MainWidget(
            left_top_widget=b1,
            left_bot_widget=b2,
            right_widget=b3
        )

        self.central_layout.addWidget(view)


def launch_ui():

    ui = TestUI()
    ui.show()
