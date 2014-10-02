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
from Pyslide import misc
from Pyslide.Effects import Effect, ProxyStateInfo
from Pyslide.Presentation import CurrentSurface as CS

# effect types

errmsg_showed = False

class AlphaEffect(Effect):

    def __init__(self, *k):
        Effect.__init__(self, *k)

        self.origimage = None

    def parse_attrs(self):
        Effect.parse_attrs(self)

        try:
            import _alphaeffect
        except ImportError:
            global errmsg_showed

            if not errmsg_showed:
                errmsg_showed = True
                import logging
                logging.error('You have to compile the alphaeffect module to use alpha effects')

            self.available = False
            return 

        self.available = True
        self.alphaobj = None

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
            if key == 'time':
                try:
                    state.time = float(val) / 10.
                except ValueError:
                    raise misc.PyslideError, 'Invalid time value: ' + str(val)

            elif key == 'set':
                try:
                    state.set = int(val)
                    if not 0 <= state.set < 256:
                        raise ValueError
                except ValueError:
                    raise misc.PyslideError, 'Invalid value for "set": ' + str(val)

            elif key == 'speed':
                try:
                    state.time = None
                    state.speed = CS.map_units(float(val))
                except ValueError:
                    raise misc.PyslideError, 'Invalid value for "speed": ' + str(val)

#            elif key == 'center':
#                state.center = CS.map_units(* misc.parse_point(val))

            elif key == 'direction':
                val = val.lower()
                if val == 'positive':
                    state.direction = _alphaeffect.DIRECTION_POS
                elif val == 'negative':
                    state.direction = _alphaeffect.DIRECTION_NEG
                else:
                    raise misc.PyslideError, \
                        'Alpha direction has to be "positive" or "negative"'

            elif key == 'hide':
                state.hide = val.lower() == 'true'

            elif key == 'type':
                val = val.lower()
                if val == 'full':
                    t = _alphaeffect.ET_FULL
                elif val == 'horizontal':
                    t = _alphaeffect.ET_HOR
                elif val == 'vertical':
                    t = _alphaeffect.ET_VER
#                elif val == 'radial':
#                    t = _alphaeffect.ET_RAD
                else:
                    raise misc.PyslideError, 'Invalid type for alpha effect: ' + val

                state.type = t

        # default values
        allstates.hide = None
        allstates.direction = _alphaeffect.DIRECTION_POS
        allstates.time = None
        allstates.speed = None
        allstates.set = None
        allstates.type = None

    def setstate(self, statename):
        if not self.available:
            self.kill()
            return

        if self.currentstate == statename:
            return

        Effect.setstate(self, statename)

        # save alpha state
        if self.alphaobj is not None:
            prevstate = self.alphaobj.getstate()
        else:
            prevstate = None

        import _alphaeffect
        state = self.getstatedata().copy()

        # special case when the attribute 'set' is used.
        if state.set is not None:
            if self.origimage is None:
                self.origimage = self.parent.image

            if self.origimage.get_masks()[3] == 0:
                self.origimage.set_alpha(state.set)
            else:
                self.parent.image = _alphaeffect.setalpha(self.origimage, state.set)

            self.kill()
            self.alphaobj = None

        else:

            if state.type is None:
                # there is no effect
                self.kill()
                return

            # create the alphaobj
            if self.origimage is None:
                self.origimage = self.parent.image

            # compute time if speed is used
            if state.time is None:
                size = self.origimage.get_size()
                if state.type == _alphaeffect.ET_VER:
                    m = size[1]
                elif state.type == _alphaeffect.ET_HOR:
                    m = size[0]
                else:
                    import logging
                    logging.error('Alpha effect need time')
                    self.kill()
                    return

                state.time = m / state.speed

            # create the alpha object

            if state.hide is None:
                state.hide = statename == 'close'

            self.alphaobj = _alphaeffect.AlphaEffect (
                time = state.time,
                source = self.origimage,
                type = state.type,
                hide = state.hide,
                direction = state.direction)

            self.parent.image = self.alphaobj.start()
            self.alphaobj.iter()

    def setend(self, statename):
        Effect.setend(self, statename)

        state = self.getstatedata(statename)
        if state.set is not None:
            self.setstate(statename)
        elif state.hide is not None:
            if state.hide:
                if self.origimage is None:
                    self.origimage = self.parent.image

                self.parent.hide()

        self.alphaobj = None

    def update(self, *k):
        if self.alphaobj is not None:
            import _alphaeffect
            if self.alphaobj.iter() == _alphaeffect.ITER_STOP:
                self.stop()
                self.alphaobj = None

