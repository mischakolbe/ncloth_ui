"""
Must support these nodes:
- nRigid
- nCloth
- nucleus
- dynamicConstraint
(- hairSystem)

UI elements needed:
- slider with map dropdown
- slider
- enum
- boolean (checkbox)
- graph
- color
- float display


Common UI Element to inherit from:
Horizontal layout with 2 elements: Name & ctrl. (30% name / 70% ctrl)

UI elements can influence each other: Grey out "inactive" elements, etc.

Combine UI elements for each node type with a dictionary: name, ui-element type, input connection, output connection, min, max, defaultValue, ...

Use YAML/.PY for config file!
https://docs.python.org/2/library/configparser.html

TODO: Clean up all these dependencies. Focus on making one system work correctly at a time! First basic structure, then worry about individual features like slider-dots!
TODO: Create unified UI-element (for each controllable attribute, whether it's a slider/graph/color/...)
TODO: Create a color UI element
TODO: Create a slider UI element.. With optional dropdown?
TODO: Create a slider UI element with dropdown (None, Vertex, Texture)
TODO: Create a boolean UI element (checkbox)
TODO: Create a graph UI element # https://stackoverflow.com/questions/45624912/pyqt-draggable-line-with-multiple-break-points?noredirect=1&lq=1
TODO: Create an enum UI element
TODO: Be able to set UI element states dynamically! (Grey out text of "inactive" elements!)
TODO: Create reliable two-way update method! Must work for all UI elements! When set through Maya UI, custom UI or via Maya code!
"""


from functools import partial

from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets
from Qt import QtCompat

from maya import cmds
import maya.OpenMayaUI as omui

