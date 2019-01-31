"""
ToDo:

- PySide2: github.com/mottosso/Qt.py  AND  fredrikaverpil.github.io/2016/07/25/dealing-with-maya-2017-and-pyside2/
"""
from contextlib import contextmanager

from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets

from maya import cmds
import maya.api.OpenMaya as om

import MSlider
reload(MSlider)
from ..lib import MUtil
reload(MUtil)


@contextmanager
def blocked_signal(widget, active=True):
    """
    Custom context manager that makes it easy to suppress signals temporarily
    """
    widget.blockSignals(active)
    yield
    widget.blockSignals(False)


class FixedHeightPolicy(QtWidgets.QSizePolicy):
    """
    """
    def __init__(self, *args, **kwargs):
        super(FixedHeightPolicy, self).__init__(*args, **kwargs)
        self.setVerticalStretch(False)


def center_to_screen(ui_window):
    """
    Centre the given window.

    """
    frame_geo = ui_window.frameGeometry()
    screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
    centre_point = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
    frame_geo.moveCenter(centre_point)

    ui_window.move(frame_geo.topLeft())


class MayaIOHolder(object):
    """
    # Add caller to the list (WHO can cause update)
    common_io_holder.add_caller(field_a)
    # Add output_funcs to list (WHAT happens if this is not the caller (how is it updated))
    common_io_holder.add_output_func(self.test_event)
    # Connect signals to holder (WHEN does the caller actually call the IOHandler)
    field_a.valueChanged.connect(partial(common_io_holder.io_signal, field_a))

    # The caller and variable in the partial-statement should be the same!
    """

    def __init__(self, mobj, attr):
        self.mobj = mobj
        self.attr = attr

        self.callers = []

    def add_caller(self, caller):
        self.callers.append(caller)

    def io_signal(self, curr_caller, value=None):
        """
        Fundamental idea is: Always go through setting Maya attr (first)!

        (QWidget-valueChange) -> Maya attr change -> QWidget value changes (blocked signal)
        # If this is called by a UI element: Set the Maya-attribute first!
        # This will kick off an MNodeMessage, which in turn will set the UI values!
        """
        # Anything other than an om.MPlug should go through a set-Maya-attr-process first!
        if not isinstance(curr_caller, om.MPlug):
            # Handle FloatSliders differently
            if isinstance(curr_caller, MSlider.FloatSlider):
                # This is very ugly, but internal value is making it difficult
                # to get the right value in here!
                value = curr_caller.value_transformation(value)

            # Handle editingFinished events differently
            if isinstance(curr_caller, QtWidgets.QDoubleSpinBox):
                # Since editingFinished does not return value: Has to be queried manually
                value = curr_caller.value()

            # Set the actual Maya attribute
            MUtil._set_mobj_attribute(self.mobj, self.attr, value)
            return

        # If it got here the curr_caller must be an om.MPlug. Therefore set all UI attributes!
        for caller in self.callers:
            with blocked_signal(caller):
                self.set_widget_value(caller, curr_caller.asFloat())

            if isinstance(caller, MSlider.FloatSlider):
                # FIX THIS! GETS TRIGGERED ALL THE TIME...
                caller.triggerAction(QtWidgets.QAbstractSlider.SliderMove)

        print("~~~ IO END ~~~")

    @staticmethod
    def set_widget_value(widget, value):
        widget.setValue(value)
