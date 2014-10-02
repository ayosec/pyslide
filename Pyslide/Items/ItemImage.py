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

class ItemImage(Item):
    '''ItemImage

    This implements the Image item
    '''

    def __init__(self, parent, content, *k):
        self.src = None
        self.dx = None
        self.dy = None
        self.content = content

        Item.__init__(self, parent, content, *k)

    def parse_attrs(self, attrs):
        Item.parse_attrs(self, attrs)

        for key, val in attrs.items():
            key = key.lower()
            if key == 'src':
                self.src = val
            elif key == 'size':
                try:
                    x, y = [int(x) for x in val.split(',', 1)]
                except ValueError:
                    raise misc.PyslideError, 'Invalid size value: ' + str(val)
                else:
                    self.dx, self.dy = x, y

    def make_item(self):
        # load the image
        from Pyslide.Main.Images import imageloader
        if self.src is None:
            image = imageloader.loadfromstr64(self.content)
        else:
            image = imageloader.loadfile(self.src)
        image = image.convert()

        if None not in (self.dx, self.dy):
            if self.dx < 10 or self.dy <10:
                size = image.get_size()
                if self.dx < 10:
                    self.dx *= size[0]
                if self.dy < 10:
                    self.dy *= size[1]

            mx, my = CS.map_units(self.dx, self.dy)
            image = pygame.transform.scale(image, (mx, my))

        # get the rect, using the size of the image
        rect = image.get_rect().move(self.orig_x, self.orig_y)
        return image, rect

