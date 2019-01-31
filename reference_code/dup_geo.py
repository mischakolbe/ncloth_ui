from PySide import QtCore
from PySide import QtGui
# import traceback
from contextlib import contextmanager
from shiboken import wrapInstance

from maya import cmds
import maya.OpenMayaUI as omui


def _get_selected_objects_by_type(obj_type):
    """
    Look for the selected objects type and return a list of names
    with the correct type.
    :Parameter:
        obj_type : `str`
            type of object we are looking for

    :return: Name of the selected objects
    :rtype: `list`
    """
    obj_list = []
    user_selection = cmds.ls(selection=True)

    for element in user_selection:
        element_relatives = cmds.listRelatives(element)
        if (element_relatives
                and cmds.nodeType(element_relatives[0]) == obj_type):
            obj_list.append(element)

    return obj_list


def _get_selection():
    """
    Look at objects already selected by the user.
    Send to _get_selected_objects_by_type what type of object
    we are looking for create a dictionary with the correct objects
    if the user has selected some.
    Geo --> last selection
    curve --> first selection
    up curve --> last selection

    :return: A dictionary with the name of the selected objects
    with one geometry, one curve and one up curve
    :rtype: `dict`
    """
    selection_dict = {'geometry': '',
                      'curve': '',
                      'up_curve': ''}
    geo_list = _get_selected_objects_by_type("mesh")
    if geo_list:
        geo = geo_list[-1]
        selection_dict['geometry'] = geo

    curve_list = _get_selected_objects_by_type("nurbsCurve")
    bezier_list = _get_selected_objects_by_type("bezierCurve")
    for bezier in bezier_list:
        curve_list.append(bezier)

    if curve_list:
        curve = curve_list[0]
        selection_dict['curve'] = curve
        up_curve = curve_list[-1]
        selection_dict['up_curve'] = up_curve

    return selection_dict


def launch_ui():
    """Run the window that will allow the user to select the options
    needed to run the Duplicate Geo tool.
    Get the dictionary of the selected objects from _get_selection
    and send it to DuplicateGeoUI.

    :return: An instance of the running dialog. Reference this to avoid
             the dialog being garbage collected.
    :rtype: DuplicateGeoUI dialog
    """
    dialog = DuplicateGeoUI(parent=main_window(), **_get_selection())
    dialog.show()

    return dialog


