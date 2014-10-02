# -*- coding: latin1 -*-
#
# Copyright (C) 2003, 2004 Ayose Cazorla León
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
                                                                                                
import pygame
import time
from Pyslide import Presentation, misc
from Pyslide.Items import Item
CS = Presentation.CurrentSurface

class ItemShape(Item):
    def __init__(self, *k):
        self.s_shape = None
        self.s_center = None
        self.s_points = None
        self.s_radius = None
        self.s_start = None
        self.s_width = None
        self.s_end = None

        Item.__init__(self, *k)

    def parse_attrs(self, attrs):
        Item.parse_attrs(self, attrs)

        for key, val in attrs.items():
            key = key.lower()

            if key == 'shape':
                val = val.lower()
                if val in ('line', 'circle', 'arc', 'rect', 'polygon'):
                    self.s_shape = val
                else:
                    raise misc.PyslideError, 'UNKNOWN SHAPE: ' + str(val)

            elif key in ('start', 'end', 'points'):
                setattr(self, 's_' + key, val)

            elif key == 'center':
                try:
                    x, y = [int(x) for x in val.split(',', 1)]
                except ValueError:
                    raise misc.PyslideError, 'Invalid center value: ' + str(val)
                else:
                    self.s_center = CS.map_units(x, y)

            elif key == 'radius':
                try:
                    self.s_radius = CS.map_units(int(val))
                except ValueError:
                    raise misc.PyslideError, \
                        'Ivalid radius value. It has to be an integer: ' + str(val)

            elif key == 'width':
                try:
                    w = int(val)
                except ValueError:
                    raise misc.PyslideError, 'Invalid width: ' + str(val)
                else:
                    if w != 0:
                        self.s_width = max(1, CS.map_units(w))


        # interpret some valus depending on the shape
        if self.s_shape == 'arc':
            try:
                self.s_start = float(self.s_start)
                self.s_end = float(self.s_end)
            except ValueError, e:
                raise misc.PyslideError, \
                    'Invalid value for start/end angle: ' + str(e)

        elif self.s_shape in ('line', 'rect'):
            try:
                self.s_start = CS.map_units(*[int(x) for x in self.s_start.split(',', 1)])
                self.s_end = CS.map_units(*[int(x) for x in self.s_end.split(',', 1)])
            except ValueError, e:
                raise misc.PyslideError, 'Invalid point value. ' + str(e)
        elif self.s_shape == 'polygon':
            p = []
            for point in self.s_points.split(';'):
                try:
                    x, y = [int(x) for x in point.split(',', 1)]
                except ValueError:
                    raise misc.PyslideError, 'Invalid point value: ' + str(point)
                else:
                    p.append(CS.map_units(x, y))

            self.s_points = p


        # default width
        if self.s_width is None:
            if self.s_shape == 'line':
                self.s_width = 1
            else:
                self.s_width = 0

    def make_item(self):

        if self.color == (0,0,0):
            colorkey = (255,255,255)
        else:
            colorkey = (0,0,0)

        surface = pygame.Surface(pygame.display.get_surface().get_size())
        surface.set_colorkey(colorkey)
        surface.fill(colorkey)
        rect = None

        if self.s_shape == 'line':
            rect = pygame.draw.line(surface, self.color,
                self.s_start, self.s_end, self.s_width)

        elif self.s_shape == 'circle':
            rect = pygame.draw.circle(surface, self.color,
                    self.s_center, self.s_radius, self.s_width)
        elif self.s_shape == 'arc':
            pass
        elif self.s_shape == 'rect':
            left, top = self.s_start
            right, bottom = self.s_end

            if left > right:
                left, right = right, left
            if top > bottom:
                top, bottom = bottom, top

            rect = pygame.Rect(left, top, right - left, bottom - top)

            if self.s_width == 0:
                surface.fill(self.color, rect)
            else:
                rect = pygame.draw.rect(surface, self.color, rect, 
                        self.s_width)
                
        elif self.s_shape == 'polygon':
            rect = pygame.draw.polygon(surface, self.color,
                    self.s_points, self.s_width)

        else:
            # hide the item
            image = pygame.Surface((0,0))
            image.fill(0)
            rect = pygame.Rect(0,0,1,1)

        if rect is None:
            rect = pygame.Rect(0,0,1,1)

        # copy the image. I did this in order to save memory
        image = pygame.Surface(rect.size)
        image.set_colorkey(colorkey)
        image.blit(surface.subsurface(rect), (0,0))

        self.orig_x, self.orig_y = rect.topleft

        return image, rect

