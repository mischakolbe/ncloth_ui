import maya.api.OpenMaya as om
from maya import cmds

import MUtil


class AbstractCallbackHandler(object):
    def __init__(self, func):
        self.func = func
        self.id = None

    @property
    def node(self):
        try:
            node_name = MUtil._get_name_of_mobj(self.mobj)
            return node_name
        except AttributeError:
            # If Callback has no mobj; pass
            pass

    def uninstall(self):
        if self.id:
            om.MEventMessage.removeCallback(self.id)
            self.id = None
            print("Callback uninstalled:", self.node, self.func)
            return True
        else:
            print("Callback not currently installed")
            return False

    def __del__(self):
        self.uninstall()


# # # # # # # # # # ATTR CHANGE IN SCENE # # # # # # # # # #


def AttrChangedCallbackHandler_test_fn(msg, plug, other_plug, client_data):
    print("Callback fired:", msg, plug, other_plug, client_data)


def attr_change_closure(maya_io_handlers):

    def reflect_attr_change_in_ui(msg, plug, other_plug, client_data):
        # msg 2056 is user-input
        if msg == 2056:
            node, attr = plug.name().split(".")
            # Since the io_handlers are attached to a specific node:
            # There is no need to compare those. Only which attribute
            for maya_io_handler in maya_io_handlers:
                if maya_io_handler.attr == attr:
                    maya_io_handler.io_signal(plug)

    return reflect_attr_change_in_ui


class AttrChangedCallbackHandler(AbstractCallbackHandler):
    """
    cb = AttrChangedCallbackHandler('pCube1', test_fn)
    cb = AttrChangedCallbackHandler('pCube1', attr_change_closure("ui_referenceX"))
    cb.install()
    cb.uninstall()
    del(cb)  # or cb = None
    """

    def __init__(self, func, node, *args, **kwargs):
        super(AttrChangedCallbackHandler, self).__init__(func, *args, **kwargs)

        # Transform given node into MObject
        self.mobj = MUtil._get_mobj_of_node(node)

    def install(self):
        if self.id:
            print("Callback is currently installed")
            return False
        self.id = om.MNodeMessage.addAttributeChangedCallback(self.mobj, self.func)
        print("Callback installed:", self.node, self.func)
        return True


# # # # # # # # # # NODE RENAMING IN SCENE # # # # # # # # # #


def node_rename_closure(outliner_datamodel):

    def reflect_scene_rename_in_ndynamics_outliner(mobj, old_name, client_data):
        item_to_change = outliner_datamodel.find_item_by_mobj_with_path(mobj)
        item_to_change.setText(MUtil._get_name_of_mobj(mobj))

    return reflect_scene_rename_in_ndynamics_outliner


def NodeNameChangedCallbackHandler_test_fn(mobj, old_name, client_data):
    print("Callback fired:", mobj, old_name, client_data)


class NodeNameChangedCallbackHandler(AbstractCallbackHandler):
    """
    """

    def __init__(self, func, node, *args, **kwargs):
        super(NodeNameChangedCallbackHandler, self).__init__(func, *args, **kwargs)

        # Transform given node into MObject
        self.mobj = MUtil._get_mobj_of_node(node)

    def install(self):
        if self.id:
            print("Callback is currently installed")
            return False
        self.id = om.MNodeMessage.addNameChangedCallback(self.mobj, self.func)
        print("Callback installed:", self.node, self.func)
        return True


# # # # # # # # # # NODE CREATION AND DELETION IN SCENE # # # # # # # # # #


def node_created_closure(ndynamics_outliner):

    def reflect_node_creation_in_ui(mobj, clientData):
        node_name = MUtil._get_name_of_mobj(mobj)
        print("reflect_node_creation_in_ui fired for mobj:", node_name, "in outliner:", ndynamics_outliner)
        ndynamics_outliner.refresh_ndynamic_mobj_inventory()
        # IMPLEMENT:
        # More refined ndynamics_outliner method that only adds an item - not refreshes everything!
        # ndynamics_outliner.ADD_A_NODE_FUNCTION_BULLSHIT(node_name)

    return reflect_node_creation_in_ui


def node_deleted_closure(ndynamics_outliner):

    def reflect_node_deletion_in_ui(mobj, clientData):
        node_name = MUtil._get_name_of_mobj(mobj)
        print("reflect_node_deletion_in_ui fired for mobj:", node_name, "in outliner:", ndynamics_outliner)
        ndynamics_outliner.refresh_ndynamic_mobj_inventory()

        # IMPLEMENT:
        # More refined ndynamics_outliner method that only removes an item - not refreshes everything!
        # ndynamics_outliner.REMOVE_A_NODE_FUNCTION_BULLSHIT(node_name)

    return reflect_node_deletion_in_ui


class MDGMessageCallbackHandler(AbstractCallbackHandler):
    """
    """

    def __init__(self, func, callback_type, node_type=None, *args, **kwargs):
        super(MDGMessageCallbackHandler, self).__init__(func, *args, **kwargs)

        self.callback = getattr(om.MDGMessage, callback_type)

        # "dependNode" matches all nodes created or deleted
        self.node_type = node_type

    def install(self):
        if self.id:
            print("Callback is currently installed")
            return False
        if self.node_type is None:
            self.id = self.callback(self.func)
        else:
            self.id = self.callback(self.func, self.node_type)
        print("Callback installed:", self.func)
        return True
