"""

"""
from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets

import MTool
reload(MTool)
from ..lib import MUtil
reload(MUtil)


class FloatSlider(QtWidgets.QSlider):

    def __init__(
            self,
            value=0,
            user_range_min=0,
            user_range_max=100,
            slider_precision=3,
            fixed_range=False,
            *args,
            **kwargs
    ):
        super(FloatSlider, self).__init__(*args, **kwargs)

        # Set integer max and min on parent. This range serves as "resultion"
        # for the slider and stays constant!
        super(FloatSlider, self).setMinimum(0)
        self._max_int = 100*10**slider_precision
        super(FloatSlider, self).setMaximum(self._max_int)

        # The min and max values seen by user. Any slider position on this range
        # is converted to the internal min/max so that slider position correlates with user-value
        self._min_value = float(user_range_min)
        self._max_value = float(user_range_max)
        self.fixed_range = fixed_range
        self.exact_value = value

        with MTool.blocked_signal(self):
            self.setValue(self.exact_value)

    @property
    def _value_range(self):
        return self._max_value - self._min_value

    def derivative_value(self):
        """
        This returns the value derived from the underlying range. Needed
        for when user uses slider to dial in value: Has to go through this conversion!
        """
        internal_val = super(FloatSlider, self).value()
        return self.value_transformation(internal_val)

    def value(self):
        """
        This returns the value interesting to the user
        """
        return self.exact_value

    def value_transformation(self, internal_val):
        ratio = internal_val / float(self._max_int)
        return_value = self._min_value + ratio * (self._value_range)
        self.exact_value = return_value

        return return_value

    def setValue(self, value):
        """
        This sets the internal value to what proportionally reflects the user-value
        """
        self.exact_value = value
        # If a new min/max is necessary: Set it to twice the value, to give user leeway
        if value > self._max_value:
            # If the slider range is fixed: Set it to the maximum possible value
            if self.fixed_range:
                value = self.maximum()

            else:
                # In the odd case the new maximum would be below 0: Set it to 0
                if value < 0:
                    self.setMaximum(0)
                else:
                    self.setMaximum(value*2)
        if value < self._min_value:
            # If the slider range is fixed: Set it to the minimum possible value
            if self.fixed_range:
                value = self.minimum()

            else:
                # In the odd case the new minimum would be above 0: Set it to 0
                if value > 0:
                    self.setMinimum(0)
                else:
                    self.setMinimum(value*2)

        # Since the user value can be negative (value - self._min_value) is necessary...
        # ...otherwise internal value could go negative, which is never intended(!)
        zeroed_user_val = (value - self._min_value) / float(self._value_range)
        new_internal_value = int(zeroed_user_val * self._max_int)

        super(FloatSlider, self).setValue(new_internal_value)

        return value

    def maximum(self):
        return self._max_value

    def minimum(self):
        return self._min_value

    def setMinimum(self, value):
        if self.fixed_range:
            # LOGGING: "Slider has fixed range. Can't set to specified value."
            return

        self.setRange(value, self._max_value)

    def setMaximum(self, value):
        if self.fixed_range:
            # LOGGING: "Slider has fixed range. Can't set to specified value."
            return

        self.setRange(self._min_value, value)

    def setRange(self, minimum, maximum):
        # Block signals when updating range, otherwise HistoryCircleSlider
        # updates circle_values twice, which is unwanted
        with MTool.blocked_signal(self):
            # old_value = self.value()
            self._min_value = minimum
            self._max_value = maximum
            self.setValue(self.exact_value)  # Put slider back in correct position

    # Find the current proportion of the slider value relative to the value range
    def proportion(self):
        return (self.value() - self._min_value) / self._value_range


