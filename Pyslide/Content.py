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
                                                                                                

import weakref

class Group:
    def __init__(self, items, parent):
        self.__items = items
        self.attrs = {}
        self.parent = weakref.ref(parent)

    def add_item(self, item):
        self.__items.append(item)
        return self.__items[-1]

    def del_item(self, n):
        del self.__items[n]

    def item(self, n):
        return self.__items[n]

    def items(self):
        return self.__items

    def getposition(self, item):
        p = 0
        t = item['type']
        for i in self.__items:
            if i is item:
                return p
            elif i['type'] == t:
                p += 1
            else:
                p = 0

    def isthelast(self, item):
        t = item['type']
        last = False
        for i in self.__items:
            if t == i['type']:
                last = item is i

        return last

class Page:
    def __init__(self, parent, attrs={}, groups=[]):
        self.__attrs = attrs.copy()
        self.__groups = groups[:]
        self.parent = weakref.ref(parent)

    def groups(self):
        return self.__groups

    def group(self, n):
        return self.__groups[n]

    def add_group(self, items = []):
        if isinstance(items, Group):
            self.__groups.append(items)
        else:
            self.__groups.append(Group(items[:], self))
        return self.__groups[-1]

    def del_group(self, n):
        del self.__groups[n]

    def get_attrs(self):
        return self.__attrs

    def set_attr(self, attr, value):
        self.__attrs[attr] = value

class Content:
    def __init__(self):
        self.__pages = []
        self.__attrs = {}

        self.cssclass = {}
        self.cssalias = {}

    def pages(self):
        return self.__pages

    def page(self, n):
        return self.__pages[n]

    def add_page(self, attrs={}, groups=[]):
        self.__pages.append(Page(self, attrs.copy(), groups[:]))
        return self.__pages[-1]

    def del_page(self, n):
        del self.__pages[n]

    def get_attrs(self):
        return self.__attrs

    def set_attrs(self, attrs):
        self.__attrs = attrs.copy()

    def move_page(self, from_, to):
        page = self.__pages[from_]
        del self.__pages[from_]
        self.__pages.insert(to, page)


