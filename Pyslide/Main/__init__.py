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

__doc__ = '''
pyslide [options] file

    -h --help               Shows this help
    --version               Shows the version
    -c -compile             Compile the presentation. Code is output by 
                            stdout.
    -f                      Use fullscreen on start.
    -K --keep-dir           Don't change the current directory. By default,
                            Pyslide sets the CWD to the presentation 
                            directory.
    -H dir --html=dir       Export to html. The files are saved in dir/
    -s --size=size          Window size. This overrides the size value
                            of the presentation
    -p PAGE_NUM             Jumps to page PAGE_NUM
    --color-names           Show all the available color names
    -x --script             Load the XML file as a script.
    -S --standalone         Makes a standalone presentation. 
    -u                      Enable unsecure mode. If you want to run
                            external programs you have to set unsecure mode.
    -v                      Verbose mode. Put more -v if you want more 
                            output.
    -I                      Ignore error on images. That is, if an image can't
                            be loaded, Pyslide will create an empty image,
                            instead of exits.
    -t minutes              Estimated time of the presentation

See pyslide manual page for more information.
'''

from Pyslide.misc import PyslideError
import logging

class Execute:
    def __init__(self, main):
        self.main = main

    def __call__(self):
        import os, logging

        from Pyslide.Presentation import BuildPresentation

        main = self.main
        cwd = os.getcwd()

        for fn in main.files:
            try:
                fo = main.loadfile(fn)
                p = BuildPresentation(fo, main)
                p.run()
            except PyslideError, i:
                if os.getenv('RAISE', False):
                    raise

                logging.critical('Invalid file "%s": %s' % (fn, str(i)))

        os.chdir(cwd)

class Standalone:
    def __init__(self, main):
        self.main = main

    def __call__(self):
        from Pyslide.File import WriteFile
        import sys

        try:
            f = self.main.loadfile(self.main.files[0])
            WriteFile(sys.stdout, f, True)
        except PyslideError, i:
            logging.critical(str(i))

class Compile:
    def __init__(self, main):
        self.main = main

    def __call__(self):
        from Pyslide.Compile import Compile
        import sys

        try:
            f = self.main.loadfile(self.main.files[0])
            Compile(f, sys.stdout, self.main)
        except PyslideError, i:
            logging.critical(str(i))



class ExportHtml:
    def __init__(self, main, directory):
        self.main = main
        self.directory = directory

    def __call__(self):
        if self.directory[0] != '/':
            import os, os.path
            self.directory = os.path.abspath(self.directory)

        try:
            f = self.main.loadfile(self.main.files[0])

            from Pyslide.Export import Html
            Html(f, self.main).export(self.directory)

        except PyslideError, i:
            logging.critical(str(i))

def printcolornames(out = None):
    from pygame.colordict import THECOLORS as d
    keys = d.keys()
    keys.sort()
    width = max([len(x) for x in keys])

    for k in keys:
        print >> out, k.ljust(width), '%3d %3d %3d' % d[k][:3]

class Main:

    def __init__(self, cmdline = None):
        if cmdline is None:
            import sys
            cmdline = sys.argv[1:]

        self.cmdline = cmdline[:]
        self.unsecure = False
        self.fullscreen = False
        self.keep_dir = False
        self.size = None
        self.start_page = 0
        self.as_script = False
        self.action = None
        self.verbose = 0
        self.imagerrors = True
        self.totaltime = None

        # save this object as the main
        setmain(self)

    def initialstate(self):
        import locale, signal, os
        from Pyslide.Main.commands import signalhandler

        locale.setlocale(locale.LC_ALL, '')
        signal.signal(signal.SIGCHLD, signalhandler)

    def start(self):

        # initial configuration
        self.initialstate()

        # argumentos
        import sys
        import getopt

        try:
            opts, args = getopt.getopt(self.cmdline, 'H:s:p:t:hfKxSucvI',
                ('help', 'version', 'compile', 'keep-dir', '--standalone', 
                 'html=', 'size=', 'color-names', 'script', 'time='))
        except getopt.GetoptError, e:
            print >> sys.stderr, __doc__
            sys.exit(2)

        for opt, arg in opts:
            if opt in ('-c', '--compile'):
                if len(args) != 1:
                    print >> sys.stderr, 'You can only compile one presentation at time'
                    sys.exit(2)

                self.action = Compile(self)

            elif opt in ('-t', '--time'):
                try:
                    self.totaltime = float(arg) * 60
                except ValueError:
                    print >> sys.stderr, 'Invalid time: ' + arg
                    sys.exit(2)

            elif opt == '-I':
                self.imagerrors = False

            elif opt == '-v':
                self.verbose += 1

            elif opt == '-u':
                self.unsecure = True

            elif opt in ('-S', '--standalone'):
                self.action = Standalone(self)

            elif opt in ('-x', '--script'):
                self.as_script = True

            elif opt in ('-H', '--html'):
                self.action = ExportHtml(self, arg)

            elif opt in ('-s', '--size'):
                self.size = arg

            elif opt == '-f':
                self.fullscreen = True

            elif opt == '--version':
                import Pyslide
                print 'Pyslide', Pyslide.VERSION
                sys.exit(0)

            elif opt in ('-h', '--help'):
                print __doc__
                sys.exit(0)

            elif opt in ('-K', '--keep-dir'):
                self.keep_dir = True

            elif opt == '-p':
                try:
                    self.start_page = int(arg)
                except ValueError:
                    print >> sys.stderr, 'Invalid page number:', arg
                    sys.exit(1)

                if self.start_page == 0:
                    print >> sys.stderr, 'Invalid page number: You can\'t use zero'
                    sys.exit(1)
                elif self.start_page > 0:
                    self.start_page -= 1

            elif opt == '--color-names':
                printcolornames()
                sys.exit(0)

        if len(args) < 1:
            print >> sys.stderr, __doc__
            sys.exit(2)

        self.files = args

        if self.action is None:
            self.action = Execute(self)

        # initialize logger
        l = logging.getLogger()
        l.addHandler(logging.StreamHandler(sys.stderr))

        if self.verbose == 0:
            level = logging.ERROR
        elif self.verbose == 1:
            level = logging.INFO
        else:
            level = logging.DEBUG
            
        l.setLevel(level)

        # Load psyco if it is available, only for a x86 machines.
        # This is because psyco is only available in this arch :-(.
        # This check avoids unnecesary message in non-x86 machines.
        import os
        if os.uname()[4] in ('i386', 'i486', 'i586', 'i686'):
            try:
                import psyco
                psyco.profile()
            except ImportError:
                logging.warning(
                    'Psyco is not available. If you install it you will get '
                    'a better performance')

    def action(self):
        # oh.. yeah...
        self.action()

    def loadfile(self, filename):
        from Pyslide.File import ReadFile

        if not self.keep_dir:
            import os.path
            path, filename = os.path.split(filename)

            if path:
                try:
                    logging.info('Change directory to ' + path)
                    os.chdir(path)
                except OSError, e:
                    raise PyslideError, ('Invalid directory: ' + path)

        logging.info('Loading ' + filename)
        return ReadFile(filename, self)


import time
STARTUP_TIME = time.time()

def getuptime():
    return time.time() - STARTUP_TIME

__MAINOBJECT__ = None
def setmain(main):
    global __MAINOBJECT__
    import weakref

    __MAINOBJECT__ = weakref.ref(main)

def getmain():
    if __MAINOBJECT__ is not None:
        return __MAINOBJECT__()

