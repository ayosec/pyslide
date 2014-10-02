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
#include <sys/time.h>
#include <unistd.h>

static double 
gettime(void)
{
    struct timeval tv;
    gettimeofday(&tv, NULL);

    return tv.tv_sec + tv.tv_usec / 1000000.;
}


int iter_full_value (AlphaEffect_object* self)
{
    Uint8 newalpha;

    if (self->start > 0) {
        double delta;
        delta = gettime() - self->start;

        if (delta >= self->total_time) {
            SDL_SetAlpha(self->dest, SDL_SRCALPHA, self->hide ? 0 : 255);
            return ITER_STOP;
        }

        newalpha = (Uint8)((delta * 255.) / self->total_time);
        if (self->hide)
            newalpha = 255 - newalpha;

    } else {
        self->start = gettime();
        newalpha = self->hide ? 255 : 0;
    }

    self->last_value = newalpha;
    SDL_SetAlpha(self->dest, SDL_SRCALPHA, newalpha);
    return ITER_AGAIN;
}


int iter_full_pixel (AlphaEffect_object* self)
{
    int x, len, offset;
    Uint8 *srcpixels, *dstpixels;
    double alpha, delta;

    delta = gettime() - self->start;
    if (self->start > 0 && delta > self->total_time)
        return ITER_STOP;

    SDL_LockSurface(self->source);
    SDL_LockSurface(self->dest);

    dstpixels = (Uint8*)self->dest->pixels;
    srcpixels = (Uint8*)self->source->pixels;
    len = self->dest->w * self->dest->h * 4;

    if (self->start > 0) {
        alpha = delta / self->total_time;
        if (self->hide)
            alpha = 1. - alpha;

        offset = self->src_offset - self->dst_offset;
        for (x = self->dst_offset; x < len; x += 4)
            dstpixels[x] = (Uint8)(srcpixels[x + offset] * alpha);
    } else {
        if (!self->hide)
            for (x = self->dst_offset; x < len; x += 4)
                dstpixels[x] = 0;
        self->start = gettime();
    }


    SDL_UnlockSurface(self->source);
    SDL_UnlockSurface(self->dest);
    return ITER_AGAIN;
}

int iter_hor (AlphaEffect_object* self)
{
    int rowstride, offset, x, retval;
    double delta, alpha;
    Uint8 *dstpixels, *srcpixels;

    retval = ITER_AGAIN;

    SDL_LockSurface(self->source);
    SDL_LockSurface(self->dest);

    dstpixels = (Uint8*)self->dest->pixels;
    srcpixels = (Uint8*)self->source->pixels;
    rowstride = self->dest->w * 4;

    offset = self->src_offset < 0 ? -1 :self->src_offset - self->dst_offset;

    if (self->start > 0) {

        Uint8 *dstrow, *srcrow;
        int newx, top, bottom, y;

        delta = gettime() - self->start;
        if (delta < self->total_time) {
            newx = (self->dest->w + 100) * delta / self->total_time;
        } else {
            retval = ITER_STOP;
            newx = self->dest->w + 100;
        }

        /* Update the "complete" zone */
        if (self->direction == DIRECTION_POS) {
            bottom = max(0, self->last_value - 100);
            top = min(newx - 100, self->dest->w);
        } else {
            newx = self->dest->w - newx;
            bottom = min(newx + 100, self->dest->w);
            top = min(self->last_value + 100, self->dest->w);
        }

        top *= 4;
        for (x = bottom * 4 + self->dst_offset; x < top; x+=4) {
            dstrow = dstpixels;
            srcrow = srcpixels;

            for (y = 0; y < self->dest->h; y++) {
                dstrow[x] = self->hide ? 0 : (offset == -1 ? 255 : srcrow[x + offset]);

                dstrow += rowstride;
                srcrow += rowstride;
            }
        }

        /*
         * shadow.. 
         */
        if (self->direction == DIRECTION_POS) {
            top = min(self->dest->w, newx);
            bottom = newx - 100;
        } else {
            top = min(self->dest->w, newx + 100);
            bottom = min(self->dest->w, newx);
        }

        for (x = max(0, bottom) + self->dst_offset; x < top; x++) {
            int of = x * 4;

            if (self->direction == DIRECTION_POS)
                alpha = (newx - x) / 100.;
            else
                alpha = (x - newx) / 100.;

            if (self->hide)
                alpha = 1. - alpha;

            dstrow = dstpixels + self->dst_offset;
            if (offset == -1) {
                Uint8 val = alpha * 255;
                for (y = 0; y < self->dest->h; y++) {
                    dstrow[of] = val;
                    dstrow += rowstride;
                }
            } else {
                srcrow = srcpixels + self->dst_offset;
                for (y = 0; y < self->dest->h; y++)
                {
                    dstrow[of] = (Uint8)(srcrow[of + offset] * alpha);
                    dstrow += rowstride;
                    srcrow += rowstride;
                }
            }
        }

        self->last_value = top;

    } else {

        /* First iteration */

        if (!self->hide)
        {
            int len = self->dest->w * self->dest->h * 4;
            for (x = self->dst_offset; x < len; x += 4)
                dstpixels[x] = 0;
        }

        self->start = gettime();
        self->last_value = self->direction == DIRECTION_POS ? 0 : self->dest->w;
    }

    SDL_UnlockSurface(self->source);
    SDL_UnlockSurface(self->dest);
    return retval;
}


