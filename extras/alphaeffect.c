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

#include "alphaeffect.h"

static int 
alphaoffset(SDL_Surface* surface)
{
    int offset;

    if(surface->format->BytesPerPixel != 4)
        return -1;

    if(surface->format->Amask == 0xff<<24)
        offset = SDL_BYTEORDER == SDL_LIL_ENDIAN ? 3 : 0;
    else if(surface->format->Amask == 0xff)
        offset = SDL_BYTEORDER == SDL_LIL_ENDIAN ? 0 : 3;
    else
        offset = -1;

    return offset;
}

/*
 *     _alphaeffect
 */

static PyObject* Pygame_SurfaceType;
static PyObject* AlphaEffect_Error;

/*
 * module methods
 */


static PyObject *
module_setalpha(PyObject *self, PyObject *args)
{
    SDL_Surface* surface;
    PyObject *source, *newsurface;
    Uint8 *pixels;
    int len, x, offset, alpha;
    double mult;

    if(!PyArg_ParseTuple(args, "O!i", Pygame_SurfaceType, &source, &alpha))
        return NULL;

    if (alpha < 0 || alpha > 255)
        return RAISE(PyExc_ValueError, "Alpha value has to be between 0 and 255");

    /* Get a new surface. We don't want change the original surface */
    if((newsurface = PyObject_CallMethod(source, "convert_alpha", NULL)) == NULL)
        return NULL;

    surface = PySurface_AsSurface(newsurface);

    /* the alpha mask */
    if(surface->format->Amask == 0xff<<24)
        offset = SDL_BYTEORDER == SDL_LIL_ENDIAN ? 3 : 0;
    else if(surface->format->Amask == 0xff)
        offset = SDL_BYTEORDER == SDL_LIL_ENDIAN ? 0 : 3;
    else {
        Py_DECREF(newsurface);
        return RAISE(PyExc_ValueError, "unsupport colormasks for alpha reference array");
    }

    /* Transform it!! */
    SDL_LockSurface(surface);

    pixels = (Uint8*)surface->pixels;
    len = surface->w * surface->h * 4;
    mult = alpha / 255.;
    for (x = offset; x < len; x += 4)
        pixels[x] = (Uint8)(pixels[x] * mult);

    SDL_UnlockSurface(surface);
    return newsurface;
}


/*
 * AlphaEffect method
 */

static PyObject*
aemethod_iter(AlphaEffect_object* self)
{
    int ret;
    ret = self->do_iteration(self);

    if (ret == -1 && PyErr_Occurred() != NULL)
        return NULL;

    return PyInt_FromLong(ret);
}

static PyObject*
aemethod_start(AlphaEffect_object* self)
{
    SDL_Rect rect;

    if (self->source != self->dest) {
        /* First, copy the image */
        rect.x = rect.y = 0;
        SDL_BlitSurface(self->source, &rect, self->dest, NULL);
    }

    Py_INCREF(self->py_dest);
    return self->py_dest;
}

static int
aemethod_init(AlphaEffect_object *self, PyObject *args, PyObject *kwds)
{
    double time;
    int hide;
    enum Direction direction;
    enum EffectType type;
    PyObject *source;

    static char *kwlist[] = {"time", "source", "type", "direction", "hide", NULL};

    if (! PyArg_ParseTupleAndKeywords(args, kwds, "dO!iii", kwlist, 
                                      &time, 
                                      Pygame_SurfaceType, &source,
                                      &type, &direction, &hide))
        return -1;

    self->total_time = time;
    self->start = 0;
    self->last_value = 0;

    self->hide = hide;
    self->direction = direction;
    self->type = type;

    /*
     * Surface info 
     */
    self->source = PySurface_AsSurface(source);
    Py_INCREF(self->py_source = source);

    if (self->source->format->Amask == 0 && type == ET_FULL) {
        self->do_iteration = iter_full_value;
        self->dest = self->source;
        self->py_source = self->py_dest = source;

        Py_INCREF(source);

    } else {
        /* select the iter function */
        switch (type) {
            case ET_FULL:
                self->do_iteration = iter_full_pixel;
                break;

            case ET_VER:
                self->do_iteration = iter_ver;
                break;

            case ET_HOR:
                self->do_iteration = iter_hor;
                break;

            case ET_RAD:
                self->do_iteration = iter_rad;
                break;

            default:
                PyErr_Format(PyExc_NotImplementedError, "Unknown value: %d", type);
                return -1;
        }

        /* Create a new surface. Because of I can't create a 
         * pygame.Surface object here, I have to call the 
         * convert_alpha method from the object
         */
        self->py_dest = PyObject_CallMethod(source, "convert_alpha", NULL);

        if (self->py_dest == NULL)
            return -1;

        self->dest = PySurface_AsSurface(self->py_dest);

        self->src_offset = alphaoffset(self->source);
        self->dst_offset = alphaoffset(self->dest);

    }

    return 0;
}

