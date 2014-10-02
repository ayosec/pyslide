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
                                                                                                

import misc
class InvalidCSS(misc.PyslideError):
    'This CSS is not valid'

class InvalidXML(misc.PyslideError):
    'This XML file is not valid'

import xml.sax
import xml.sax.saxutils
import xml.sax.xmlreader

from Content import Group, Page, Content
            
defaulttags = ('text', 'image', 'shape', 'system', 'list')

class ContentParser(xml.sax.saxutils.DefaultHandler):
    def __init__(self, main, filename):
        xml.sax.saxutils.DefaultHandler.__init__(self)

        self.filename = filename
        self.__content = Content()
        self.depth = 0
        self.unsecure = main.unsecure
        self.main = main

        self.last_page = None
        self.last_item = None
        self.last_group = None
        self.last_tag = None

        self.current_tag = None

        self.aliases = self.__content.cssalias
        self.styles = self.__content.cssclass
        self.contentchars = None
        self.currentimageid = None

        import re
        self.re_css_class = re.compile(r'^\s*?(\S+)\s*\{(\s*.+?\s*)\}(.*)$', re.S)
        self.re_css_comments = re.compile(r'/\*.*?\*/', re.S)

    def showerror(self, exception, text):
        linenumber = self.locator.getLineNumber()
        columnnumber = self.locator.getColumnNumber()

        # open the file and print the error line
        try:
            f = open(self.filename)
        except IOError:
            pass
        else:
            import sys
            lines = f.readlines()

            s = max(1, linenumber - 3)
            while s < linenumber:
                sys.stderr.write('%5d %s' % (s, lines[s-1]))
                s += 1

            sys.stderr.write('\033[1;31m%5d\033[m %s' % (s, lines[s-1]))
            s += 1

            t = min(linenumber + 3, len(lines)) + 1
            while s < t:
                sys.stderr.write('%5d %s' % (s, lines[s-1]))
                s += 1

            sys.stderr.write('\n')

        # raise the exception
        raise exception, '%s:%d:%d: %s' % \
            (self.filename, linenumber, columnnumber, text)

    def error(self, exception):
        self.showerror(InvalidXML, exception.args[0])

    fatalError = error

    def setDocumentLocator(self, locator):
        self.locator = locator

    def getlocation(self):
        l = self.locator
        return '%d:%d:' % (l.getLineNumber(), l.getColumnNumber())

    def startElement(self, name, xml_attrs):
        self.depth += 1
        self.current_tag = name

        # Copy the attributes into a dictionary
        attrs = {}
        for key, val in xml_attrs.items(): attrs[key] = val

        if name == 'presentation':
            if self.depth != 1:
                self.showerror(InvalidXML, 'The root node has to be <presentation>')

            # Save the presentation attributes.
            self.__content.set_attrs(attrs)

        elif name == 'page':
            if self.depth != 2:
                self.showerror(InvalidXML, '<page> has to be a child of the root node')

            self.last_page = self.__content.add_page(attrs)

        elif name == 'group':
            if self.depth != 3:
                self.showerror(InvalidXML, '<group> has to be a child of a page')

            self.last_group = self.last_page.add_group([])
            self.last_group.attrs = attrs

        elif name == 'style':
            # limited support for CSS.
            if attrs.has_key('source'):
                # load and external file
                try:
                    self.contentchars = open(attrs['source']).read()
                except IOError, e:
                    self.showerror(InvalidCSS, 'Unable to load the file: ' + str(e))
            else:
                self.contentchars = ''

        elif name == 'defimage':
            try:
                self.currentimageid = attrs['id']
            except KeyError:
                self.showerror(InvalidXML, 'You have to put an id for <defimage>')

            self.contentchars = ''

        else:

            if (name in defaulttags) or self.aliases.has_key(name):
                if self.depth != 4:
                    self.showerror(InvalidXML, '<%s> has to be a child of a group' % name)
            else:
                self.showerror(InvalidXML, 'Unknown tag: "%s"' % name)

            if name == 'system' and not self.unsecure:
                raise InvalidXML, '"unsecure mode" is required for <system> tags.'

            # check (if it is an alias) if the alias exists, and it is correct
            if self.aliases.has_key(name):
                al = self.aliases[name]
                if name not in defaulttags:
                    if not al.has_key('item-type'):
                        raise InvalidCSS, \
                          'Invalid alias "%s": item-type attribute not present' % name

            self.last_item = \
                self.last_group.add_item({'type': name, 'attrs': attrs, 'content': ''})


    def endElement(self, name):
        if self.current_tag == 'style':
            css, alias = self.parsecss(self.contentchars)
            for css_class, attributes in css.items():
                if self.styles.has_key(css_class):
                    dest = self.styles[css_class]
                else:
                    dest = self.styles[css_class] = {}

                for key, val in attributes.items():
                    dest[key] = val

            for alias, attributes in alias.items():
                self.aliases[alias] = attributes

        elif self.current_tag == 'defimage':
            from Pyslide.Main.Images import imageloader
            imageloader.saveimage(self.currentimageid, self.contentchars)

        self.contentchars = None
        self.current_tag = None
        self.depth -= 1
        self.last_tag = name

    def parsecss(self, css_text):
        css = {}
        aliases = {}

        # remove comments, if any
        css_text = self.re_css_comments.sub('', css_text)
        while True:
            m = self.re_css_class.match(css_text)
            if not m:
                return css, aliases

            # new class
            class_name = m.group(1).lower()
            content = m.group(2)
            css_text = m.group(3) 

            # parse attributes
            d = {}
            for line in content.split(';'):
                line = line.strip()
                if not line: continue
                try:
                    key, val = line.split(':')
                except ValueError:
                    raise InvalidCSS, 'Incorrect syntax. (":")'

                d[key.strip().lower()] = val.strip()

            if class_name[0] == '.':
                css[class_name[1:]] = d
            else:
                aliases[class_name] = d

    def characters(self, chrs):
        if self.current_tag in ('style', 'defimage'):
            self.contentchars += chrs

        elif self.depth == 4:
            self.last_item['content'] += chrs

    def get_content(self):
        return self.__content

