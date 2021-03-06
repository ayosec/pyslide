# -*- coding: latin1 -*-
#
# Copyright (C) 2003, 2004 Ayose Cazorla Le�n
#
# Authors
#       Ayose Cazorla <ayose.cazorla@hispalinux.es>
#
# This file is part of Pyslide.
#
# Pyslide is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pyslide is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pyslide; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

class SurfaceInfo:
    def set_surface(self, surface):
        self.surface = surface
        self.width, self.height = surface.get_size()

    def map_units(self, x = None, y = None):
        cx, cy = self.width, self.height
        if None not in (x, y):
            x = cx * x / 1000
            y = cy * y / 750
            return x, y
        elif x is not None:
            return cx * x / 1000
        elif y is not None:
            return cy * y / 750

CurrentSurface = SurfaceInfo()

from Pyslide.Presentation.base import NewPresentation, Presentation
from Pyslide.Presentation.build import BuildPresentation
from Pyslide.Main.commands import signalhandler
