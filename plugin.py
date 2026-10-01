import os

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .map_tool import SnapNodesCircleTool


class SnapNodesCirclePlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.tool = None

    def initGui(self):
        icon = QIcon(os.path.join(os.path.dirname(__file__), "icon.svg"))
        self.action = QAction(icon, "Snap nodes within a circle",
                              self.iface.mainWindow())
        self.action.setCheckable(True)
        self.action.setToolTip("Snap together all nodes inside a circle "
                               "centred on a snapping point")
        self.action.triggered.connect(self.activate_tool)

        self.tool = SnapNodesCircleTool(self.iface)
        self.tool.setAction(self.action)

        self.iface.addPluginToVectorMenu("&Snap Nodes Circle", self.action)
        self.iface.advancedDigitizeToolBar().addAction(self.action)

    def activate_tool(self):
        self.iface.mapCanvas().setMapTool(self.tool)

    def unload(self):
        if self.iface.mapCanvas().mapTool() is self.tool:
            self.iface.mapCanvas().unsetMapTool(self.tool)
        self.iface.removePluginVectorMenu("&Snap Nodes Circle", self.action)
        self.iface.advancedDigitizeToolBar().removeAction(self.action)
        self.tool = None
        self.action = None
