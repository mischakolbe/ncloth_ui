from PySide import QtCore
from PySide import QtGui
# import traceback
from contextlib import contextmanager
from shiboken import wrapInstance

from maya import cmds
import maya.OpenMayaUI as omui


class ConvertCurvesToMeshUi(QtGui.QMainWindow):
    """
    Window to allow the user to convert curves to meshes and while dynamically
    changing the radius

    """

    def __init__(self, *args, **kwargs):
        super(ConvertCurvesToMeshUi, self).__init__(*args, **kwargs)

        self._meshes = []

        self.setWindowTitle("Convert curves to mesh")

        # Setup the widgets
        central_widget = QtGui.QWidget()
        self.setCentralWidget(central_widget)
        self.vertical_layout = QtGui.QVBoxLayout(central_widget)
        self.vertical_layout.setSpacing(0)

        # Create a button to create the initial geo
        self.create_button = QtGui.QPushButton("Create meshes")


        # Create a button to dynamically control the radius of the geo
        self.attributes_widgets = [
            AttributeWidget("Radius:", "radius", minimum=0.01, maximum=2, default_value=0.1),
            AttributeWidget("Taper:", "taper", maximum=10, default_value=1),
            AttributeWidget("Twist:", "twist", maximum=360),
            AttributeEnumWidget("Length Divisions Spacing:", "lengthDivisionsSpacing", ["uniform", "parametric"], default_value=1),
            AttributeWidget("Length Divisions:", "lengthDivisions", 3, maximum=15, data_type=int),
            AttributeWidget("Width Divisions:", "widthDivisions", 7, maximum=15, data_type=int)
        ]

        # Create a button to finalise and clean up the geo
        self.finalise_button = QtGui.QPushButton("Combine meshes")


        # Add to the layout
        self.vertical_layout.addWidget(self.create_button)
        self.vertical_layout.addSpacing(20)

        # Add the attribute widgets
        for widget in self.attributes_widgets:
            self.vertical_layout.addWidget(widget)

        self.vertical_layout.addSpacing(20)
        self.vertical_layout.addStretch()
        self.vertical_layout.addWidget(self.finalise_button)

        # Set the size of the window
        self.setMaximumHeight(self.sizeHint().height())
        self.setMinimumHeight(self.sizeHint().height())
        self.setMinimumWidth(300)

        # Center the window to the screen
        self.center()

        self.create_connections()

    def create_connections(self):
        """
        Create the signal/slot connections.

        """
        # Create the connections
        self.create_button.clicked.connect(self.create_geo)
        self.finalise_button.clicked.connect(self.finalise_geo)

    def center(self):
        """
        Centre the window.

        """
        frame_geo = self.frameGeometry()
        centre_point = QtGui.QDesktopWidget().availableGeometry().center()
        frame_geo.moveCenter(centre_point)
        self.move(frame_geo.topLeft())

    def create_geo(self):
        """

        """
        meshes = cfx.utils.groom.convert_curves_to_meshes()

        # Convert to pymel nodes
        self._meshes = pm.ls(meshes)

        for widget in self.attributes_widgets:
            widget._nodes = self._meshes
            widget._update_nodes()

    def finalise_geo(self):
        """

        """
        try:
            meshes = [node.nodeName() for node in self._meshes]
            cfx.utils.groom.convert_curves_to_meshes_cleanup(meshes)
        finally:
            self._meshes = []

            for widget in self.attributes_widgets:
                widget._nodes = []
