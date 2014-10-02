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

HEADER = '''#!/usr/bin/python
# -*- coding: latin1 -*-
# This is a compiled pyslide presentation
# Created on %(DATE)s

PYSLIDE_PATH = '%(PATH)s'

class main:
    fullscreen = %(FULLSCREEN)s
    size = None
    start_page = %(START_PAGE)s

import os.path
d, f = os.path.split(__file__)
if d:
    import os
    os.chdir (d)
del d, f

import sys
if PYSLIDE_PATH not in sys.path:
    sys.path.append(PYSLIDE_PATH)

from Pyslide import Presentation as P
from Pyslide import Content as C

c = C.Content()
c.set_attrs(%(MAINATTRS)s)
''' 

FOOTER = '''
#Run presentation\nP.BuildPresentation(c, main).run()

'''

def Compile(content, output, main):
    import time
    import os.path

    w = output.write

    DATE = time.strftime('%c')
    PATH, N = os.path.split(__file__)
    PATH = PATH[:PATH.rfind('/')]
    FULLSCREEN = repr(main.fullscreen)
    START_PAGE = getattr(main, 'start_page', 0)

    contentattrs = content.get_attrs()
    if hasattr(main, 'size') and main.size is not None:
        contentattrs = contentattrs.copy()
        contentattrs['size'] = main.size

    MAINATTRS = repr(contentattrs)

    w(HEADER % locals())

    for page in content.pages():
        w('\n# %New page%\n')
        w('p = c.add_page(%s)\n' % repr(page.get_attrs()))
        for group in page.groups():
            w('g = p.add_group()         # %Group%\n')
            for item in group.items():
                w('g.add_item(%s)\n' % repr(item))


    w(FOOTER)