int iter_ver(AlphaEffect_object* self)
{
    int rowstride, offset, x;
    double delta, alpha;
    int retval = ITER_AGAIN;

    Uint8 *dstpixels, *srcpixels;

    SDL_LockSurface(self->source);
    SDL_LockSurface(self->dest);

    dstpixels = (Uint8*)self->dest->pixels;
    srcpixels = (Uint8*)self->source->pixels;
    rowstride = self->dest->w * 4;

    offset = self->src_offset < 0 ? -1 :self->src_offset - self->dst_offset;

    if (self->start > 0) {
        Uint8 *dstrow, *srcrow;
        int y, newy, top, bottom;

        delta = gettime() - self->start;

        if (delta < self->total_time) {
            newy = (self->dest->h + 100) * delta / self->total_time;
        } else {
            retval = ITER_STOP;
            newy = self->dest->h + 100;
        }

        /* Update the "complete" zone */
        if (self->direction == DIRECTION_POS) {
            bottom = max(0, self->last_value - 100);
            top = min(newy - 100, self->dest->h);
        } else {
            newy = self->dest->h - newy;
            bottom = min(newy + 100, self->dest->h);
            top = min(self->last_value + 100, self->dest->h);
        }

        for (y = bottom; y < top; y++) {

            dstrow = dstpixels + rowstride * y;
            srcrow = srcpixels + rowstride * y;

            for (x = self->dst_offset; x < rowstride; x += 4)
                dstrow[x] = self->hide ? 0 : (offset == -1 ? 255 : srcrow[x + offset]);
        }

        /*
         * shadow.. 
         */

        if (self->direction == DIRECTION_POS) {
            top = min(self->dest->h, newy);
            bottom = newy - 100;
        } else {
            top = min(self->dest->h, newy + 100);
            bottom = min(self->dest->h, newy);
        }


        for (y = max(0, bottom); y < top; y++) {
            dstrow = dstpixels + (rowstride * y);
            srcrow = srcpixels + (rowstride * y);

            if (self->direction == DIRECTION_POS)
                alpha = (newy - y) / 100.;
            else
                alpha = (y - newy) / 100.;

            if (self->hide)
                alpha = 1. - alpha;

            if (offset == -1) {
                Uint8 val = alpha * 255;
                for (x = self->src_offset; x < rowstride; x += 4)
                    dstrow[x] = val;
            } else
                for (x = self->src_offset; x < rowstride; x += 4)
                    dstrow[x] = (Uint8)(srcrow[x + offset] * alpha);
        }

        self->last_value = top;

    } else {

        /* First iteration */

        if (!self->hide)
        {
            int len = self->dest->w * self->dest->h * 4;
            for (x = self->dst_offset; x < len; x += 4)
                dstpixels[x] = 0;
        }

        self->start = gettime();
        self->last_value = self->direction == DIRECTION_POS ? 0 : self->dest->h;
    }

    SDL_UnlockSurface(self->source);
    SDL_UnlockSurface(self->dest);
    return retval;
}

int iter_rad(AlphaEffect_object* self)
{
    PyErr_SetString(PyExc_NotImplementedError, "not yet");
    return -1;
}




/*
 * Methods for change state
 */


PyObject* aemethod_setstate(AlphaEffect_object* self, PyObject* args)
{
    PyObject* tuple;
    int last_value, hide, direction, type;

    /* TODO: update everything.
     *
     * At this moment, only an ET_FULL effect is changed in this
     * method. 
     */

    if(!PyArg_ParseTuple(args, "O!", &PyTuple_Type, &tuple))
        return NULL;

    if(!PyArg_ParseTuple(tuple, "iiii", &last_value, &hide, &direction, &type))
        return NULL;

    if (self->type == ET_FULL && type == ET_FULL)
        self->start = gettime() - (last_value * self->total_time / 255.);

    Py_INCREF(Py_None);
    return Py_None;
}

PyObject* aemethod_getstate(AlphaEffect_object* self)
{
    return Py_BuildValue("(iiii)",
            self->last_value,
            self->hide,
            self->direction,
            self->type);
}
