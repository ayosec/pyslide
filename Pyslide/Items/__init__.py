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
from Pyslide import misc, Presentation
CS = Presentation.CurrentSurface

ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT = -1, 0, 1

class ReplaceThisItem(Exception):
    'This exception is used when a item want to be replaced by another'

class LastPoint:
    def __init__(self):
        self.reset()
        self.list_firstx = None

    def reset(self):
        self.x, self.y = CS.map_units(20, 20)

    def set(self, x = None, y = None):
        if x is not None: self.x = x
        if y is not None: self.y = y

    def get(self):
        return self.x, self.y

    def __repr__(self):
        return '<LastPoint (%d, %d)>' % (self.x, self.y)

class Item(pygame.sprite.Sprite):
    '''
    Item(attrs)

    This is the base class for all the items that you will put in
    the slide surface.
    '''

    def __init__ (self, parent, content, attrs, last_point):
        pygame.sprite.Sprite.__init__(self)

        del content # not used

        # get the main object
        if parent is not None:
            item, group = parent
            page = group.parent()
            self.maincontent = page.parent()

        # default values
        self.current_effects = pygame.sprite.Group()
        self.nexteffectstate = 'front'
        self.closing = None
        self.ttl = None
        self.wait_time = None
        self.waiting = False
        self.raw_attrs = attrs
        self.keep_always = False
        self.effectstate = None
        self.align = ALIGN_LEFT
        self.color = (255,255,255)

        self.effects = []

        self.parent = parent
        self.onpagenumber = None

        self.orig_x, self.orig_y = last_point.get()
        self.parse_attrs(attrs)
        self.check_state()

        # move the last_point
        last_point.set(self.orig_x, self.orig_y + self.height)

    def getid(self):
        return id(self.parent)

    def getparent(self):
        return self.parent

    def getpagenumber(self):
        return self.onpagenumber

    def parse_attrs(self, attrs):
        '''parse_attrs(attrs) -> None

        Loads the values of the attrs dictionary, and put the
        values as object attributes. This will convert everything
        (effects, integer values, etc). Unknown attributes will be
        ignored.
        '''

        from Pyslide import Effects

        for r_key, val in attrs.items():
            key = r_key.lower()
            key_used = True

            if key == 'xy':
                try:
                    x, y = [int(x) for x in val.split(',', 1)]
                except ValueError:
                    raise misc.PyslideError, 'Invalid XY value: ' + str(val)
                else:
                    self.orig_x, self.orig_y = CS.map_units(x, y)

            elif key == 'y':
                if len(val) and val[0] in ('+', '-'):
                    relative = val[0] == '+' and 1 or -1
                    val = val[1:]
                else:
                    relative = 0

                try:
                    y = CS.map_units(y = int(val))
                except ValueError:
                    raise misc.PyslideError, 'Invalid y value: ' + str(val)

                if relative == -1:
                    self.orig_y -= y
                elif relative == 1:
                    self.orig_y += y
                else:
                    self.orig_y = y

            elif key == 'x':
                if len(val) and val[0] in ('+', '-'):
                    relative = val[0] == '+' and 1 or -1
                    val = val[1:]
                else:
                    relative = 0

                try:
                    x = CS.map_units(x = int(val))
                except ValueError:
                    raise misc.PyslideError, 'Invalid x value: ' + str(val)

                if relative == -1:
                    self.orig_x -= x
                elif relative == 1:
                    self.orig_x += x
                else:
                    self.orig_x = x

            elif key == 'color':
                c = misc.parse_color(val)
                if c is not None:
                    self.color = c
            elif key == 'ttl':
                if val == 'none':
                    self.ttl = None
                else:
                    try:
                        self.ttl = int(val) / 10.
                    except ValueError:
                        raise misc.PyslideError, 'You have to put an integer in TTL'
            elif key == 'wait':
                if val == 'none':
                    self.wait_time = None
                else:
                    try:
                        self.wait_time = int(val) / 10.
                    except ValueError:
                        raise misc.PyslideError, 'You have to put an integer in WAIT'

            elif key.startswith('effect-'):
                # get its attributes
                try:
                    ef_attrs = self.maincontent.cssclass[val]
                except KeyError:
                    raise misc.PyslideError, 'Unknown class: ' + val

                # get the effect
                name = key[key.find('-')+1:]
                try:
                    ef = Effects.load(self, name, ef_attrs)
                except Effects.EffectError, e:
                    raise misc.PyslideError, 'Error in effect (%s): %s' % (name, e)

                self.effects.append(ef)

            elif key == 'keep-always':
                self.keep_always = val.lower() == 'yes'

            elif key == 'align':
                val = val.lower()
                if val == 'left':
                    self.align = ALIGN_LEFT
                elif val == 'center':
                    self.align = ALIGN_CENTER
                elif val == 'right':
                    self.align = ALIGN_RIGHT
                else:
                    raise misc.PyslideError, 'Invalid align value: ' + val
            else:
                key_used = False

            if key_used:
                del attrs[r_key]


    def check_state(self):
        '''check_state()

        This function is called after parse_attrs() to initialize
        the state of the item
        '''
        if self.align != ALIGN_LEFT:
            self.orig_x = 0

        image, rect = self.make_item()
        self.width, self.height = rect.size

        # align
        self.orig_x = self.align_x(rect.width)

        # update effectos
        for e in self.effects:
            e.parse_attrs()

    def make_item(self):
        '''make_item() -> (surface, rect)

        This function is called after a start() event. The child
        class will put in this method every initialization that 
        they need for the item. For instance, an image item will
        load its image in this method.

        It returns a tuple (surface, rect).
        '''
        return None, None

    def free_item(self):
        '''free_item(self) -> None

        The data that you set in make_item() have to be freed
        in this method.
        '''
        del self.image, self.rect

    def start(self, onpagenumber = None):
        '''start(onpagenumber = None) -> None

        start() is called every time that the item is put in a
        surface. It sets the required values for the item.
        '''

        self.onpagenumber = onpagenumber
        self.start_time = time.time()
        self.closing = False

        if self.wait_time is None:
            self.waiting = False
            self.image, self.rect = self.make_item()
            self.seteffects('open')
        else:
            self.waiting = True
            self.hide()

    def seteffects(self, state, setend = False):
        '''seteffects(efstate, setend = False)

        Set the effect states to efstate
        '''

        if self.waiting:
            self.nexteffectstate = state

        self.effectstate = state
        self.start_time = time.time()

        if self.image is None:
            self.image, self.rect = self.make_item()

        for s in self.effects:
            self.current_effects.add(s)

            # special case for 'open'
            if state == 'open' and not s.usedstate('open'):
                state = 'front'

            if setend:
                s.setend(state)
            else:
                s.setstate(state)

    def align_x(self, width):
        '''align_x(width) -> x

        Moves the orig_x to aling the item
        '''
        max_width = CS.width

        if self.align == ALIGN_CENTER:
            x  = (max_width - width) / 2
        elif self.align == ALIGN_RIGHT:
            x = max_width - width
        elif self.align == ALIGN_LEFT:
            x = self.orig_x

        return x

    def stop(self):
        '''stop()
        
        stop() is called when the item is removed from the 
        surface. The item is not removed immediately, but it 
        loads the close-effects, and, when all are done, it
        kills itself.
        '''

        if self.keep_always:
            # do nothing is this in is a keep-always item
            return

        if self.waiting:
            self.kill()
            return

        self.closing = True

        self.seteffects('close')
        self.current_effects.update()

        if len(self.current_effects) == 0:
            self.kill()

    def force_stop(self):
        '''force_stop()

        Stop all the effects and kill itself. This does not show
        any close-effect
        '''

        for s in self.current_effects.sprites():
            s.stop()

        if not self.keep_always:
            self.kill()

    def kill(self):
        pygame.sprite.Sprite.kill(self)
        self.hide()

    def hide(self):
        '''hide()

        Hide the item. That is, creates a new surface (1x1), 
        will full alpha.
        '''
        # hide the item
        self.image = pygame.Surface((1,1)).convert_alpha()
        self.image.fill(0)
        self.rect = self.image.get_rect()

    def update(self, *k):
        '''update()

        The main method. It is called in every iteration of the 
        program. It updates all the effects, and check the TTL and 
        WAIT values.

        Save some rare exceptions, children never need to implement 
        this method.
        '''

        if self.waiting:
            if time.time() - self.start_time > self.wait_time:
                self.waiting = False
                self.image, self.rect = self.make_item()
                self.seteffects('open')
            else:
                return

        if not self.closing and self.ttl is not None:
            if time.time() - self.start_time > self.ttl:
                self.stop()
                return

        # update the effects
        self.current_effects.update()
        if len(self.current_effects) == 0:
            if self.closing:
                self.kill()
            elif self.effectstate == 'open':
                self.seteffects(self.nexteffectstate)

