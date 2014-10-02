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

class ImageNotFound(Exception):
    pass

class ImageLoader:

    def __init__(self):
        self.cachefiles = []
        self.embeddedimages = {}

    def saveimage(self, id, content, encodedbase64 = True):
        if encodedbase64:
            from base64 import decodestring
            content = decodestring(content)

        import pygame
        from cStringIO import StringIO

        source = StringIO(content)
        self.embeddedimages[id] = pygame.image.load(source)

    def loadfromstring(self, rawstring):
        from cStringIO import StringIO
        import pygame

        source = StringIO(rawstring)
        return pygame.image.load(source)

    def loadfromstr64(self, base64str):
        from base64 import decodestring
        return self.loadfromstring(decodestring(base64str))

    def loadfile(self, filename):
        import pygame

        try:
            # embedded images
            if filename.startswith('id://'):
                try:
                    return self.embeddedimages[filename[5:]]
                except KeyError:
                    raise ImageNotFound, 'Could not load image with id "%s"' % filename[5:]

            # is it cached?
            for n, i in self.cachefiles:
                if n == filename:
                    return i

            # load the image
            try:
                img = pygame.image.load(filename)
            except pygame.error, e:
                raise ImageNotFound, 'Error loading an image: %s' % str(e)

            # and cache it
            if len(self.cachefiles) > 0:
                del self.cachefiles[0]

            self.cachefiles.append( (filename, img) )

        except ImageNotFound, (error,):
            from Pyslide.Main import getmain
            main = getmain()

            if main.imagerrors:
                from Pyslide.misc import PyslideError
                raise PyslideError, error

            else:
                # empty image
                import logging
                logging.warning("Can't load %s. Using an empty surface." % filename)

                surface = pygame.Surface((1,1))
                surface.fill((0,0,0,0))

                return surface

        return img

imageloader = ImageLoader()

