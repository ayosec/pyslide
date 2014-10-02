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


class C_signalhandler:

    def __init__(self):
        self.pids = {}

        import atexit
        atexit.register(C_signalhandler.atexit, self)

    def atexit(self):
        import os
        for p in self.pids.keys():
            os.kill(p, 15)

    def register(self, item, pid):
        import weakref
        self.pids[pid] = weakref.ref(item)

    def __call__(self, signum, stack):
        import os

        pids = []
        try:
            while True:
                pid, status = os.waitpid(0, os.WNOHANG)
                if pid == 0:
                    break

                pids.append(pid)
        except OSError:
            pass

        for p in pids:
            if p in self.pids.keys():
                item = self.pids[p]()
                if item is not None:
                    item.stop()
                del self.pids[p]


signalhandler = C_signalhandler()