class ItemPageNumber(Item):

    def __init__(self, n, total):
        self.page_number = n
        self.total_pages = total
        self.original_top = 0
        self.keep_always = False

        # default state
        Item.__init__(self, None, '', {}, LastPoint())

    def set_keepalways(self, ka = True):
        self.keep_always = ka

        if not ka:
            # reset animations
            self.start_time = time.time() - 0.5

    def make_item(self):

        font = pygame.font.Font(None, 30)
        text = lambda N: ''.join([' %d ' % (n+1) for n in range(N)])

        canvas = pygame.Surface(font.size(text(self.total_pages)))
        canvas.fill((200,200,200))

        # page position
        offset = font.size(text(self.page_number-1))[0]
        textwidth = font.size(' %d ' % self.page_number)[0]
        canvas.fill((100,100,255), (offset, 0, textwidth, 30))

        # render numbers
        canvas.blit(font.render(text(self.total_pages), True, (0,0,0,255)), (0,0))

        # see if the page_number is showed
        cx, cy = canvas.get_size()
        if (offset + textwidth) > CS.width:
            if offset > cx - CS.width:
                start_x = cx - CS.width
            else:
                # center it
                start_x = offset - (CS.width - textwidth) / 2

            canvas = canvas.subsurface((start_x, 0, CS.width, cy))

        # save the image
        rect = pygame.Rect(0, CS.height - cy, CS.width, cy)
        image = pygame.Surface((CS.width, cy))

        if CS.width > cx:
            image.fill((200,200,200))

        image.blit(canvas, (0,0))
        return image, rect

    def update(self):
        if not self.keep_always:
            now = time.time() - self.start_time

            if now > 1.5:
                self.kill()
            elif now > 0.5:
                self.image.set_alpha(255 * (1.5 - now))
                self.rect.top = CS.height - (self.rect.height * (1.5 - now))