class DuplicateGeoUI(QtGui.QDialog):
    """A window to allow the user to specify options needed for the
    Duplicate Geo tool. The window will specify Geo to duplicate,
    the curve along which it will be duplicate, the number of duplications
    and the orientation of those duplications.
    """

    def __init__(self, parent=None, geometry='', curve='', up_curve=''):
        """Initialization method. and set global variables

        :Keywords:
            parent : `QtGui.QWidget` or `None`
                The parent widget to embed this dialog within.
                If None do not embed this widget into another.
            geometry : `string`
                name of the last geometry selected
            curve : `string`
                name of the first curve selected
            up_curve : `string`
                name of the last curve selected
        """
        super(DuplicateGeoUI, self).__init__(parent=parent)
        self.geometry = geometry
        self._geo_height = 0
        if self.geometry:
            self._geo_height = cmds.exactWorldBoundingBox(self.geometry)[4]
        self.curve = curve
        self.up_curve = up_curve

        self.setWindowTitle('Duplicate Geo Along Curve')
        self.setModal(False)
        self.setWindowModality(QtCore.Qt.NonModal)
        self.create_widgets()
        self.build_layout()
        self.connect_buttons()
        self.pre_fill_widget()

    def create_widgets(self):
        """Build ui widgets"""
        # Get geometry
        get_geo_tooltip = 'Select geometry to duplicate along the curve'
        self.get_geo_label = QtGui.QLabel('Geometry Name')
        self.get_geo_label.setToolTip(get_geo_tooltip)
        self.get_geo_line = QtGui.QLineEdit('')
        self.get_geo_button = QtGui.QPushButton('Get Geo')

        # Get Curve
        get_curve_tooltip = ('Select curve along which you '
                             'want to duplicate the geometry')
        self.get_curve_label = QtGui.QLabel('Curve Name')
        self.get_curve_label.setToolTip(get_curve_tooltip)
        self.get_curve_line = QtGui.QLineEdit('')
        self.get_curve_button = QtGui.QPushButton('Get Curve')

        # Get UpCurve
        get_up_curve_tooltip = 'Optional, Curve to setup geometry orientation'
        self.get_up_curve_label = QtGui.QLabel('Up Curve Name')
        self.get_up_curve_label.setToolTip(get_up_curve_tooltip)
        self.get_up_curve_line = QtGui.QLineEdit('')
        self.get_up_curve_line.setPlaceholderText("Optional")
        self.get_up_curve_button = QtGui.QPushButton('Get Up Curve')

        # nB Copy
        nb_pieces_tooltip = 'Number of duplications'
        self.nb_pieces_label = QtGui.QLabel('Number of pieces')
        self.nb_pieces_label.setToolTip(nb_pieces_tooltip)
        self.nb_pieces_box = QtGui.QSpinBox()
        self.nb_pieces_box.setValue(10)
        self.nb_pieces_box.setMinimum(1)
        self.nb_pieces_box.setMaximum(10000000)
        self.nb_pieces_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.nb_pieces_slider.setRange(1, 300)
        self.nb_pieces_slider.setPageStep(self.nb_pieces_slider.maximum()/20.0)

        # Apply
        self.apply_button = QtGui.QPushButton('Apply')

        # Separation Widgets
        self.separation_label = QtGui.QLabel("Separation")
        self.separation_box = QtGui.QDoubleSpinBox()
        # start off with no gaps between the duplicates
        self.separation_box.setValue(0)
        # allow inter-penetration but only till the objects overlap
        self.separation_box.setMinimum(-1)
        self.separation_box.setMaximum(10000000)
        self.separation_box.setDecimals(5)
        self.separation_box.setEnabled(False)

        # Select Up Curve Widget
        self.select_up_curve_button = QtGui.QPushButton("Select Up Curve")
        self.select_up_curve_button.setEnabled(False)

    def build_layout(self):
        """Layout ui widgets."""
        # groupBox Layout
        new_duplication_group = QtGui.QGroupBox()
        new_duplication_group.setTitle('Create New Duplication')

        last_duplication_group = QtGui.QGroupBox()
        last_duplication_group.setTitle('Last Duplication')

        # add widget to layout
        new_duplication_layout = QtGui.QGridLayout()
        new_duplication_layout.addWidget(self.get_geo_label, 0, 0)
        new_duplication_layout.addWidget(self.get_geo_line, 0, 1, 1, 2)
        new_duplication_layout.addWidget(self.get_geo_button, 0, 3)
        new_duplication_layout.addWidget(self.get_curve_label, 1, 0)
        new_duplication_layout.addWidget(self.get_curve_line, 1, 1, 1, 2)
        new_duplication_layout.addWidget(self.get_curve_button, 1, 3)
        new_duplication_layout.addWidget(self.get_up_curve_label, 2, 0)
        new_duplication_layout.addWidget(self.get_up_curve_line, 2, 1, 1, 2)
        new_duplication_layout.addWidget(self.get_up_curve_button, 2, 3)
        new_duplication_layout.addWidget(self.nb_pieces_label, 3, 0)
        new_duplication_layout.addWidget(self.nb_pieces_slider, 3, 1, 1, 2)
        new_duplication_layout.addWidget(self.nb_pieces_box, 3, 3)
        new_duplication_layout.addWidget(self.apply_button, 5, 1, 1, 2)

        last_duplication_layout = QtGui.QGridLayout()
        last_duplication_layout.addWidget(self.separation_label, 1, 0)
        last_duplication_layout.addWidget(self.separation_box, 1, 1)
        last_duplication_layout.addWidget(
            self.select_up_curve_button, 2, 1, 1, 1)

        # set layout settings
        new_duplication_layout.setColumnStretch(0, 0)
        new_duplication_layout.setColumnStretch(1, 1)
        new_duplication_layout.setColumnStretch(2, 1)
        new_duplication_layout.setColumnStretch(3, 0)

        last_duplication_layout.setColumnStretch(0, 0)
        last_duplication_layout.setColumnStretch(1, 1)
        last_duplication_layout.setColumnStretch(2, 1)

        # set layout to groupBox
        new_duplication_group.setLayout(new_duplication_layout)
        last_duplication_group.setLayout(last_duplication_layout)

        # main layout
        self.main_layout = QtGui.QGridLayout()
        # add widget to main layout
        self.main_layout.addWidget(new_duplication_group, 0, 0)
        self.main_layout.addWidget(last_duplication_group, 1, 0)

        # set layout to dialog
        self.setLayout(self.main_layout)

    def connect_buttons(self):
        """Connect signals."""
        self.apply_button.clicked.connect(self.apply)
        self.get_curve_button.clicked.connect(self.set_curve_field_from_sel)
        self.get_geo_button.clicked.connect(self.set_geo_field_from_sel)
        self.get_up_curve_button.clicked.connect(
            self.set_up_curve_field_from_sel)
        self.nb_pieces_slider.valueChanged[int].connect(
            self.nb_copy_slider_changed)
        self.nb_pieces_box.valueChanged[int].connect(self.nb_copy_box_changed)
        self.separation_box.valueChanged[float].connect(
            self.separation_box_changed)
        self.select_up_curve_button.clicked.connect(self.select_up_curve)

    def apply(self):
        """
        Harvest UI values and deliver to duplication function

        The values from the UI are captured, typecast, then passed on to the
        duplicate_geo_along_curve function which in turn does the actual
        duplication and offset setup.
        """
        curve_name = self.get_curve_line.text()
        geo_name = self.get_geo_line.text()
        up_curve_name = self.get_up_curve_line.text()
        nb_pieces = self.nb_pieces_box.value()
        if curve_name and geo_name:
            cmds.undoInfo(chunkName='apply chunk', openChunk=True)
            duplication_value = duplicate_geo_along_curve(
                curve=curve_name,
                base_geo=geo_name,
                dup_amount=nb_pieces,
                up_curve=up_curve_name)
            self.last_up_curve = duplication_value[0]
            self.last_separation_attr = duplication_value[1]

            self.separation_box.setEnabled(True)
            self.select_up_curve_button.setEnabled(True)
            cmds.undoInfo(chunkName='apply chunk', closeChunk=True)

        else:
            QtGui.QMessageBox.critical(None, 'Error',
                                       'Select a geometry and a curve')

    def set_curve_field_from_sel(self):
        """get a curve name from _get_selection
        set the widget accordingly
        """
        curve = _get_selection()['curve']
        if curve:
            if curve != str(self.get_up_curve_line.text()):
                self.get_curve_line.setText(curve)
            else:
                QtGui.QMessageBox.critical(None, 'Error',
                                           'Up Curve and Curve has to '
                                           'be different')
        else:
            QtGui.QMessageBox.critical(None, 'Error',
                                       'Select a curve')

    def set_up_curve_field_from_sel(self):
        """get a up curve name from _get_selection
        set the widget accordingly
        """
        up_curve = _get_selection()['up_curve']
        if up_curve:
            if up_curve != str(self.get_curve_line.text()):
                self.get_up_curve_line.setText(up_curve)
            else:
                QtGui.QMessageBox.critical(None, 'Error',
                                           'Up Curve and Curve has to '
                                           'be different')
        else:
            QtGui.QMessageBox.critical(None, 'Error',
                                       'Select a curve')

    def set_geo_field_from_sel(self):
        """get a geometry name from _get_selection
        set the widget accordingly
        """
        geo = _get_selection()['geometry']
        if geo:
            self.get_geo_line.setText(geo)
            self._geo_height = cmds.exactWorldBoundingBox(self.geometry)[4]
        else:
            QtGui.QMessageBox.critical(None, 'Error',
                                       'Select a geometry')

    def nb_copy_slider_changed(self, value):
        """ connect slider value to box value"""
        if value < self.nb_pieces_slider.maximum():
            self.nb_pieces_box.setValue(value)
        else:
            pass

    def nb_copy_box_changed(self, value):
        """connect box value to slider value"""
        self.nb_pieces_slider.setValue(value)

    def separation_box_changed(self):
        """Connect box value to saved separation attribute"""
        sep_box = float(self.separation_box.value())
        nb_pieces = self.nb_pieces_box.value()
        # with this the separation value of the spin box will refer to
        # the number of the shapes that would fit between duplications
        # ie. sep_box = 0 means no gap between duplications
        #     sep_box = 1 means 1 shape fits between each duplication
        #     sep_box = 2 means 2 shape fits between each duplication
        base_separation = self._geo_height * (nb_pieces - 1)
        separation_offset = sep_box + 1
        separation_value = base_separation * separation_offset
        cmds.setAttr(self.last_separation_attr, separation_value)

    def select_up_curve(self):
        """Select Up Curve"""
        up_curve = self.last_up_curve
        cmds.select(up_curve)

    def pre_fill_widget(self):
        """Get the name of the pre selected objects and
        pre fill the correspondant widget"""
        self.get_geo_line.setText(self.geometry)
        self.get_curve_line.setText(self.curve)
        if self.up_curve != self.curve:
            self.get_up_curve_line.setText(self.up_curve)

launch_ui()
