# Snap Nodes Circle

QGIS plugin (Advanced Digitizing toolbar): snaps together all nodes located
inside an adjustable circle centred on a snapping point.

## Usage

1. Enable snapping (*Project > Snapping Options*).
2. Toggle editing on the layers whose nodes should move.
3. Click the tool icon (Advanced Digitizing toolbar, or *Vector > Snap Nodes Circle* menu).
4. Click on a snapped point: it becomes the centre of the circle.
5. Move the mouse to stretch the radius (shown in the status bar, in map units).
6. Click again: all nodes of the editable layers inside the circle are moved onto the centre.
7. `Esc` or right-click cancels.

## Behaviour

- The centre must be on a snapping point; it may belong to a non-editable layer.
- Nodes of **all** editable layers are moved.
- Reprojection between layer CRS and map CRS is handled.
- Each modified layer can be undone in a single step (`Ctrl+Z`).

## Installation

*Plugins > Install from ZIP*, or copy the `snap_nodes_circle` folder into the
`python/plugins` folder of the active QGIS profile.

## License

GNU GPL v2 or later — see [LICENSE](LICENSE).
