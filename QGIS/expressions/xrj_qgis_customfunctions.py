# Copyright (C) 2025  Xu Ruijun
# SPDX-License-Identifier: MIT
from qgis.core import *
from qgis.gui import *
import math

@qgsfunction(args='auto', group='Custom', referenced_columns=[])
def my_diff(r, deg, feature, parent):
    geom = feature.geometry()
    pt = geom.asPoint()
    rad = deg/180*math.pi
    return QgsGeometry.fromPointXY(QgsPointXY(pt.x()+math.sin(rad)*r/(math.cos(pt.y()/180*math.pi)), pt.y()+math.cos(rad)*r))
