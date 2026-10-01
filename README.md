# Snap Nodes Circle

Plugin QGIS (barre « Numérisation avancée ») : accroche ensemble tous les nœuds
situés dans un cercle de rayon ajustable, centré sur un point d'accrochage.

## Utilisation

1. Activez l'accrochage (*Projet > Options d'accrochage*).
2. Mettez en édition les couches dont les nœuds doivent bouger.
3. Cliquez sur l'icône de l'outil (barre « Numérisation avancée » ou menu *Vecteur > Snap Nodes Circle*).
4. Cliquez sur un point accroché : il devient le centre du cercle.
5. Déplacez la souris pour étirer le rayon (affiché dans la barre d'état, en unités de la carte).
6. Cliquez à nouveau : tous les nœuds des couches en édition situés dans le cercle sont ramenés sur le centre.
7. `Échap` ou clic droit : annule.

## Comportement

- Le centre doit être sur un point d'accrochage ; il peut appartenir à une couche non éditable.
- Les nœuds de **toutes** les couches en édition sont déplacés.
- Les reprojections entre le CRS des couches et celui de la carte sont gérées.
- Chaque couche modifiée est annulable en une seule action (`Ctrl+Z`).

## Installation

*Extensions > Installer depuis un ZIP*, ou copier le dossier `snap_nodes_circle`
dans le dossier `python/plugins` du profil QGIS actif.

## Licence

GNU GPL v2 ou ultérieure — voir [LICENSE](LICENSE).
