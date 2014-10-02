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
from Pyslide.Effects import Effect, StateInfo, ProxyStateInfo
from Pyslide.Presentation import CurrentSurface as CS

def getcenter(item):
    return (CS.width - item.width) / 2, (CS.height - item.height) / 2

class MoveEffect(Effect):
    '''MoveEffect

    Implements the Move effect
    '''

    def parse_attrs(self):
        Effect.parse_attrs(self)

        from Pyslide import misc

        # initialize states
        allstates = ProxyStateInfo(self)

        for key, val in self.attrs.items():
            key = key.lower()

            # state
            t = key.find('-')
            state = allstates

            if t != -1: 
                s = key[:t]
                if s in ('open', 'close', 'back', 'front'):
                    state = getattr(self, s + 'state')
                    key = key[t+1:]

            # parameter
            if key == 'start':
                val = val.lower()
                if val == 'origin':
                    state.start = self.parent.orig_x, self.parent.orig_y
                elif val == 'center':
                    state.start = getcenter(self.parent)
                else:
                    state.start = CS.map_units(* misc.parse_point(val))
                    state.relstart = misc.parse_relativepoint(val)
            elif key == 'end':
                val = val.lower()
                if val == 'origin':
                    state.end = self.parent.orig_x, self.parent.orig_y
                elif val == 'center':
                    state.end = getcenter(self.parent)
                else:
                    state.end = CS.map_units(* misc.parse_point(val))
                    state.relend = misc.parse_relativepoint(val)
            elif key == 'time':
                state.speed = None
                try:
                    state.time = float(val) / 10.
                except ValueError:
                    raise misc.PyslideError, 'Invalid "time" value: ' + val
            elif key == 'speed':
                state.time = None
                try:
                    state.speed = CS.map_units(float(val))
                except ValueError:
                    raise misc.PyslideError, 'Invalid "speed" value: ' + val


        # default values..
        allstates.start = None
        allstates.end = None
        allstates.time = None
        allstates.speed = None
        allstates.relstart = None
        allstates.relend = None

    def usedstate(self, name):
        s = self.getstatedata(name)
        return not \
            ((s.start is None and s.end is None) or (s.time is None and s.speed is None))

    def setstate(self, statename):
        if self.currentstate == statename:
            return

        Effect.setstate(self, statename)
        state = self.getstatedata().copy()

        # check if there is any info for this state.
        if not self.usedstate(statename):
            self.kill()
            return

        # copy the current point where point is None
        curpoint = self.parent.rect.topleft
        if state.start is None:
            state.start = curpoint
        elif state.end is None:
            state.end = curpoint

        # relative points..
        for n in (0, 1):
            if state.relstart is not None and state.relstart[n]:
                state.start = list(state.start)
                state.start[n] += curpoint[n]
            if state.relend is not None and  state.relend[n]:
                state.end = list(state.end)
                state.end[n] += curpoint[n]

        # work only with time, since this is easier than with speed
        if state.time is None:
            sx, sy = state.start
            ex, ey = state.end
            z = state.speed

            state.time = (((ex-sx)**2 + (ey - sy)**2)**0.5) / z
            state.speed = None

        # move to the first iteration
        self.parent.rect.topleft = state.start

        self.movestate = state

    def update(self, *k):
        state = self.movestate

        import time
        delta = (time.time() - self.start_time)

        if delta < state.time:
            delta =  (state.time - delta) / state.time
            sx, sy = state.start
            ex, ey = state.end
            nx = ex + (sx - ex) * delta     # new point
            ny = ey + (sy - ey) * delta
            self.parent.rect.topleft = nx, ny
        else:
            self.parent.rect.topleft = state.end
            self.stop()

    def setend(self, statename):

        Effect.setend(self, statename)

        state = self.getstatedata(statename)
        if state.end is not None and state.relend is None:
            self.parent.rect.topleft = state.end