class HistoryCircleSlider(QtWidgets.QWidget):

    brightest_color = (0, 156, 255)
    darkest_color = (24, 90, 150)
    min_circle_dia = 1
    max_circle_dia = 3
    max_num_circles = 3
    y_offset = -5

    def __init__(
            self,
            value=0,
            user_range_min=0,
            user_range_max=100,
            orientation=QtCore.Qt.Horizontal,
            *args,
            **kwargs
    ):
        super(HistoryCircleSlider, self).__init__(*args, **kwargs)
        self.setContentsMargins(0, 0, 0, 0)

        self.slider = FloatSlider(value=value, user_range_min=user_range_min, user_range_max=user_range_max)
        self.slider.setOrientation(orientation)

        layout = QtWidgets.QFormLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.slider)
        self.setLayout(layout)

        self.slider.actionTriggered.connect(self.update_circle_percentages_when_unclicked)

        self.circle_values = [self.slider.value()]

    def circle_percentage(self, circle_value):
        return (circle_value-self.slider.minimum()) / float(self.slider.maximum()-self.slider.minimum())

    def paintEvent(self, event):
        """
        Automatically executed method that draws elements in QWidget
        """
        painter = QtGui.QPainter(self)
        pen = QtGui.QPen(QtGui.QColor(255, 255, 255), 1)

        for i, circle_value in enumerate(self.circle_values[:-1]):
            circle_percentage = self.circle_percentage(circle_value)

            rate = (i+1) / float(len(self.circle_values)-1)

            color = [d+(b-d)*rate for d, b in zip(self.darkest_color, self.brightest_color)]

            pen.setColor(QtGui.QColor(*color))
            painter.setPen(pen)
            dia = self.min_circle_dia + (self.max_circle_dia - self.min_circle_dia)*rate

            # Define min and max pixel values of slider. values 5 and 4 empirically determined
            min_slider_pos = 5
            max_slider_pos = self.slider.size().width() - 4
            # Determine x-position of circle
            pos = circle_percentage * (max_slider_pos-min_slider_pos) + min_slider_pos

            painter.drawEllipse(QtCore.QPoint(pos, self.slider.height()+self.y_offset), dia, dia)

    def update_circle_percentages_when_unclicked(self, *args):
        # Any time the value changed but the slider is not pressed: Update circle percentages
        # Therefore a scripted value change AND a finished mouse-input are handled correctly
        if self.slider.isSliderDown():
            return
        self.update_circle_percentages()

    def update_circle_percentages(self):
        print("UPDATING CIRCLES!")
        # Append the new value and ...
        self.circle_values.append(self.slider.value())
        # ... if the list is longer than max_num_circles...
        # (+1 because list must store current percentage as well, which does not get a circle)
        if len(self.circle_values) > self.max_num_circles + 1:
            # ... drop the currently first entry
            self.circle_values.pop(0)

    def value(self):
        return self.slider.value()

    def setValue(self, value):
        self.slider.setValue(value)


class FloatFieldSlider(QtWidgets.QWidget):

    def __init__(
            self,
            orientation=QtCore.Qt.Horizontal,
            height=20,
            value=0,
            min_value=-10000000,
            max_value=10000000,
            user_range_min=0,
            user_range_max=100,
            *args,
            **kwargs
    ):
        super(FloatFieldSlider, self).__init__(*args, **kwargs)

        # Set up size of FloatFieldSlider widget
        self.setSizePolicy(MTool.FixedHeightPolicy())
        self.setObjectName("FloatFieldSlider")

        # Create float field
        self.float_field = QtWidgets.QDoubleSpinBox()
        self.float_field.setRange(min_value, max_value)
        self.float_field.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.float_field.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.float_field.setSizePolicy(MTool.FixedHeightPolicy())
        self.float_field.setMinimumSize(QtCore.QSize(55, 0))
        self.float_field.setFixedHeight(height)
        self.float_field.setDecimals(3)
        self.float_field.setObjectName("float_field")
        self.float_field.setValue(value)

        # Create slider
        slider_size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        slider_size_policy.setHorizontalStretch(0)
        slider_size_policy.setVerticalStretch(0)

        self.float_slider = HistoryCircleSlider(
            value=value,
            user_range_min=user_range_min,
            user_range_max=user_range_max
        )
        self.float_slider.setSizePolicy(slider_size_policy)
        self.float_slider.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.float_slider.setObjectName("float_slider")

        slidersLayout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight)
        slidersLayout.addWidget(self.float_field)
        slidersLayout.addWidget(self.float_slider)
        self.setLayout(slidersLayout)

        self.setContentsMargins(0, 0, 0, 0)
        slidersLayout.setContentsMargins(0, 0, 0, 0)

    def value(self):
        return self.float_field.value()
