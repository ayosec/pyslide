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


class PyslideError(Exception):
    pass

def RenderGradient(surf, topcolor, bottomcolor):
    '''Creates a new 3d vertical gradient array.

    This code was copied from the vgrade example'''

    import pygame
    from Numeric import array, repeat, resize, arange, \
        Float, NewAxis, Int, UnsignedInt8

    topcolor = array(topcolor, copy=0)
    bottomcolor = array(bottomcolor, copy=0)
    diff = bottomcolor - topcolor
    width, height = surf.get_size()
    # create array from 0.0 to 1.0 triplets
    column = arange(height, typecode=Float)/height
    column = repeat(column[:, NewAxis], [3], 1)
    # create a single column of gradient
    column = topcolor + (diff * column).astype(Int)
    # make the column a 3d image column by adding X
    column = column.astype(UnsignedInt8)[NewAxis,:,:]
    #3d array into 2d array
    column = pygame.surfarray.map_array(surf, column)
    # stretch the column into a full image
    return resize(column, (width, height))
 


def parse_color(c):

    from pygame.colordict import THECOLORS

    c = c.strip().lower()
    if THECOLORS.has_key(c):
        return THECOLORS[c][:3]

    try:
        r, g, b = map(lambda s: int(s), c.split(',', 2))
    except ValueError:
        import sys
        print >> sys.stderr, 'Invalid color string:', c
        return None

    return r, g, b


def parse_point(point):
    try:
        point = [int(x) for x in point.split(',')]
        if len(point) != 2:
            raise ValueError
    except ValueError:
        raise PyslideError, 'Incorrect point value: ' + val
    return tuple(point)

def parse_relativepoint(point):
    try:
        x, y = point.split(',')
    except ValueError:
        raise PyslideError, 'Incorrect point value: ' + val

    return [(len(a) and a[0]) in ('-', '+') for a in (x, y)]

