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

class Html:
    def __init__(self, content, main):
        self.content = content
        self.main = main

    def export(self, directory):
        import os.path
        import os
        import misc

        # Check destination directory
        if os.path.exists(directory):
            if not os.path.isdir(directory):
                raise misc.PyslideError, 'Destination is not a directory'
        else:
            try:
                os.mkdir(directory)
            except OSError, e:
                raise misc.PyslideError, str(e)


        # Create the presentation in order to grab images from it
        # XXX Can this be made better?? (without create the 
        #     presentation)
        import Presentation
        pres = Presentation.BuildPresentation(self.content, self.main)

        # Render pages into BMP files.
        # This is a hack... maybe it will be better if 
        # it were made directly by the Presentation object.

        from Pyslide.Presentation.Pages import renderbackground

        import pygame
        pygame.display.iconify()

        page_num = 1
        keep_always_items = []
        surface = pygame.Surface(pres.win.get_size())

        for xpage in pres.pages:
            page = xpage.createpage()
            # render background
            bg = page.getbackground()
            if bg is None:
                bg = pres.defaultbackground
            renderbackground(surface, bg)

            for image, rect in keep_always_items:
                surface.blit(image, rect.topleft)

            for g in page.groups:
                for item in g:
                    image, rect = item.make_item()
                    surface.blit(image, rect.topleft)

                    # save it if it is a keep-always item
                    if item.keep_always:
                        keep_always_items.append((image, rect))

            # save the image
            import PIL.Image
            print 'Writing slide #%d' % page_num
            img = PIL.Image.fromstring('RGB', surface.get_size(),
                pygame.image.tostring(surface, 'RGB'))
            img.save(os.path.join(directory, 'img-%d.png' %  page_num))

            f = open(os.path.join(directory, 'slide%03d.html' % page_num), 'w')
            f.write('<html>\n<head>\n<title>%s. #%d</title><body>\n' % 
                    (pres.caption, page_num))
            f.write('<p align="center">')
            if page_num > 1:
                f.write('<a href="slide%03d.html">Prev</a>\n' % (page_num-1))
            f.write('Current: %d\n' % page_num)
            if page_num < len(pres.pages):
                f.write('<a href="slide%03d.html">Next</a>\n' % (page_num+1))
            f.write('<br/><br/>\n<img src="img-%(n)d.png" alt="slide #%(n)d"/></p>'
                    '</body></html>\n' %  {'n': page_num})

            page_num += 1

        
