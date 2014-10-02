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
from pygame.locals import *

class EffectError(Exception):
    pass

class StateInfo:
    def copy(self):
        from copy import copy
        return copy(self)

class ProxyStateInfo(object):
    def __init__(self, effect):
        object.__setattr__(self, 'e', effect)
    def __setattr__(self, at, val):
        for s in ('open', 'close', 'front', 'back'):
            s = getattr(self.e, s + 'state')
            if not hasattr(s, at):
                setattr(s, at, val)

class Effect(pygame.sprite.Sprite):
    '''Effect(kind, parent, attrs)

    This is the base class for all the effects
    '''

    def __init__(self, parent, attrs):
        pygame.sprite.Sprite.__init__(self)

        self.parent = parent
        self.attrs = attrs

        self.currentstate = None
        self.openstate = StateInfo()
        self.closestate = StateInfo()
        self.backstate = StateInfo()
        self.frontstate = StateInfo()

    def parse_attrs(self):
        '''parse_attrs()

        '''
        pass

    def setstate(self, state):
        '''setstate(state)

        '''

        self.currentstate = state

        import time
        self.start_time = time.time()

    def setend(self, state):
        self.kill()

    def stop(self):
        '''stop()

        Restores the image and rect of the parent and
        remove itself from all the groups
        '''
        self.kill()

    def update(self):
        '''update() -> None

        The sprite.update event
        '''
        pass

    def getstatedata(self, name = None):
        '''getstatedata(name = None) -> StateInfo

        name can be 'open', 'close', 'back' or Noe. If name is
        None, returns the current state
        '''

        if name is None:
            name = self.currentstate

        name = name + 'state'
        if not hasattr(self, name):
            from Pyslide import misc
            raise misc.PyslideError, 'Invalid effect name: ' + name

        return getattr(self, name)

    def usedstate(self, name):
        return True

def load(parent, name, attrs):
    '''load(parent, name, attrs) -> Effect

    Loads an effect. If the effect is not available, the EffectError
    exception is raised.
    '''

    try:
        e = available_effects[name]
    except KeyError:
        raise EffectError, 'There is no "%s" effect' % name

    return e(parent, attrs)

from MoveEffect import MoveEffect
from AlphaEffect import AlphaEffect #, VAlphaEffect, HAlphaEffect

available_effects = {
    'move': MoveEffect,
    'alpha': AlphaEffect,
};

