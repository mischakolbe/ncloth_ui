# http://www.chrisevans3d.com/pub_blog/mighty-message-attribute/


import maya.api.OpenMaya as om
from maya import cmds


def print_func(msg, plug, other_plug, client_data):
    """
    Attrs:
        msg: int, Type of message which caused the function to be called
        plug: OpenMaya.MPlug, First plug. Meaning depends upon the specific message which invoked the callback.
        other_plug: OpenMaya.MPlug, Second plug. Meaning depends upon the specific message which invoked the callback.
        client_data: NoneType, Pointer to user-defined data supplied when the callback was registered.

    Example:
        # Values for when pCube1.tx was keyed
        msg: 18433
        plug.name(): pCube1.translateX
        other_plug.name(): animCurveTL1.output
        client_data: None
    """
    if msg == 2056:
        # UserManipulation
        return
    elif msg == 2052:
        # UserManipulation
        return
    elif msg == 18433:
        print "KEY!"
    elif msg == 2064:
        print "LOCK!"
    elif msg == 2080:
        print "UNLOCK!"
    else:
        print "msg:", msg


def test_func(msg, plug, other_plug, client_data):
    if msg == 2064:
        slave = "B.tx"  # UI reference here somehow!
        if not cmds.objExists(slave):
            # Remove MMessage and return early
            remove_node_callbacks(plug.node())
            return

        # Update UI!
        cmds.setAttr(slave, cmds.getAttr("pCube1.tx"))
        print "EVALED!"


def get_mobj_of_node(node):

    selectionList = om.MSelectionList()
    selectionList.add(node)

    return selectionList.getDependNode(0)


def add_attr_changed_callback(node, func):
    ''' Add polling callback for Shot check updates'''

    mobj = get_mobj_of_node(node)

    return om.MNodeMessage.addAttributeChangedCallback(mobj, func)  # void pointer to clientData?!


def get_node_callbacks(node):
    ''' Remove polling callback for Shot check updates'''

    if type(node) is not om.MObject:
        node = get_mobj_of_node(node)

    return om.MMessage.nodeCallbacks(node)


def remove_node_callbacks(node):
    ''' Remove callback for Shot check updates'''

    node_callbacks = get_node_callbacks(node)

    return om.MMessage.removeCallbacks(node_callbacks)


def testDef():

    remove_node_callbacks("pCube1")
    add_attr_changed_callback("pCube1", test_func)


testDef()


print get_node_callbacks("pCube1")
