"""

"""
import os

from Qt import QtGui
from Qt import QtWidgets


proj_path = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir))
media_path = os.path.join(proj_path, "media")


def get_image_path(name):
    path = os.path.join(media_path, name)

    return path


def get_icon_path(name):
    name += "_icon.png"
    path = os.path.join(media_path, name)

    return path


class MIcon(QtGui.QIcon):
    def __init__(self, name, *args, **kwargs):
        icon_path = get_icon_path(name)
        super(MIcon, self).__init__(icon_path, *args, **kwargs)
