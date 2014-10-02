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
from Pyslide import Presentation, misc
CS = Presentation.CurrentSurface

class ItemSystem(pygame.sprite.Sprite):

    processrunning = {}

    def __init__ (self, parent, content, attrs, last_point):
        pygame.sprite.Sprite.__init__(self)

        del content # not used

        self.keep_always = False
        self.cmd_str = None
        self.method = None
        self.stopwhen_close = False
        self.timer = None
        self.starttime = None
        self.pid = None
        self.parent = parent

        self.attrs_item = attrs.copy()

        for key, val in attrs.items():
            key = key.lower()
            if key == 'method':
                self.method = val.lower()
                del self.attrs_item['method']

                if self.method not in ('read', 'start'):
                    raise misc.PyslideError, 'method attibute has to be "read" or "start"'

            elif key == 'cmd':
                self.cmd_str = val
                del self.attrs_item['cmd']

            elif key == 'stopwhen':
                if val.startswith('timer:'):
                    self.timer = float(val[6:]) / 10.
                elif val == 'close':
                    self.stopwhen_close= True
                else:
                    raise misc.PyslideError, 'Unknow value for stopwhen: ' + str(val)

        if None in (self.cmd_str, self.method):
            raise misc.PyslideError, \
                'You have to set both "method" and "cmd" attibutes for <system"'

        if self.method == 'read':
            # create text item, and replace me with it
            import os
            r, w = os.pipe()
            if os.fork() == 0:
                os.close(r)
                os.dup2(w, 1)  # stdout
                os.execv('/bin/sh', ('sh', '-c', self.cmd_str))

            os.close(w)
            cnt = ''
            while True:
                try:
                    l = os.read(r, 1000)
                except OSError, e:
                    # ignore error if it was caused by a signal
                    if e.errno != 4:
                        raise

                    continue

                if not l:
                    break
                cnt += l

            os.close(r)

            from Pyslide.Items import ItemText, ReplaceThisItem
            sprite = ItemText(None, cnt, self.attrs_item, last_point)
            raise ReplaceThisItem, sprite

    def update(self):
        if self.timer is not None:
            import time
            if time.time() - self.starttime > self.timer:
                self.stop()

    def start(self, onpagenumber):
        self.onpagenumber = onpagenumber

        import os
        # fork and run the process. Don't change std{in,out,err} 
        self.pid = os.fork()
        if self.pid == 0:
            os.execv('/bin/sh', ('sh', '-c', self.cmd_str))

        if (not self.stopwhen_close) and (self.timer is None):
            self.kill()
        else:
            import time
            self.starttime = time.time()

            from Pyslide.Main import commands
            commands.signalhandler.register(self, self.pid)
 
            # fake image
            self.image = pygame.Surface((0,0))
            self.rect = (0,0,0,0)

    def stop(self):
        import os
        try:
            os.kill(self.pid, 15) # SIGTERM
        except OSError:
            pass

        self.kill()

    force_stop = stop


    def getid(self):
        return id(self.parent)

    def getparent(self):
        return self.parent