class ItemTimer(Item):
    def __init__(self):
        self.lastupdate = None
        self.keep_always = False
        self.start_time = None

        # default state
        Item.__init__(self, None, '', {}, LastPoint())

    def make_item(self):
        from Pyslide.Main import getuptime, getmain
        uptime = int(getuptime())
        main = getmain()

        color = (0,0,0,255)

        if main.totaltime is not None:
            uptime = main.totaltime - uptime
            if uptime < 0:
                color = (255,0,0,255) # red when uptime is negative

        if uptime < 60:
            fmt = ' %d seconds ' % uptime
        else:
            # use floor divisio (// operator)
            fmt = ' %d:%02d ' % (uptime // 60, uptime % 60)

        font = pygame.font.Font(None, 30)
        img = font.render(fmt, True, color)
        size = img.get_size()
        rect = pygame.Rect(CS.width - size[0], 0, size[0], size[1])

        surface = pygame.Surface(size)
        surface.fill((200,200,200))
        surface.blit(img, (0,0))

        return surface, rect

    def start(self, *k):
        Item.start(self, *k)
        self.lastupdate = time.time()

    def togglekeepalways(self):
        self.keep_always = not self.keep_always
        self.start()
        if not self.keep_always:
            self.start_time += -0.5

    def update(self):
        N = time.time()
        if N - self.lastupdate > 1:
            self.image, self.rect = self.make_item()
            self.lastupdate = N

        if not self.keep_always:
            now = N - self.start_time

            if now > 1.5:
                self.kill()
            elif now > 0.5:
                self.image.set_alpha(255 * (1.5 - now))
                self.rect.top = self.rect.height * (1.5 - now) - self.rect.height


# import items
from ItemText import ItemText
from ItemShape import ItemShape
from ItemImage import ItemImage
from ItemSystem import ItemSystem
from ItemList import ItemList


def getitemtype(name):
    availableitems = {
        'text': ItemText,
        'image': ItemImage,
        'shape': ItemShape,
        'system': ItemSystem,
        'list': ItemList,
    }

    # raise KeyError if item is not found
    return availableitems[name.lower()]


