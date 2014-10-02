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
from Pyslide.Items.ItemText import ItemText
CS = Presentation.CurrentSurface

LIST_SQUARE, LIST_RHOMBUS, LIST_CIRCLE, LIST_ENUM = 1, 2, 3, 4

class ItemList(ItemText):
    '''ItemList(text, attrs)

    This implements the List item
    '''

    def __init__ (self, parent, text, attrs, last_point, *k):
        item, group = parent

        self.listtype = LIST_RHOMBUS
        self.depth = 0
        self.itemposition = group.getposition(item)
        self.isthelastitem = group.isthelast(item)

        if last_point.list_firstx is None:
            last_point.list_firstx = last_point.x

        ItemText.__init__(self, parent, text, attrs, last_point, *k)

        if self.isthelastitem:
            last_point.x = last_point.list_firstx
            last_point.list_firstx = None

    def parse_attrs(self, attrs):

        ItemText.parse_attrs(self, attrs)

        for key, val in attrs.items():
            key = key.lower()
            if key == 'list-type':
                val = val.lower()
                if val == 'square':
                    self.listtype = LIST_SQUARE
                elif val == 'rhombus':
                    self.listtype = LIST_RHOMBUS
                elif val == 'circle':
                    self.listtype = LIST_CIRCLE
                elif val == 'enum':
                    self.listtype = LIST_ENUM
                else:
                    raise misc.PyslideError, 'Invalid value for list-type: ' + val
            elif key == 'list-depth':
                try:
                    self.depth = int(val)
                except ValueError:
                    raise misc.PyslideError, 'Invalid value for list-depth: ' + val

    def make_item(self):
        # font metrics
        font = self.getfont(self.font_file, self.font_size)
        fontheight = font.get_height()

        if self.listtype == LIST_ENUM:
            shape, shaperect = self.drawstring('%3d.' % (self.itemposition+1), 
                    int(self.font_size*0.8))

            shaperect.y = max(0, (fontheight - shaperect.height) / 2)
        else:
            x, y = fontheight/4, fontheight/4
            shape = pygame.Surface((x*2, y*2)).convert_alpha()
            shape.fill(0)
            shaperect = shape.get_rect()
            shaperect.top = y

            if self.listtype == LIST_SQUARE:
                shape.fill(self.color, (x/2, y/2, x, y))
            elif self.listtype == LIST_CIRCLE:
                pygame.draw.circle(shape, self.color, (x, y), y)
            elif self.listtype == LIST_RHOMBUS:
                pygame.draw.polygon(shape, self.color, 
                    [(x, 0), (0, y), (x, 2*y), (x*2, y)])
            else:
                raise misc.PyslideError, 'Incorrect listtype: ' + str(self.listtype)

        w = shaperect.width + 20

        # indent
        if self.depth < 7:
            self.depth = (self.depth + 1) * 50

        textimage, rect = ItemText.make_item(self,
            margin=w + CS.map_units(x = self.depth))

        # compose the image
        image = pygame.Surface((w + rect.width, rect.height)).convert_alpha()
        image.fill(0)
        image.blit(shape, (0, shaperect.y))
        image.blit(textimage, (w,0))
        rect = image.get_rect().move(rect.topleft)

        rect.x += CS.map_units(x = self.depth)

        return image, rect

    def __repr__(self):
        if len(self.text) > 15:
            c = self.text[:12] + '...'
        else:
            c = self.text
        return '<ItemList in %d groups. "%s">' % (len(self.groups()), c)


