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
        super(TestSlider, self).__init__(*args, **kwargs)


class DoubleSlider(QtGui.QSlider):

    def __init__(self, slider_precision=3, *args, **kwargs):
        super(DoubleSlider, self).__init__(*args, **kwargs)

        # Set integer max and min on parent. This range serves as "resultion"
        # for the slider and stays constant!
        super(DoubleSlider, self).setMinimum(0)
        self._max_int = 100*10**slider_precision
        super(DoubleSlider, self).setMaximum(self._max_int)

        # The min and max values seen by user. Any slider position on this range
        # is converted to the internal min/max so that slider position correlates with user-value
        self._min_value = 0.0
        self._max_value = 100.0

    @property
    def _value_range(self):
        return self._max_value - self._min_value

    def value(self):
        """
        This returns the value interesting to the user
        """
        internal_val = super(DoubleSlider, self).value()
        ratio = internal_val / float(self._max_int)
        return_value = self._min_value + ratio * (self._value_range)
        return return_value

    def maximum(self):
        return self._max_value

    def minimum(self):
        return self._min_value

    def setValue(self, value):
        """
        This sets the internal value to what proportionally reflects the user-value
        """

        # If a new min/max is necessary: Set it to twice the value, to give user leeway
        if value > self._max_value:
            # In the odd case the new maximum would be below 0: Set it to 0
            if value < 0:
                self.setMaximum(0)
            else:
                self.setMaximum(value*2)
        if value < self._min_value:
            # In the odd case the new minimum would be above 0: Set it to 0
            if value > 0:
                self.setMinimum(0)
            else:
                self.setMinimum(value*2)

        # Since the user value can be negative (value - self._min_value) is necessary...
        # ...otherwise internal value could go negative, which is never intended(!)
        zeroed_user_val = (value - self._min_value) / float(self._value_range)
        new_internal_value = int(zeroed_user_val * self._max_int)

        super(DoubleSlider, self).setValue(new_internal_value)

    def setMinimum(self, value):
        self.setRange(value, self._max_value)

    def setMaximum(self, value):
        self.setRange(self._min_value, value)

    def setRange(self, minimum, maximum):
        old_value = self.value()
        self._min_value = minimum
        self._max_value = maximum
        self.setValue(old_value)  # Put slider back in correct position

    # Find the current proportion of the slider value relative to the value range
    def proportion(self):
        return (self.value() - self._min_value) / self._value_range





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

        self.test_widget = DoubleSlider()
        self.test_widget.setOrientation(QtCore.Qt.Horizontal)

        self.test_label = QtGui.QLabel()

        self.test_field = QtGui.QLineEdit()

        self.test_widget.setValue(-25)
        self.test_widget.setRange(-60, -20)

        # Add to central layout
        self.central_layout.addWidget(self.test_widget)
        self.central_layout.addWidget(self.test_label)
        self.central_layout.addWidget(self.test_field)

        self.test_widget.valueChanged.connect(self.update_label)
        self.test_field.editingFinished.connect(self.value_update)

    def update_label(self):
        self.test_label.setText(str(self.test_widget.value()))

    def value_update(self):
        new_field_val = float(self.test_field.text())
        # if new_field_val > self.test_widget._min_value:
        #     self.test_widget.setMaximum(new_field_val)
        #     print "WOW, BIG!"
        # if new_field_val < self.test_widget._max_value:
        #     self.test_widget.setMinimum(new_field_val)
        #     print "WOW, SMALL!"

        self.test_widget.setValue(new_field_val)


def launch_ui():

    ui = TestUI()
    ui.show()
