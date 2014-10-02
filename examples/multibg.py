#!/usr/bin/python
# -*- coding: latin1 -*-

# (HACK) the Main 
class Main:
    fullscreen = True
    start_page = 0

def best_size():
    import sys
    if len(sys.argv) == 2:
        return sys.argv[1]
    else:
        import pygame.display
        if not pygame.display.get_init():
            pygame.display.init()

        r = pygame.display.list_modes()
        if r == -1:
            size = '800x600'
        else:
            size = '%dx%d' % r[0]

        return size

def main():
    PYSLIDE_PATH = '..'

    import sys
    if PYSLIDE_PATH not in sys.path:
        sys.path.append(PYSLIDE_PATH)

    from Pyslide import Presentation
    from Pyslide import Content

    c = Content.Content()
    Main.size = best_size()

    # Pages
    for bg in range(40):
        p = c.add_page({
                'bgcolor': '200,%d,%d' % (bg*5, bg*5),
                'ttl': '0'})
        g = p.add_group()

        g.add_item({
            'content': 'Another useless example ;-)', 'type': 
            'text', 'attrs': 
            {'align': 'center', 'interspace': '20', 'y': str(bg*2)}})

        g.add_item({
            'content': 'This shows how you can create your'
                    ' presentations directly in python', 'type': 
            'text', 'attrs': 
            {'align': 'center', 'interspace': '20'}})

    #Run presentation
    bp = Presentation.BuildPresentation(c, Main)
    bp.run()

if __name__ == '__main__':
    main()

