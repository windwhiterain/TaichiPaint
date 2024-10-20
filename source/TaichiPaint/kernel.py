from TaichiLib import *
from .common import Texture


@ti.kernel
def _fill(canvas: ti.template(), rect: RectI, value: ti.template()):
    rect_full = RectI.full(VecI(canvas.shape))
    rect_active = rect.intersect(rect_full)
    for i, j in ti.ndrange(*rect_active.range()):
        canvas[i, j] = value


def fill(canvas: Texture, value):
    _fill(canvas.resource, canvas.rect_resource.I(), value)


@ti.kernel
def _sample(canvas: ti.template(), rect: RectI, texture_sample: ti.template(), rect_sample: RectI):
    rect_full = RectI.full(VecI(canvas.shape))
    rect_active = rect.intersect(rect_full)
    for i, j in ti.ndrange(*rect_active.range()):
        inside = rect.div_point(VecI(i, j))
        outside = rect_sample.mul_point(inside)
        canvas[i, j] = texture_sample[outside]


def sample(canvas: Texture, texture_sample: Texture):
    _sample(canvas.resource, canvas.rect_resource.I(),
            texture_sample.resource, texture_sample.rect_resource.I())


@ti.kernel
def _draw_texture(canvas: ti.template(), rect: RectI, texture_pattern: ti.template(), rect_sample: RectI, color: Color, alpha: float):
    rect_full = RectI.full(VecI(canvas.shape))
    rect_active = rect.intersect(rect_full)
    for i, j in ti.ndrange(*rect_active.range()):
        inside = rect.div_point(VecI(i, j))
        outside = rect_sample.mul_point(inside)
        _alpha = texture_pattern[outside]*alpha
        if _alpha > 0:
            canvas[i, j] = lerp(canvas[i, j], color, _alpha)


def draw_texture(canvas: Texture, texture_sample: Texture, color: Color, alpha: float):
    _draw_texture(canvas.resource, canvas.rect_resource.I(), texture_sample.resource,
                  texture_sample.rect_resource.I(), color, alpha)


@ti.kernel
def _draw_function(canvas: ti.template(), rect: RectI, function: ti.template(), color: Color, alpha: float):
    rect_full = RectI.full(VecI(canvas.shape))
    rect_active = rect.intersect(rect_full)
    for i, j in ti.ndrange(*rect_active.range()):
        parameter = rect.div_point(VecI(i, j))
        _alpha = function(parameter)*alpha
        if _alpha > 0:
            canvas[i, j] = lerp(canvas[i, j], color, _alpha)


def draw_function(canvas: Texture, function: Callable[[Vec], float], color: Color, alpha: float):
    _draw_function(canvas.resource, canvas.rect_resource.I(),
                   function, color, alpha)


@ti.kernel
def _draw_functions(canvas: ti.template(), rect: RectI, function: ti.template(), offsets: ti.template(), num: int, value: ti.template(), alpha: float):
    rect_full = RectI.full(VecI(canvas.shape))
    for i, j, k in ti.ndrange((0, num), *rect.range()):
        parameter = rect.div_point(VecI(j, k))
        offset = round_vec(offsets[i])
        idx = offset+VecI(j, k)
        _alpha = function(parameter)*alpha
        if rect_full.inside(idx) and _alpha > 0:
            canvas[idx] = lerp(canvas[idx], value, _alpha)


def draw_functions(canvas: Texture, function: Callable[[Vec], float], offsets: ti.Field, num: int, value, alpha: float):
    _draw_functions(canvas.resource, canvas.rect_resource.I(),
                    function, offsets, num, value, alpha)


@ti.kernel
def _max_functions(canvas: ti.template(), rect: RectI, function: ti.template(), offsets: ti.template(), num: int, alpha: float):
    rect_full = RectI.full(VecI(canvas.shape))
    for i, j, k in ti.ndrange((0, num), *rect.range()):
        parameter = rect.div_point(VecI(j, k))
        offset = round_vec(offsets[i])
        idx = offset+VecI(j, k)
        _alpha = function(parameter)*alpha
        if rect_full.inside(idx) and _alpha > 0:
            ti.atomic_max(canvas[idx], function(parameter)*alpha)


def max_functions(canvas: Texture, function: Callable[[Vec], float], offsets: ti.Field, num: int, alpha: float):
    _max_functions(canvas.resource, canvas.rect_resource.I(),
                   function, offsets, num, alpha)


@ti.kernel
def _mul_functions(canvas: ti.template(), rect: RectI, function: ti.template(), offsets: ti.template(), num: int, overlap_num: int, alpha: float):
    rect_full = RectI.full(VecI(canvas.shape))
    for o, i, j, k in ti.ndrange((0, overlap_num), tm.ceil(num/overlap_num, int), *rect.range()):
        if o+i*overlap_num < num:
            parameter = rect.div_point(VecI(j, k))
            offset = round_vec(offsets[o, i])
            idx = offset+VecI(j, k)
            _alpha = function(parameter)*alpha
            if rect_full.inside(idx) and _alpha > 0:
                ti.atomic_mul(canvas[idx], 1 - function(parameter)*alpha)


def mul_functions(canvas: Texture, function: Callable[[Vec], float], offsets: ti.Field, num: int, overlap_num: int, alpha: float):
    _mul_functions(canvas.resource, canvas.rect_resource.I(),
                   function, offsets, num, overlap_num, alpha)


@ti.kernel
def _colorize(canvas: ti.template(), rect: RectI, alpha_inv: ti.template(), alpha_rect: RectI, value: ti.template()):
    for idx in ti.grouped(ti.ndrange(*rect.range())):
        parameter = rect.div_point(idx)
        alpha_idx = alpha_rect.mul_point(parameter)
        prev = canvas[idx]
        canvas[idx] = lerp(
            prev, value, 1-alpha_inv[alpha_idx])


def colorize(canvas: Texture, alpha: Texture, value):
    _colorize(canvas.resource, canvas.rect_resource.I(),
              alpha.resource, alpha.rect_resource.I(), value)
