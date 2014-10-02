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
from Pyslide.misc import parse_color, PyslideError
from Pyslide.Presentation.base import NewPresentation
from pygame.locals import *

def BuildPresentation(content, main):
    '''BuildPresentation (content, **args) -> presentation

    Parses the content data and creates a new presentation.
    content is the result of File.ReadFile.
    '''

    from Pyslide.Presentation import Pages
    from Pyslide import Items

    fullscreen = main.fullscreen
    size = main.size
    start_page = main.start_page

    p_attrs = content.get_attrs()

    flags = HWACCEL
    if fullscreen:
        flags |= FULLSCREEN

    # Size
    if size is None:
        if p_attrs.has_key('size'):
            size = p_attrs['size']
        else:
            # get the ¿best? size
            pygame.display.init()
            r = pygame.display.list_modes()
            if r == -1:
                size = '800x600'
            else:
                # the biggest size
                size = '%dx%d' % r[0]

    try:
        w, h = [int(x) for x in size.split('x')]
    except ValueError:
        raise PyslideError, 'Invalid size ("%s")' % size

    # create the presentation
    caption = p_attrs.get('caption', 'Presentation')
    presentation = NewPresentation (caption, w, h, flags)

    if start_page is not None:
        presentation.setstartpage(start_page)

    # default background
    defbg = Pages.createbackground(p_attrs)
    if defbg is None: defbg = (0,0,0)
    presentation.setdefaultbg(defbg)

    # Create the pages
    for pagexml in content.pages():
        presentation.addpage(Pages.Page(pagexml))

    return presentation

