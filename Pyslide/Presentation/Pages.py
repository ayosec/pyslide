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

def renderbackground(surface, background):
    '''renderbackground(surface, background)

    Renders background on surface. background can be:

     * a pygame.Surface object (use blit)
     * a tuple, interpreted as a color (use fill)
     * None.. do nothing

    '''

    if isinstance(background, tuple):
        surface.fill(background)
    elif isinstance(background, pygame.Surface):
        surface.blit(background, (0,0))
    elif background is not None:
        raise TypeError, 'background has to be Surface, tuple or None'

def createbackground(attrs):
    '''createbackground(attrs) -> background

    Create a background for this attributes. "background" can be:

     * a pygame.Surface object
     * a tuple: this is a color used to fill the background
     * None: there is no background for this attributes.

    '''

    from Pyslide import misc
    from Pyslide.Presentation import CurrentSurface
    size = CurrentSurface.width, CurrentSurface.height

    if attrs.has_key('bggrad'):
        try:
            top, bottom = attrs['bggrad'].split('-', 1)
        except ValueError:
            raise misc.PyslideError, 'Invalid value for bggrad: ' + attrs['bggrad']

        top = misc.parse_color(top)
        bottom = misc.parse_color(bottom)

        if None in (top, bottom):
            raise misc.PyslideError, 'Invalid gradient value: ' + attrs['bggrad']

        bg = pygame.Surface(size)
        grad = misc.RenderGradient(bg, top, bottom)
        pygame.surfarray.blit_array(bg, grad)    

    elif attrs.has_key('bg'):
        scale = attrs.get('bgscale', 'yes') == 'yes'

        from Pyslide.Main.Images import imageloader
        bg = imageloader.loadfile(attrs['bg'])
        if scale:
            bg = pygame.transform.scale(bg, size).convert()
        else:
            s = bg.get_size()
            if (s[0] < size[0]) or (s[1] < size[1]):
                i = pygame.Surface(size).convert()
                i.fill(0)
                i.blit(bg, (0,0))
                bg = i
            else:
                bg = bg.convert()

    elif attrs.has_key('bgcolor'):
        bg = misc.parse_color(attrs['bgcolor'])
        if bg is None:
            raise misc.PyslideError, 'Invalid color: ' + attrs['bgcolor']

    else:
        bg = None

    return bg

def applycss(item, group):
    '''applycss(attrs, item, group) -> item

    Get attributes for the item. Returns the item type and its attributes
    '''

    from Pyslide.misc import PyslideError

    parentobj = group.parent().parent()

    # its own attributes
    newattrs = item['attrs'].copy()
    itemtype = item['type']

    # class attributes
    if newattrs.has_key('class'):
        c = newattrs['class']
        del newattrs['class']

        try:
            classattrs = parentobj.cssclass[c].items()
        except KeyError:
            raise PyslideError, 'Unknown class: ' + c

        for key, val in classattrs:
            if not newattrs.has_key(key):
                newattrs[key] = val


    # alias attributes
    if parentobj.cssalias.has_key(itemtype):
        alias = parentobj.cssalias[itemtype]
        if itemtype not in ('text', 'image', 'system', 'shape', 'list'):
            try:
                itemtype = alias['item-type']
            except:
                raise PyslideError, \
                    'Invalid alias "%s": item-type attribute not present' % itemtype

        for key, val in alias.items():
            if not newattrs.has_key(key):
                newattrs[key] = val

    # group attibutes
    for key, val in group.attrs.items():
        if not newattrs.has_key(key):
            newattrs[key] = val


    # remove for- attributes, if it is necessary
    posgroup = group.getposition(item) + 1

    for key in newattrs.keys():
        if key.startswith('for-'):
            place = key.split('-')[1]
            put = False

            try:
                # is it a number?
                put = (int(place) == posgroup)

            except ValueError:
                place = place.lower()
                v = ['first', 'second', 'third']
                if place in v:
                    put = (v.index(place) + 1) == posgroup

                elif (place == 'even' and (posgroup % 2) == 0) \
                   or (place == 'odd' and (posgroup % 2) == 1):
                    put = True

                elif place == 'last':
                    put = group.isthelast(item)

            if put:
                k = '-'.join(key.split('-')[2:])
                if not newattrs.has_key(k):
                    newattrs[k] = newattrs[key]
            del newattrs[key]
            
    # THE item!
    return {'type': itemtype, 'content': item['content'], 'attrs': newattrs}


class CreatedPage:

    def __init__(self, attrs, groups):
        self.groups = groups
        self.attrs = attrs
        self.stage = 0
        self.__bg = None

        if attrs.has_key('ttl'):
            try:
                self.ttl = int(attrs['ttl']) / 10.
            except ValueError:
                raise PyslideError, 'Invalid TTL value: ' + str(attrs['ttl'])
        else:
            self.ttl = None

    def currentgroups(self):
        return self.groups[:self.stage+1]

    def getcurrentgroup(self):
        return self.groups[self.stage]

    def nextstage(self):
        if self.stage < len(self.groups) - 1:
            self.stage += 1
            return self.groups[self.stage]
        return None

    def prevstage(self):
        if self.stage > 0:
            self.stage -= 1
            return self.groups[self.stage + 1]
        return None

    def setstage(self, n):
        if n < 0:
            self.stage = len(self.groups) + n
        else:
            self.stage = n

    def getbackground(self):
        if self.__bg is None:
            self.__bg = createbackground(self.attrs)
        return self.__bg

def iskeepalways(item, group):
    '''iskeepalways(item, group) -> bool

    Returns True if item is a keep-always item
    '''

    def i():
        yield item['attrs']
        yield group.attrs

        p = group.parent().parent()
        if p.cssalias.has_key(item['type']):
            yield p.cssalias[item['type']]

        if item['attrs'].has_key('class'):
            c = item['attrs']['class']
            if p.cssclass.has_key(c):
                yield p.cssclass[c]


    for attrs in i():
        if attrs.has_key('keep-always'):
            return attrs['keep-always'] == 'yes'

    return False

class Page:
    def __init__ (self, page):
        self.page = page

    def getkeepalwaysitems(self):

        # we have to create all the previous items to 
        # the keep-always items, because that items may 
        # need the LastPoint info.

        # First, create a flat list of items
        from copy import copy as C

        items = []
        for g in self.page.groups():
            x = C(g.items())
            for i in x: i['parent-group'] = g
            items += x

        # find the last keep-always item
        last = -1
        keepalwaysitems = []
        for n, i in enumerate(items):
            if iskeepalways(i, i['parent-group']):
                last = n
                keepalwaysitems.append(i)

        from Pyslide import Items

        result = []
        lp = Items.LastPoint()
        if last >= 0:
            for item in items[:last+1]:
                i = self.createitem(item, item['parent-group'], lp)
                if item in keepalwaysitems:
                    result.append(i)

        return result

    def createitem(origitem, group, lp):
        from Pyslide import Items
        from copy import copy as C

        item = applycss(origitem, group)

        try:
           itemtype = Items.getitemtype(item['type'])
        except KeyError:
            from Pyslide import misc
            raise misc.PyslideError, 'invalid item: ' + item['type']

        try:
            i = itemtype((origitem, group), C(item['content']), C(item['attrs']), lp)
        except Items.ReplaceThisItem, (t,):
            i = t

        return i

    createitem = staticmethod(createitem)

    def createpage(self):
        from Pyslide import Items

        groups = []
        lp = Items.LastPoint()

        for group in self.page.groups():
            groups.append([self.createitem(i, group, lp) for i in group.items()])

        return CreatedPage(self.page.get_attrs(), groups)


