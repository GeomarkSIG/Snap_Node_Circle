import math

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from qgis.core import (
    Qgis,
    QgsCoordinateTransform,
    QgsFeatureRequest,
    QgsGeometry,
    QgsPointXY,
    QgsProject,
    QgsRectangle,
    QgsVectorLayer,
)
from qgis.gui import QgsMapTool, QgsRubberBand, QgsSnapIndicator

try:
    _POLYGON = Qgis.GeometryType.Polygon
except AttributeError:  # QGIS < 3.30
    from qgis.core import QgsWkbTypes
    _POLYGON = QgsWkbTypes.PolygonGeometry

try:
    _MSG_INFO, _MSG_WARN = Qgis.MessageLevel.Info, Qgis.MessageLevel.Warning
except AttributeError:
    _MSG_INFO, _MSG_WARN = Qgis.Info, Qgis.Warning

CIRCLE_SEGMENTS = 72


class SnapNodesCircleTool(QgsMapTool):
    """Clic 1 sur un point accroché = centre ; la souris étire le rayon ;
    clic 2 = tous les noeuds des couches en édition dans le cercle sont
    ramenés sur le centre."""

    def __init__(self, iface):
        super().__init__(iface.mapCanvas())
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.center = None
        self.band = None
        self.snap_indicator = QgsSnapIndicator(self.canvas)
        self.setCursor(Qt.CrossCursor)

    # ------------------------------------------------------------------ cycle
    def activate(self):
        super().activate()
        self.iface.messageBar().pushMessage(
            "Accrocher les noeuds",
            "Cliquez sur un point accroché (centre), étirez le rayon, cliquez pour valider. "
            "Echap / clic droit : annuler.",
            level=_MSG_INFO, duration=6)

    def deactivate(self):
        self._reset()
        self.snap_indicator.setMatch(self._empty_match())
        super().deactivate()

    def _reset(self):
        self.center = None
        if self.band is not None:
            self.canvas.scene().removeItem(self.band)
            self.band = None
        self.iface.statusBarIface().clearMessage()

    @staticmethod
    def _empty_match():
        from qgis.core import QgsPointLocator
        return QgsPointLocator.Match()

    # ----------------------------------------------------------------- events
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self._reset()
            e.accept()

    def canvasMoveEvent(self, e):
        match = self.canvas.snappingUtils().snapToMap(e.pos())
        self.snap_indicator.setMatch(match)
        if self.center is None:
            return
        pt = self.toMapCoordinates(e.pos())
        self._update_band(self._distance(self.center, pt))

    def canvasReleaseEvent(self, e):
        if e.button() == Qt.RightButton:
            self._reset()
            return
        if e.button() != Qt.LeftButton:
            return

        if self.center is None:
            match = self.canvas.snappingUtils().snapToMap(e.pos())
            if not match.isValid():
                self.iface.messageBar().pushMessage(
                    "Accrocher les noeuds",
                    "Aucun point d'accrochage sous le curseur : activez l'accrochage "
                    "(Projet > Options d'accrochage).",
                    level=_MSG_WARN, duration=4)
                return
            self.center = QgsPointXY(match.point())
            self._update_band(0)
            return

        radius = self._distance(self.center, self.toMapCoordinates(e.pos()))
        if radius <= 0:
            return
        center = self.center
        self._reset()
        self._snap_nodes(center, radius)

    # --------------------------------------------------------------- display
    @staticmethod
    def _distance(a, b):
        return math.hypot(a.x() - b.x(), a.y() - b.y())

    def _update_band(self, radius):
        if self.band is None:
            self.band = QgsRubberBand(self.canvas, _POLYGON)
            self.band.setColor(QColor(230, 57, 70, 200))
            self.band.setFillColor(QColor(61, 139, 253, 50))
            self.band.setWidth(2)
        if radius > 0:
            geom = QgsGeometry.fromPointXY(self.center).buffer(radius, CIRCLE_SEGMENTS)
            self.band.setToGeometry(geom, None)
        else:
            self.band.reset(_POLYGON)
        self.iface.statusBarIface().showMessage("Rayon : %.4f (unités de la carte)" % radius)

    # ------------------------------------------------------------------ core
    def _snap_nodes(self, center, radius):
        map_crs = self.canvas.mapSettings().destinationCrs()
        project = QgsProject.instance()
        total_nodes = 0
        total_features = 0
        layers_done = []

        for layer in project.mapLayers().values():
            if not isinstance(layer, QgsVectorLayer) or not layer.isEditable():
                continue
            if not layer.isSpatial():
                continue
            nodes, feats = self._snap_layer(layer, map_crs, center, radius)
            if nodes:
                total_nodes += nodes
                total_features += feats
                layers_done.append(layer.name())

        self.canvas.refresh()
        if total_nodes:
            self.iface.messageBar().pushMessage(
                "Accrocher les noeuds",
                "%d noeud(s) accroché(s) sur %d entité(s) (%s)."
                % (total_nodes, total_features, ", ".join(layers_done)),
                level=_MSG_INFO, duration=5)
        else:
            self.iface.messageBar().pushMessage(
                "Accrocher les noeuds",
                "Aucun noeud à déplacer (couches en édition requises).",
                level=_MSG_WARN, duration=4)

    def _snap_layer(self, layer, map_crs, center, radius):
        ctx = QgsProject.instance().transformContext()
        to_map = QgsCoordinateTransform(layer.crs(), map_crs, ctx)
        to_layer = QgsCoordinateTransform(map_crs, layer.crs(), ctx)

        try:
            center_l = to_layer.transform(center)
            bbox_map = QgsRectangle(center.x() - radius, center.y() - radius,
                                    center.x() + radius, center.y() + radius)
            bbox_l = to_layer.transformBoundingBox(bbox_map)
        except Exception:
            return 0, 0

        r2 = radius * radius
        nodes_moved = 0
        feats_moved = 0
        started = False

        request = QgsFeatureRequest().setFilterRect(bbox_l)
        for feat in layer.getFeatures(request):
            geom = feat.geometry()
            if geom is None or geom.isNull():
                continue
            new_geom = QgsGeometry(geom)
            idx_to_move = []
            for i, v in enumerate(geom.vertices()):
                try:
                    vm = to_map.transform(QgsPointXY(v.x(), v.y()))
                except Exception:
                    continue
                dx, dy = vm.x() - center.x(), vm.y() - center.y()
                if dx * dx + dy * dy <= r2:
                    if v.x() != center_l.x() or v.y() != center_l.y():
                        idx_to_move.append(i)
            if not idx_to_move:
                continue
            for i in idx_to_move:
                new_geom.moveVertex(center_l.x(), center_l.y(), i)
            if not started:
                layer.beginEditCommand("Accrocher les noeuds dans un cercle")
                started = True
            if layer.changeGeometry(feat.id(), new_geom):
                nodes_moved += len(idx_to_move)
                feats_moved += 1

        if started:
            if feats_moved:
                layer.endEditCommand()
            else:
                layer.destroyEditCommand()
        return nodes_moved, feats_moved
