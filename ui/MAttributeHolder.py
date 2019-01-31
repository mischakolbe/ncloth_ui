"""
ToDo:

- PySide2: github.com/mottosso/Qt.py  AND  fredrikaverpil.github.io/2016/07/25/dealing-with-maya-2017-and-pyside2/
"""
from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets

from maya import cmds
import pymel.core as pm

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


class FloatSliderMapBox(QtWidgets.QWidget):

    attribute_box_height = 18

    def __init__(
        self,
        node_name="",
        attr_name="",
        value=0,
        add_shy_button=True,
        add_label=True,
        add_slider=True,
        user_range_min=0,
        user_range_max=100,
        add_map_type_selector=True,
        *args,
        **kwargs
    ):
        super(FloatSliderMapBox, self).__init__(*args, **kwargs)

        self.node_name = node_name
        self.attr_name = attr_name

        # Set up size of FloatSliderMapBox widget
        self.setSizePolicy(MTool.FixedHeightPolicy())
        # self.setMinimumSize(QtCore.QSize(0, self.attribute_box_height))
        # self.setMaximumSize(QtCore.QSize(16777215, self.attribute_box_height))
        # self.setObjectName("FloatSliderMapBox")

        # Create layout for all widgets
        self.attr_box_layout = QtWidgets.QHBoxLayout(self)
        self.attr_box_layout.setSpacing(4)
        self.attr_box_layout.setContentsMargins(0, 0, 0, 0)
        # self.attr_box_layout.setObjectName("attr_box_layout")

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # SHY BUTTON
        if add_shy_button:
            self.shy_switch = MButton.ShyButton()

            # Add to layout
            self.attr_box_layout.addWidget(self.shy_switch)  # What are these optional flags?! -> , 0, 1

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # LABEL
        if add_label:
            self.attr_label = MLabel.AttrLabel(self.tr(self.attr_name))

            # Add to layout
            self.attr_box_layout.addWidget(self.attr_label)

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # FLOAT FIELD SLIDER
        if add_slider:
            self.float_field_slider = MSlider.FloatFieldSlider(
                value=value,
                height=self.attribute_box_height,
                user_range_min=user_range_min,
                user_range_max=user_range_max,
            )

            # Connect value change in UI to change Maya value
            self.float_field_slider.float_slider.slider.valueChanged.connect(self.set_maya_attr)

            # Add to layout
            self.attr_box_layout.addWidget(self.float_field_slider)

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # MAP BUTTON
        if add_map_type_selector:
            self.map_type_selector = MComboBox.MapTypeComboBox(self)
            self.map_type_selector.setSizePolicy(MTool.FixedHeightPolicy())
            self.map_type_selector.setMaximumSize(QtCore.QSize(55, 16777215))
            self.map_type_selector.setBaseSize(QtCore.QSize(0, 0))
            # self.map_type_selector.setObjectName("map_type_selector")

            # Add to layout
            self.attr_box_layout.addWidget(self.map_type_selector)

    def set_maya_attr(self, value):
        value = self.float_field_slider.float_slider.slider.value()
        cmds.setAttr("{}.{}".format(self.node_name, self.attr_name), value)

    def set_value(self, value):
        self.float_field_slider.set_value(value)