def ReadFile(filename, main):

    try:
        f = open(filename)
    except IOError, e:
        raise misc.PyslideError, e

    if main.as_script:
        # ignore begining lines which starts with a '#'
        from cStringIO import StringIO
        n = StringIO()
        while True:
            l = f.readline()
            if not l:
                return Content()

            if l[0] != '#':
                n.write(l)
                break

        n.write(f.read())
        f = n
        f.seek(0)

    inputsource = xml.sax.InputSource()
    inputsource.setByteStream(f)

    parser = xml.sax.make_parser()
    dh = ContentParser(main, filename)
    parser.setContentHandler(dh)
    parser.setErrorHandler(dh)
    try:
        parser.parse(inputsource)
    except xml.sax.SAXException, e:
        raise InvalidXML, e

    return dh.get_content()


def WriteFile(file, content, standalone = False):

    # TODO use pyxml or similar

    imageids = []

    def write_open(node, attrs, marg=0, keep=False):
        if marg: file.write(' ' * (marg * 4))
        file.write('<' + node)
        for key, value in attrs.items():
            file.write(' %s="%s"' % (key, value))
        file.write(keep and '>' or '>\n')

    def write_close(node, marg=0):
        if marg: file.write(' ' * (marg * 4))
        file.write('</%s>\n' % node)

    def toxml(s):
        s = s.replace('&', '&amp;')
        s = s.replace('<', '&lt;')
        s = s.replace('>', '&gt;')
        return s

    # Main attributes
    attrs = content.get_attrs()

    if standalone and attrs.has_key('bg'):
        attrs = attrs.copy()
        imageids.append(attrs['bg'])
        attrs['bg'] = 'id://' + attrs['bg']

    write_open('presentation', attrs)

    # CSS (if any)
    if content.cssalias or content.cssclass:
        write_open('style', {}, 1)

        for key, val in content.cssalias.items():
            file.write('    %s {\n' % key)
            file.write(toxml(''.join(['      %s: %s;\n' % a for a in val.items()])))
            file.write('    }\n\n')

        for key, val in content.cssclass.items():
            file.write('    .%s {\n' % key)
            file.write(toxml(''.join(['      %s: %s;\n' % a for a in val.items()])))
            file.write('    }\n\n')

        write_close('style', 1)

    # Pages
    for page in content.pages():
        attrs = page.get_attrs()
        if standalone and attrs.has_key('bg'):
            attrs = attrs.copy()
            imageids.append(attrs['bg'])
            attrs['bg'] = 'id://' + attrs['bg']

        write_open('page', attrs, 1)

        # its items
        for group in page.groups():
            write_open('group', group.attrs, 2)
            for item in group.items():
                if standalone and item['type'] == 'image' \
                              and item['attrs'].has_key('src'):

                    a = item['attrs'].copy()
                    src = a['src']
                    a['src'] = 'id://' + src
                    imageids.append(src)

                    write_open('image', a, 3, True)
                    write_close('image')
                else:
                    write_open(item['type'], item['attrs'], 3, True)
                    file.write(toxml(unicode(item['content']).encode('utf8')))
                    write_close(item['type'])

            write_close('group', 2)

        write_close('page', 1)

    # Write images
    import base64
    done = []
    for img in imageids:
        if img in done:
            continue

        write_open('defimage', {'id': img}, 1)
        file.write(base64.encodestring(open(img).read()))
        write_close('defimage', 1)

    write_close('presentation')


