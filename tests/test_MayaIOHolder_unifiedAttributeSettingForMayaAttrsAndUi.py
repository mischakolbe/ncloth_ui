from PySide import QtCore
from PySide import QtGui

from shiboken import wrapInstance
from functools import partial

from maya import cmds
import maya.OpenMayaUI as omui

from ..ui import MUiAttributes
reload(MUiAttributes)
from ..ui import MComboBox
reload(MComboBox)
from ..ui import MSlider
reload(MSlider)
from ..ui import MTool
reload(MTool)
from ..ui import MLabel
reload(MLabel)
from ..lib import MGlobals
reload(MGlobals)
from ..ui import MButton
reload(MButton)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)


class Communicate(QtCore.QObject):

    closeApp = QtCore.Signal()


class MayaIOHolder(object):
    def __init__(self):
        self.callers = []
        self.output_funcs = []

    def add_caller(self, caller):
        self.callers.append(caller)

    def add_output_func(self, func):
        self.output_funcs.append(func)

    def io_signal(self, curr_caller, value):
        # print("~io_signal~", "self:", self, "curr_caller:", curr_caller, "value:", value)
        print("\n~~~ IO START ~~~")
        for caller, output_func in zip(self.callers, self.output_funcs):
            if caller != curr_caller:
                # print(caller)
                if hasattr(caller, "blockSignals"):
                    with MTool.blocked_signal(caller):
                        output_func(caller, value)
                else:
                    output_func(caller, value)
        print("~~~ IO END ~~~")


def calluser(*args):
    print(args)


class TestUI(QtGui.QMainWindow):

    def __init__(self, parent=maya_main_window(), *args, **kwargs):
        super(TestUI, self).__init__(parent, *args, **kwargs)

        self.create_ui()
        self.center_to_screen()

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

        common_io_holder = MayaIOHolder()

        field_a = QtGui.QSpinBox()
        field_a.setPrefix("field_a")
        field_b = QtGui.QSpinBox()
        field_b.setPrefix("field_b")
        field_c = QtGui.QSpinBox()
        field_c.setPrefix("field_c")

        # Add caller to the list (WHO can cause update)
        common_io_holder.add_caller(field_a)
        common_io_holder.add_caller(field_b)
        common_io_holder.add_caller(field_c)
        common_io_holder.add_caller("pCube1.tx")

        # Add output_funcs to list (WHAT happens for each caller)
        common_io_holder.add_output_func(self.test_event)
        common_io_holder.add_output_func(self.test_event)
        common_io_holder.add_output_func(self.test_event)
        common_io_holder.add_output_func(self.test_setter)

        # Connect signals to holder (WHEN does the caller actually call the IOHandler)
        field_a.valueChanged.connect(partial(common_io_holder.io_signal, field_a))
        field_b.valueChanged.connect(partial(common_io_holder.io_signal, field_b))
        field_c.valueChanged.connect(partial(common_io_holder.io_signal, field_c))

        # Add to central layout
        self.central_layout.addWidget(field_a)
        self.central_layout.addWidget(field_b)
        self.central_layout.addWidget(field_c)

    def test_event(self, widget, value):
        print("Setting {} to value {}".format(widget.prefix(), value))
        widget.setValue(value)
        # print("self:", type(self), self, "args:", type(args), args)
        # self.c.closeApp.emit()

    def test_setter(self, attr, value):
        print("Setting {} to value {}".format(attr, value))
        cmds.setAttr(attr, value)

    # def value_changed(self, value):
    #     self.

    def center_to_screen(self):
        """
        Centre the window.

        """
        frame_geo = self.frameGeometry()
        screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
        centre_point = QtGui.QApplication.desktop().screenGeometry(screen).center()
        frame_geo.moveCenter(centre_point)
        self.move(frame_geo.topLeft())


def launch_ui():

    ui = TestUI()
    ui.show()
