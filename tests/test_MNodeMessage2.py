import maya.api.OpenMaya as om
import maya.cmds as cmds


class AttrChangedCallbackHandler(object):

    def __init__(self, node, func):
        self.func = func
        self.id = None

        # Transform given node into MObject
        self.node = node
        self.mobj = self._get_mobj_of_node(node)

    def install(self):
        if self.id:
            print "callback is currently installed"
            return False
        self.id = om.MNodeMessage.addAttributeChangedCallback(self.mobj, self.func)
        # self.id = om.MEventMessage.addEventCallback(self.callback, self.function)
        return True

    def uninstall(self):
        if self.id:
            om.MEventMessage.removeCallback(self.id)
            self.id = None
            return True
        else:
            print "callback not currently installed"
            return False

    @staticmethod
    def _get_mobj_of_node(node):
        selectionList = om.MSelectionList()
        selectionList.add(node)

        return selectionList.getDependNode(0)

    def __del__(self):
        self.uninstall()


def test_fn(msg, plug, other_plug, client_data):
    if msg == 2056:
        print "callback fired 2", msg, plug, other_plug, client_data



cb = AttrChangedCallbackHandler('pCube1', test_fn)
cb.install()

# callback is active
cb.uninstall()
# callback not active
cb.install()
# callback on again
del(cb)  # or cb = None
# callback gone again