from ui import MUiAttributes
reload(MUiAttributes)
from ui import MContainer
reload(MContainer)
from ui import MTreeView
reload(MTreeView)
from lib import callback
reload(callback)
from ui import MStyle
reload(MStyle)
from ui import MDoubleSpinBox
reload(MDoubleSpinBox)
from ui import MWidget
reload(MWidget)
from ui import MDockWidget
reload(MDockWidget)
from lib import MGlobals
reload(MGlobals)
from lib import MUtil
reload(MUtil)
from ui import MIcon
reload(MIcon)
from ui import MMessageBox
reload(MMessageBox)
from ui import MTool
reload(MTool)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return QtCompat.wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class NClothUi(QtWidgets.QMainWindow):
    """
    Window to allow the user to convert curves to meshes and while dynamically
    changing the radius
    """

    # Could transform all states into a dictionary... (in playground:True/False, etc)
    # data = {
    #     "nodes": {
    #         "node_a_bla": {  # These nodes are gathered from maya scene!
    #             "type": "nCloth",  # nucleus, ...
    #             "collapsed_by_default": {  # List of attrs that are collapsed by default
    #                 "collision"
    #             }
    #         }
    #     }
    # }

    def __init__(self, parent=maya_main_window(), *args, **kwargs):
        super(NClothUi, self).__init__(parent, *args, **kwargs)

        # self.ndynamic_nodes_in_playground = []

        self.node_callbacks = []

        self.create_ui()

    def create_ui(self):
        """
        Create the UI
        """
        self.setWindowTitle("NClothUi")
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.create_layout()

        # Set the size of the window
        self.setMinimumWidth(380)
        self.setGeometry(0, 0, 800, 600)
        MTool.center_to_screen(self)

        # self.setStyleSheet(MStyle.style)

    def create_layout(self):
        """
        Create the layouts and add widgets
        """
        # Add central widget to window. This holds everything inside the window
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setObjectName("central_widget")
        self.central_widget.setContentsMargins(0, 0, 0, 0)

        # Create central layout
        self.central_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.central_layout.setSpacing(0)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setObjectName("central_layout")

        # Create nCloth outliner
        self.ndynamics_outliner = MTreeView.NDynamicsOutliner()

        # Create callbacks for outliner
        self.install_ndynamics_outliner_callbacks()

        # Create node playground window
        self.node_playground_window = MDockWidget.NodePlayGround()
        self.expose_ndynamic_nodes_in_playground_selected_in_outliner()

        # Create tool bar
        self.tool_bar = self.create_tool_bar()

        # Create main splitter widget
        self.splitter_widget = MWidget.MainWidget(
            top_left_widget=self.tool_bar,
            bot_left_widget=self.ndynamics_outliner,
            right_widget=self.node_playground_window
        )

        # Connect renaming from outliner and playground
        self.ndynamics_outliner._datamodel.itemChanged.connect(self.outliner_and_playground_renaming)

        # Add widgets to central_layout
        self.central_layout.addWidget(self.splitter_widget)

    def outliner_and_playground_renaming(self, outliner_item):
        """
        Rename playground dock widget based on outliner-rename
        """
        # Find the dock_widget based on the given outliner item
        dock_widget = self.find_outliner_item_in_playground(outliner_item)
        # If it exists in the playground: Rename it
        if dock_widget is not None:
            dock_widget = dock_widget.setWindowTitle(outliner_item.text())

    def create_tool_bar(self):
        init_tool_bar = QtWidgets.QToolBar()

        # Create expose button
        expose_action = QtWidgets.QAction(MIcon.MIcon("visible"), 'Show', self)
        expose_action.setShortcut('Shift+H')
        expose_action.triggered.connect(self.expose_ndynamic_nodes_in_playground_selected_in_outliner)
        init_tool_bar.addAction(expose_action)

        # Create hide button
        hide_action = QtWidgets.QAction(MIcon.MIcon("shy"), 'Hide', self)
        hide_action.setShortcut('Ctrl+H')
        hide_action.triggered.connect(self.hide_ndynamic_nodes_in_playground_selected_in_outliner)
        init_tool_bar.addAction(hide_action)

        # Create settings button
        settings_action = QtWidgets.QAction(MIcon.MIcon("settings"), 'Settings', self)
        settings_action.triggered.connect(self.settings)
        init_tool_bar.addAction(settings_action)

        # Create info button
        info_action = QtWidgets.QAction(MIcon.MIcon("info"), 'Info', self)
        info_action.setShortcut('F1')
        info_action.triggered.connect(MMessageBox.AboutNClothUiMessageBox)
        init_tool_bar.addAction(info_action)

        # Create quit Button
        exit_action = QtWidgets.QAction(MIcon.MIcon("quit"), 'Quit', self)
        exit_action.triggered.connect(self.close)
        init_tool_bar.addAction(exit_action)

        return init_tool_bar

    def settings(self):
        print("HAHAHA")

    # --------------------------------------------------------------------------
    # SLOTS
    # --------------------------------------------------------------------------

    @property
    def selected_outliner_items(self):
        selected_items = self.ndynamics_outliner.selected_ncloth_outliner_standard_items
        return selected_items

    @property
    def dock_widgets_in_playground(self):
        node_playground_children = []
        for node in self.node_playground_window.children():
            if isinstance(node, MDockWidget.MDockWidget):
                node_playground_children.append(node)

        return node_playground_children

    def find_outliner_item_in_playground(self, outliner_item):
        for dock_widget in self.dock_widgets_in_playground:
            # Compare the mobj the outliner item and dock widget represent
            if outliner_item.mobj is dock_widget.mobj:
                return dock_widget
        return None

    def expose_ndynamic_nodes_in_playground_selected_in_outliner(self):
        """
        For all items selected in the ndynamics outliner: Show their corresponding dock widget
        in the node playground if it's hidden or create it if it doesn't exist yet.
        """
        for outliner_item in self.selected_outliner_items:
            dock_widget = self.find_outliner_item_in_playground(outliner_item)
            if dock_widget is None:
                self.add_ndynamic_node_to_playground(outliner_item)
            else:
                dock_widget.show()

    def hide_ndynamic_nodes_in_playground_selected_in_outliner(self):
        """
        For all items selected in the ndynamics outliner: Hide their corresponding
        dock widget in the node playground, if it exists.
        """
        for outliner_item in self.selected_outliner_items:
            dock_widget = self.find_outliner_item_in_playground(outliner_item)
            if dock_widget is not None:
                dock_widget.hide()

    def close_ndynamic_nodes_in_playground_selected_in_outliner(self):
        """
        For all items selected in the ndynamics outliner: Close their corresponding
        dock widget in the node playground, if it exists.

        This is currently not in use but is probably handy to have, in case
        the user loses a widget or wants to reset it for some other reason.
        """
        for outliner_item in self.selected_outliner_items:
            dock_widget = self.find_outliner_item_in_playground(outliner_item)
            if dock_widget is not None:
                dock_widget.close()

    def add_ndynamic_node_to_playground(self, outliner_item):
        node_name = MUtil._get_name_of_mobj(outliner_item.mobj)
        node_dag_path = MUtil._get_long_name_of_mobj(outliner_item.mobj, full=True)
        node_type = MUtil._get_readable_node_type_of_mobj(outliner_item.mobj)

        # This event function selects the ndynamic outliner item that corresponds
        # to the dock widget the  user currently hovers over
        double_click_event_function = self.ndynamics_outliner.select_ncloth_outliner_item_from_dock_widget
        dock_widget = MDockWidget.MDockWidget(double_click_event_function)
        dock_widget.setWindowTitle(node_name)
        dock_widget.set_mobj(outliner_item.mobj)
        dock_widget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)

        self.attr_tree = MTreeView.AttrTree(node_name)

        ndynamic_type_specific_attr_groups = MGlobals.exposed_attrs_based_on_node_type[node_type]

        # "nucleus": {
        #     "SOME_NUCLEUS_ATTR_GROUP": {
        #         "gravity": ["gravity", "FloatSliderMapBox"],
        #     },

        new_maya_io_handlers = []

        for attr_group in ndynamic_type_specific_attr_groups:
            # Create attr group widget (top-item) here
            new_attr_group = self.attr_tree._append_widget_item(custom_widgets=attr_group)[0]
            new_attr_group.setText(attr_group)

            for cloth_map_ui_name, (cloth_map_maya_name, attr_ctrl_type) in ndynamic_type_specific_attr_groups[attr_group].iteritems():
                attr_type_specific_ctrl = getattr(MUiAttributes, attr_ctrl_type)

                if cmds.attributeQuery(cloth_map_ui_name, node=node_dag_path, softRangeExists=True):
                    user_range_min, user_range_max = cmds.attributeQuery(cloth_map_ui_name, node=node_dag_path, softRange=True)

                new_attr_box = attr_type_specific_ctrl(
                    mobj=outliner_item.mobj,
                    attr=cloth_map_ui_name,
                    user_range_min=user_range_min,
                    user_range_max=user_range_max,
                    value=cmds.getAttr("{}.{}".format(node_name, cloth_map_ui_name)),
                )

                new_maya_io_handlers.append(new_attr_box.maya_io_handler)

                self.attr_tree._append_widget_row(
                    new_attr_group,
                    [new_attr_box]
                )[0]

        # Add callback for this node. Passing on the io_handlers.
        # They suffice to find & update UI elements if attr of node changes
        node_callback = callback.AttrChangedCallbackHandler(
            callback.attr_change_closure(new_maya_io_handlers),
            node_dag_path
        )
        node_callback.install()
        self.node_callbacks.append(node_callback)

        self.attr_tree.expandAll()

        dock_widget.setWidget(self.attr_tree)
        self.node_playground_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock_widget)

    def install_ndynamics_outliner_callbacks(self):
        outliner_mdg_callbacks = [
            ["addNodeAddedCallback", "node_created_closure"],
            ["addNodeRemovedCallback", "node_deleted_closure"],
        ]

        for ndynamic_type in MGlobals.ndynamic_node_types:
            # Add callbacks for this ndynamic_type
            for mdg_callback_type, mdg_callback_func in outliner_mdg_callbacks:
                # Add specific callback type with its appropriate function to run when fired
                callback_func = getattr(callback, mdg_callback_func)
                node_callback = callback.MDGMessageCallbackHandler(
                    callback_func(self.ndynamics_outliner),
                    mdg_callback_type,
                    ndynamic_type
                )
                node_callback.install()
                self.node_callbacks.append(node_callback)

    def closeEvent(self, event):
        # Clean up node_callbacks when UI is closed
        for node_callback in self.node_callbacks:
            print("Uninstalling:", node_callback)
            node_callback.uninstall()

        for outliner_node_callback in self.ndynamics_outliner.outliner_node_callbacks:
            print("Uninstalling:", outliner_node_callback)
            outliner_node_callback.uninstall()


def launch_ui():
    # Development workaround for PySide winEvent error (Maya 2014)
    # Make sure the UI is deleted before recreating
    try:
        ui.close()
    except UnboundLocalError:
        pass

    # Create minimal UI object
    ui = NClothUi()
    ui.show()

    return ui
