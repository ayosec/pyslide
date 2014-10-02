#!/usr/bin/python

from distutils.core import setup
from distutils.core import Extension

classifiers = '''
Development Status ::  5 - Production/Stable
Environment :: X11 Applications
Topic :: Multimedia :: Graphics :: Presentation
License :: OSI Approved :: GNU General Public License (GPL)
'''.split('\n')

setup(name = 'pyslide', version = "0.4",
    author = 'Ayose Cazorla',
    author_email = 'ayose.cazorla@hispalinux.es',
    url = 'http://hispalinux.es/~setepo/pyslide/',
    license = 'GNU General Public License (GPL)',
    description = 'A presentation program',
    packages = ['Pyslide', 'Pyslide.Items', 'Pyslide.Main',
                'Pyslide.Effects', 'Pyslide.Presentation'],
    scripts = ['pyslide'],
    ext_modules = [
        Extension("Pyslide.Effects._alphaeffect", 
            ['extras/alphaeffect.c', 'extras/iters.c'],
            include_dirs=['/usr/include/SDL'], 
            libraries=['SDL'])],

    classifiers = classifiers)
