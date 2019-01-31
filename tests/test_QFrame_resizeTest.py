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


class TestSlider(QtGui.QSlider):

    def __init__(self, *args, **kwargs):
        super(TestSlider, self).__init__()

        # Initialize basic look
        self.setFixedSize(200, 20)


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

        self.frame_widget = QtGui.QFrame()
        self.frame_widget.setLineWidth(2)
        self.frame_widget.setContentsMargins(2, 2, 2, 2)
        self.frame_widget.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Sunken)

        self.frame_layout = QtGui.QVBoxLayout(self.frame_widget)
        self.frame_layout.setStretch(1, 1)

        self.button_a = QtGui.QPushButton("Lala!")
        self.button_a.clicked.connect(self.delete_stuff)
        self.button_b = QtGui.QPushButton("Oh no!")
        self.button_c = QtGui.QPushButton("Outside Button")

        self.frame_layout.addWidget(self.button_a)
        self.frame_layout.addWidget(self.button_b)

        self.central_layout.addWidget(self.frame_widget)
        self.central_layout.addWidget(self.button_c)

    def delete_stuff(self):
        self.button_b.setVisible(False)


def launch_ui():

    ui = TestUI()
    ui.show()