static void
aemethod_dealloc(AlphaEffect_object* self)
{
    Py_XDECREF(self->py_source);
    Py_XDECREF(self->py_dest);

    self->ob_type->tp_free(self);
}

/* 
 * Type defintion
 */

static PyMethodDef aetype_methods[] = {
    {"iter", (PyCFunction)aemethod_iter, METH_NOARGS, "iter()"},
    {"start", (PyCFunction)aemethod_start, METH_NOARGS, "start(...)"},
    {"getstate", (PyCFunction)aemethod_getstate, METH_NOARGS, "getstate()"},
    {"setstate", (PyCFunction)aemethod_setstate, METH_VARARGS, "setstate(...)"},
    {NULL}
};

static PyTypeObject alphaeffect_type = {
    PyObject_HEAD_INIT(NULL)
    0,                             /*ob_size*/
    "_alphaeffect.AlphaEffect",    /*tp_name*/
    sizeof(AlphaEffect_object),    /*tp_basicsize*/
    0,                             /*tp_itemsize*/
    (destructor)aemethod_dealloc,  /*tp_dealloc*/
    0,                             /*tp_print*/
    0,                             /*tp_getattr*/
    0,                             /*tp_setattr*/
    0,                             /*tp_compare*/
    0,                             /*tp_repr*/
    0,                             /*tp_as_number*/
    0,                             /*tp_as_sequence*/
    0,                             /*tp_as_mapping*/
    0,                             /*tp_hash */
    0,                             /*tp_call*/
    0,                             /*tp_str*/
    0,                             /*tp_getattro*/
    0,                             /*tp_setattro*/
    0,                             /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,            /*tp_flags*/
    "AlphaEffect object",          /* tp_doc */
    0,                             /* tp_traverse */
    0,                             /* tp_clear */
    0,                             /* tp_richcompare */
    0,                             /* tp_weaklistoffset */
    0,                             /* tp_iter */
    0,                             /* tp_iternext */
    aetype_methods,                /* tp_methods */
    0,                             /* tp_members */
    0,                             /* tp_getset */
    0,                             /* tp_base */
    0,                             /* tp_dict */
    0,                             /* tp_descr_get */
    0,                             /* tp_descr_set */
    0,                             /* tp_dictoffset */
    (initproc)aemethod_init,       /* tp_init */
};

/*
 * Module definition
 */

static PyMethodDef module_methodlist[] = {
    {"setalpha",  module_setalpha, METH_VARARGS, ""},
    {NULL, NULL, 0, NULL}
};



void init_alphaeffect(void)
{
    PyObject *pygame_surface;
    PyObject *dict;
    PyObject *module;

    if ((module = Py_InitModule("_alphaeffect", module_methodlist)) == NULL)
        return;

    alphaeffect_type.tp_new = PyType_GenericNew;
    if (PyType_Ready(&alphaeffect_type) < 0)
        return;

    /* I need the pygame.surface.Surface type
     */

    if((pygame_surface = PyImport_ImportModule("pygame.surface")) == NULL)
        return;

    dict = PyModule_GetDict(pygame_surface);
    if((Pygame_SurfaceType = PyDict_GetItemString(dict, "Surface")) == NULL) {
        RAISE(PyExc_AttributeError, "pygame.surface module has no attribute 'Surface'");
        return;
    }

    Py_INCREF(Pygame_SurfaceType);
    Py_DECREF(pygame_surface);

    /* Add module objects 
     */
    AlphaEffect_Error = PyErr_NewException("_alphaeffect.Error", NULL, NULL);

    PyModule_AddObject(module, "AlphaEffect", (PyObject *)&alphaeffect_type);
    PyModule_AddObject(module, "Error", AlphaEffect_Error);

#define ADD_INT(n) if(PyModule_AddIntConstant(module, #n, n) != 0) return
    ADD_INT(ET_FULL);
    ADD_INT(ET_HOR);
    ADD_INT(ET_VER);
    ADD_INT(ET_RAD);
    ADD_INT(DIRECTION_POS);
    ADD_INT(DIRECTION_NEG);
    ADD_INT(ITER_STOP);
    ADD_INT(ITER_AGAIN);
}

