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
from Pyslide.Presentation import CurrentSurface
from pygame.locals import *

def NewPresentation(caption='Presentation', 
        width=640, height=480, flags=HWACCEL, iconify=False):
    if not pygame.font.get_init():
        pygame.font.init()
    if not pygame.display.get_init():
        pygame.display.init()

    win = pygame.display.set_mode((width, height), flags)
    pygame.mouse.set_visible(False)
    pygame.display.set_caption(caption)

    if iconify: pygame.display.iconify()

    return Presentation(win, caption)

class Presentation:
    def __init__ (self, win, caption):
        self.win = win
        self.pages = []
        self.caption = caption
        self.num_page = 0
        self.page = None
        self.displayneedflip = False
        self.start_page = None
        self.current_page = pygame.sprite.RenderUpdates()
        self.special_sprites = pygame.sprite.RenderUpdates()

        CurrentSurface.set_surface(win)

    def setstartpage(self, pagenum):
        self.start_page = pagenum

    def add_sprites(self, sprites):
        # get IDs for the current sprites
        ids = [x.getid() for x in self.current_page.sprites()]
        for s in sprites:
            if s.getid() not in ids:
                self.current_page.add(s)
                s.start(self.num_page)

    def remove_sprites(self, sprites, force_stop):
        if force_stop:
            for s in sprites:
                if s.keep_always:
                    if s.getpagenumber() > self.num_page:
                        s.kill()
                else:
                    s.force_stop()
        else:
            for s in sprites:
                s.stop()

    def addpage (self, page):
        self.pages.append (page)

    def next_page (self):
        if self.num_page < len(self.pages)-1:
            self.set_page(self.num_page + 1)
            self.update_itemstate()

    def prev_page (self):
        if self.num_page > 0:
            self.set_page(self.num_page - 1, show_effects = False)

            while True:
                sprites = self.page.nextstage()
                if sprites is None: break
                self.add_sprites(sprites)

            self.update_itemstate(use_setend = True)

    def set_page(self, n, show_effects=True):
        self.num_page = n

        # empty the page
        self.remove_sprites(self.current_page.sprites(), not show_effects)
        self.current_page.update()

        # add the new sprites
        self.page = page = self.pages[self.num_page].createpage()
        for group in page.currentgroups():
            self.add_sprites(group)

        # show the page
        from Pyslide.Presentation.Pages import renderbackground
        renderbackground(self.win, self.getcurrentbg())
        self.displayneedflip = True

        # update (if any) the bar
        self.update_pagenum()

        import time
        self.page_start_time = time.time()

    def next_stage(self):
        page = self.page
        sprites = page.nextstage()
        if sprites is None:
            self.next_page()
        else:
            self.add_sprites(sprites)
        self.update_itemstate()

    def prev_stage(self):
        page = self.page
        sprites = page.prevstage()
        if sprites is None:
            self.prev_page()
        else:
            self.remove_sprites(sprites, force_stop = True)
            self.update_itemstate()

    def update_itemstate(self, use_setend = False):
        cg = self.page.getcurrentgroup()
        for item in self.current_page.sprites():
            if item.effectstate == 'back' and item in cg:
                item.seteffects('front')
            elif item not in cg:
                item.seteffects('back', use_setend)

    def setdefaultbg(self, bg):
        self.defaultbackground = bg

    def update_pagenum(self):
        from Pyslide import Items
        # check if page-number item is already in the page
        for sprite in self.special_sprites.sprites():
            if isinstance(sprite, Items.ItemPageNumber):
                sprite.kill()

                if sprite.keep_always:
                    # restore it
                    sprite = Items.ItemPageNumber(self.num_page+1, len(self.pages))
                    self.special_sprites.add(sprite)
                    sprite.start()
                    sprite.set_keepalways()
                    return True

        return False

    def show_pagenum(self):
        from Pyslide import Items

        # check if page-number item is already in the page
        for sprite in self.special_sprites.sprites():
            if isinstance(sprite, Items.ItemPageNumber):
                # it is already a keep-always item
                if sprite.keep_always:
                    sprite.set_keepalways(False)
                else:
                    sprite.set_keepalways()
                    self.update_pagenum()

                return

        # if not, create it
        sprite = Items.ItemPageNumber(self.num_page+1, len(self.pages))
        self.special_sprites.add(sprite)
        sprite.start()

    def show_timer(self):
        from Pyslide import Items

        # check if timer item is already in the page
        for sprite in self.special_sprites.sprites():
            if isinstance(sprite, Items.ItemTimer):
                # it is already visible... remove it
                sprite.togglekeepalways()
                return

        # if not, create it
        sprite = Items.ItemTimer()
        self.special_sprites.add(sprite)
        sprite.start()

    def run (self):

        # Go to the start-page
        if self.start_page < 0:
            self.start_page = max(0, len(self.pages) + self.start_page)
        elif self.start_page >= len(self.pages):
            self.start_page = len(self.pages) - 1

        while self.num_page < self.start_page:
            # start only keep-always items
            page = self.pages[self.num_page]
            self.add_sprites(page.getkeepalwaysitems())
            self.num_page += 1

        self.set_page(self.num_page)

        #clock = pygame.time.Clock()
        import time
        while True:
            #clock.tick(20)
            time.sleep(0.05)
            page = self.page

            bg = self.getcurrentbg()
            if isinstance(bg, tuple):
                bgcolor = bg
                bg = lambda s, r: s.fill(bgcolor, r)

            self.special_sprites.clear(self.win, bg)
            self.current_page.clear(self.win, bg)

            self.current_page.update()
            self.special_sprites.update()
 
            for event in pygame.event.get():
                if event.type == QUIT:
                    return

                elif event.type == MOUSEBUTTONDOWN:
                    if event.button in (1, 5):
                        self.next_stage()
                    elif event.button == 2:
                        self.show_pagenum()
                    elif event.button in (3, 4):
                        self.prev_stage()

                elif event.type == KEYDOWN:
                    if event.key == K_f:
                        pygame.display.toggle_fullscreen()
                    elif event.key == K_LEFT:
                        self.prev_stage()
                    elif event.key in (K_RIGHT, K_SPACE):
                        self.next_stage()
                    elif event.key == K_PAGEUP:
                        self.prev_page()
                    elif event.key == K_PAGEDOWN:
                        self.next_page()
                    elif event.key == K_q:
                        return
                    elif event.key == K_s:
                        self.show_pagenum()
                    elif event.key == K_t:
                        self.show_timer()
                    elif event.key == K_d:
                        s = self.current_page.sprites()
                        print '%d items:' % len(s)
                        import pprint; pprint.pprint(s)
                        print 'keep-always: %d\n' % len([0 for x in s if x.keep_always])

            if page.ttl is not None:
                if time.time() - self.page_start_time >= page.ttl:
                    self.page.setstage(-1)
                    self.next_page()

            dirty = self.current_page.draw(self.win) + \
                    self.special_sprites.draw(self.win)
            pygame.display.update(dirty)

            if self.displayneedflip:
                pygame.display.flip()
                self.displayneedflip = False

            # if the page is empty, go to the next stage
            if len(self.current_page) == 0:
                self.next_stage()

    def getcurrentbg(self):
        bg = self.page.getbackground()
        if bg is None:
            bg = self.defaultbackground

        return bg

