"""
ToDo:

- PySide2: github.com/mottosso/Qt.py  AND  fredrikaverpil.github.io/2016/07/25/dealing-with-maya-2017-and-pyside2/
"""
from functools import partial

from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets

import MButton
reload(MButton)
import MComboBox
reload(MComboBox)
import MSlider
reload(MSlider)
import MTool
reload(MTool)
import MLabel
reload(MLabel)
from ..lib import MGlobals
reload(MGlobals)
from ..lib import MUtil
reload(MUtil)


class AbstractBox(QtWidgets.QWidget):
    def __init__(self, mobj, attr, *args, **kwargs):
        super(AbstractBox, self).__init__(*args, **kwargs)

        self.mobj = mobj
        self.attr = attr

        # Add an IO handler to this Box
        self.maya_io_handler = MTool.MayaIOHolder(self.mobj, self.attr)


class FloatSliderMapBox(AbstractBox):

    def __init__(
        self,
        mobj,
        attr,
        value=0,
        add_slider=True,
        user_range_min=0,
        user_range_max=100,
        add_map_type_selector=True,
        *args,
        **kwargs
    ):
        super(FloatSliderMapBox, self).__init__(mobj, attr, *args, **kwargs)

        # Set up size of FloatSliderMapBox widget
        self.setSizePolicy(MTool.FixedHeightPolicy())
        self.setMaximumHeight(MGlobals.attribute_box_height)

        # Create layout for all widgets
        self.attr_box_layout = QtWidgets.QHBoxLayout(self)
        self.attr_box_layout.setSpacing(MGlobals.box_item_spacing)
        self.attr_box_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.attr_box_layout)

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # LABEL
        self.attr_label = MLabel.AttrLabel(self.tr(self.attr))
        # Add to layout
        self.attr_box_layout.addWidget(self.attr_label)

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # FLOAT FIELD SLIDER
        if add_slider:
            self.float_field_slider = MSlider.FloatFieldSlider(
                value=value,
                height=MGlobals.attribute_box_height,
                user_range_min=user_range_min,
                user_range_max=user_range_max,
            )

            # Add to layout
            self.attr_box_layout.addWidget(self.float_field_slider)

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # MAP BUTTON
        if add_map_type_selector:
            self.map_type_selector = MComboBox.MapTypeComboBox(self)
            self.map_type_selector.setSizePolicy(MTool.FixedHeightPolicy())
            self.map_type_selector.setMaximumSize(QtCore.QSize(MGlobals.map_type_selector_width, 16777215))
            self.map_type_selector.setBaseSize(QtCore.QSize(0, 0))
            self.attr_box_layout.addWidget(self.map_type_selector)
        else:
            # If no map_type_selector should be added: Add spacer for visual consistency
            spacer = QtWidgets.QSpacerItem(
                MGlobals.map_type_selector_width + MGlobals.box_item_spacing,
                0,
                QtWidgets.QSizePolicy.Minimum,
                QtWidgets.QSizePolicy.Expanding
            )
            self.attr_box_layout.addItem(spacer)

        self.connect_maya_io_handler()

    def connect_maya_io_handler(self):
        # Add slider
        # WHO can cause update
        self.maya_io_handler.add_caller(self.float_field_slider.float_slider.slider)
        # WHEN does the caller actually call the IOHandler
        self.float_field_slider.float_slider.slider.valueChanged.connect(
            partial(
                self.maya_io_handler.io_signal,
                self.float_field_slider.float_slider.slider
            )
        )

        # Add field
        # WHO can cause update
        self.maya_io_handler.add_caller(self.float_field_slider.float_field)
        # WHEN does the caller actually call the IOHandler
        self.float_field_slider.float_field.editingFinished.connect(
            partial(
                self.maya_io_handler.io_signal,
                self.float_field_slider.float_field
            )
        )


class SolverDisplayBox(AbstractBox):

    def __init__(self, mobj, attr, add_label=True, *args, **kwargs):
        super(SolverDisplayBox, self).__init__(mobj, attr, *args, **kwargs)

        # Set up size of SolverDisplayBox widget
        self.setSizePolicy(MTool.FixedHeightPolicy())

        # Create layout for all widgets
        self.attr_box_layout = QtWidgets.QHBoxLayout(self)
        self.attr_box_layout.setSpacing(MGlobals.box_item_spacing)
        self.attr_box_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.attr_box_layout)

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # LABEL
        if add_label:
            self.attr_label = MLabel.AttrLabel(self.tr(attr))

            # Add to layout
            self.attr_box_layout.addWidget(self.attr_label)

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # SOLVER DISPLAY TYPE DROPDOWN
        self.solver_display_dropdown = MComboBox.SolverDisplayComboBox(self)
        self.attr_box_layout.addWidget(self.solver_display_dropdown)

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # COLOR SELECTOR
        self.color_picker = MButton.MColorButton(self)
        self.color_picker.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.attr_box_layout.addWidget(self.color_picker)
