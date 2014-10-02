/*
 * 
 * Copyright (C) 2004 Ayose Cazorla León
 * 
 * Authors
 *       Ayose Cazorla <ayose.cazorla@hispalinux.es>
 * 
 * This file is part of Pyslide.
 * 
 * Pyslide is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * Pyslide is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with Pyslide; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#define NO_PYGAME_C_API
#include <pygame/pygame.h>

enum Continue { ITER_STOP, ITER_AGAIN };

enum EffectType { ET_FULL, ET_HOR, ET_VER, ET_RAD };
enum Direction { DIRECTION_POS, DIRECTION_NEG };

struct _AE;
typedef int (*iter_function)(struct _AE*);

struct _AE{
    PyObject_HEAD

    double total_time;
    double start;

    int last_value;
    int hide;

    PyObject* py_source;
    PyObject* py_dest;

    SDL_Surface* source;
    SDL_Surface* dest;

    int src_offset;
    int dst_offset;

    enum Direction direction;
    enum EffectType type;

    iter_function do_iteration;
};

typedef struct _AE AlphaEffect_object;

iter_function getiterator(int type);

/* 
 * Methods for iteration 
 */

int iter_full_value (AlphaEffect_object*);
int iter_full_pixel (AlphaEffect_object*);
int iter_hor (AlphaEffect_object*);
int iter_ver(AlphaEffect_object*);
int iter_rad(AlphaEffect_object*);


/*
 * Methods for change state
 */
PyObject* aemethod_setstate(AlphaEffect_object* self, PyObject* args);
PyObject* aemethod_getstate(AlphaEffect_object* self);

