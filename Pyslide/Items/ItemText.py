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
from Pyslide.Items import Item, ALIGN_RIGHT, ALIGN_CENTER, ALIGN_LEFT
CS = Presentation.CurrentSurface

class ItemText(Item):
    '''ItemText(text, attrs)

    This implements the Text item
    '''

    def __init__ (self, parent, text, *k):
        self.text = text
        self.shadow = (127,127,127)
        self.font_size = CS.map_units(y=60)
        self.font_file = None
        self.font = None
        self.interspace = 0

        Item.__init__(self, parent, text, *k)

    def parse_attrs(self, attrs):
        'See Item.parse_attrs for info.'

        Item.parse_attrs(self, attrs)

        for key, val in attrs.items():
            key = key.lower()
            if key == 'shadow':
                if val.lower() == 'none':
                    self.shadow = None
                else:
                    c = misc.parse_color(val)
                    if c is not None: self.shadow = c
            elif key == 'font-file':
                self.font_file = val
            elif key == 'font-size':
                try:
                    val = int(val)
                except ValueError:
                    raise misc.PyslideError, 'You have to put and integer in FONT-SIZE'

                if val < 10:
                    val *= 15;
                self.font_size = CS.map_units(y=val)
            elif key == 'interspace':
                try:
                    interspace = int(val)
                except ValueError:
                    raise misc.PyslideError, 'Invalid interspace value: ' + val

                self.interspace = CS.map_units(y = interspace)

    def make_item(self, margin=0):
        'See Item.make_image for info.'

        return self.drawstring(self.text, margin=margin)

    def getfont(self, fontfile, fontsize):
        try:
            return pygame.font.Font (fontfile, fontsize)
        except (IOError, RuntimeError), e:
            raise misc.PyslideError, 'loading font (%s): %s' %(fontfile, e)

    def drawstring(self, text, font_size = None, margin=0):

        if font_size is None:
            font_size = self.font_size

        colors = [self.color]
        if self.shadow is not None:
            colors.append(self.shadow)

        max_width = CS.width - (self.orig_x + margin)
        font = self.getfont(self.font_file, font_size)


        # split in lines

        texts = []
        current_line = None
        line = text.replace('\r', ' ')  # HTML style
        for word in line.split():
            if current_line is None:
                current_line = word
            else:
                if font.size(current_line + ' ' + word)[0] > max_width:
                    texts.append(current_line)
                    current_line = word
                else:
                    current_line += ' ' + word

        if current_line:
            texts.append(current_line)
                
        # size of the item
        width, height = 0, 0
        for line in texts:
            w, h = font.size(line)

            height += h + 2 + self.interspace
            if w > width:
                width = w

        if len(colors) != 1:
            width += 2
            height += len(texts) * (2 + self.interspace)

        # draw the items
        image = pygame.Surface((width, height)).convert_alpha()
        image.fill(0)
        y = 0
        for line in texts:
            t1 = font.render (line, 1, colors[0])

            if len(colors) == 1:
                t = t1

            else:
                t2 = font.render (line, 1, colors[1])

                rect = t1.get_rect()
                rect = rect.inflate(4,4).move(2,2)

                t = pygame.Surface(rect.size).convert_alpha()
                t.fill(0) # full alpha
                t.blit(t2, (2,2))
                t.blit(t1, (0,0))

            w, h = t.get_size()
            if self.align == ALIGN_LEFT:
                x = 0
            elif self.align == ALIGN_CENTER:
                x = (width - w) / 2
            elif self.align == ALIGN_RIGHT:
                x = width - w
            else:
                raise NotImplementedError

            image.blit(t, (x,y))
            y += h + self.interspace

        rect = pygame.Rect(self.orig_x, self.orig_y, width, height)
        return image, rect

    def __repr__(self):
        if len(self.text) > 15:
            c = self.text[:12] + '...'
        else:
            c = self.text
        return '<ItemText in %d groups. "%s">' % (len(self.groups()), c)

