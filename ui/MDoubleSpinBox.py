"""

"""
from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets

import MTool
reload(MTool)
import MLabel
reload(MLabel)


class FloatFieldVector(QtWidgets.QWidget):

    def __init__(
            self,
            node_name,
            attr_names,
            height=20,
            min_value=-10000000,
            max_value=10000000,
            *args,
            **kwargs
    ):
        super(FloatFieldVector, self).__init__(*args, **kwargs)

        # Set up size of FloatFieldSlider widget
        self.setSizePolicy(MTool.FixedHeightPolicy())
        self.setObjectName("FloatFieldVector")

        # Create main layout
        main_layout = QtWidgets.QHBoxLayout(self)
        self.setContentsMargins(0, 0, 0, 0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create label
        self.attr_label = MLabel.AttrLabel(self.tr(attr_names[0]))
        # Add to layout
        main_layout.addWidget(self.attr_label)

        # Create float field
        self.float_fields = []
        for attr_name in attr_names:
            float_field = QtWidgets.QDoubleSpinBox()
            float_field.setRange(min_value, max_value)
            float_field.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
            float_field.setFocusPolicy(QtCore.Qt.StrongFocus)
            float_field.setSizePolicy(MTool.FixedHeightPolicy())
            float_field.setMinimumSize(QtCore.QSize(55, 0))
            float_field.setFixedHeight(height)
            float_field.setDecimals(3)
            float_field.setObjectName("float_field")
            float_field.setValue(0)
            main_layout.addWidget(float_field)

            self.float_fields.append(float_field)
