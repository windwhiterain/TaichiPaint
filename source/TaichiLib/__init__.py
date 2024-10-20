from dataclasses import dataclass, field
from typing import Callable, ClassVar, Optional
from taichi.lang.util import in_taichi_scope
import taichi as ti
import taichi.types as tt
import taichi.math as tm
Color = tt.vector(3, float)
VecI = tt.vector(2, int)
Vec = tt.vector(2, float)


@ti.pyfunc
def round_vec(_: Vec) -> VecI:
    if ti.static(in_taichi_scope()):
        return ti.round(_, int)
    else:
        return VecI(round(_.x), round(_.y))


@ti.pyfunc
def lerp(x: ti.template(), y: ti.template(), l: float):
    return x*(1-l)+y*l


@ti.dataclass
class Rect:
    l: Vec
    u: Vec

    @ti.pyfunc
    def size(self) -> Vec:
        return self.u-self.l

    @ti.pyfunc
    def center(self) -> Vec:
        return (self.l+self.u)/2

    @ti.pyfunc
    def scale(self, scale: float) -> 'Rect':
        center = self.center()
        size = self.size()
        return Rect(center-size*scale/2, center+size*scale/2)

    @ti.pyfunc
    def mul(self, other) -> 'Rect':
        size = self.size()
        return Rect(self.l+size*other.l, self.l+size*other.u)

    @ti.pyfunc
    def add(self, other) -> 'Rect':
        return other.move(self.l)

    @ti.pyfunc
    def mul_point(self, _: Vec):
        return _*self.size()+self.l

    @ti.pyfunc
    def div_point(self, _: Vec):
        return (_-self.l)/self.size()

    @ti.pyfunc
    def add_point(self, _: Vec):
        return _+self.l

    @ti.pyfunc
    def sub_point(self, _: Vec):
        return _-self.l

    @ti.pyfunc
    def move(self, _: Vec) -> 'Rect':
        return Rect(self.l+_, self.u+_)

    @ti.pyfunc
    def set_center(self, _: Vec) -> 'Rect':
        return self.move(_-self.center())

    @ti.pyfunc
    def origin(self) -> 'Rect':
        return Rect(Vec(0), self.size())

    @ti.pyfunc
    def intersect(self, other) -> 'Rect':
        return Rect(ti.max(self.l, other.l), ti.min(self.u, other.u))

    @ti.pyfunc
    def I(self) -> 'RectI':
        return RectI(round_vec(self.l), round_vec(self.u))


@ti.pyfunc
def Rect_center_size(center: Vec, size: Vec) -> Rect:
    return Rect(center-size/2, center+size/2)


Rect.center_size = Rect_center_size


Rect.full = Rect(Vec(0), Vec(1))


@ti.dataclass
class RectI:
    l: VecI
    u: VecI

    @ti.pyfunc
    def size(self) -> VecI:
        return self.u-self.l

    @ti.pyfunc
    def inside(self, _: VecI) -> bool:
        return (_ >= self.l).all() and (_ < self.u).all()

    @ti.pyfunc
    def mul(self, other: Rect) -> 'RectI':
        size = self.size()
        return RectI(self.l+round_vec(size*other.l), self.l+round_vec(size*other.u))

    @ti.pyfunc
    def div_point(self, _: VecI) -> Vec:
        return (Vec(_-self.l)+Vec(0.5))/self.size()

    @ti.pyfunc
    def mul_point(self, _: Vec) -> VecI:
        return round_vec((_*self.size())-Vec(0.5))+self.l

    @ti.pyfunc
    def sub_point(self, _: VecI) -> Vec:
        return Vec(_-self.l)+Vec(0.5)

    @ti.pyfunc
    def add_point(self, _: Vec) -> VecI:
        return round_vec(_-Vec(0.5))+self.l

    @ti.func
    def range(self):
        return ((self.l.x, self.u.x), (self.l.y, self.u.y))

    @ti.pyfunc
    def div(self, other) -> Rect:
        size = self.size()
        return Rect(Vec(other.l)/size, Vec(other.u)/size)

    @ti.pyfunc
    def intersect(self, other) -> 'RectI':
        return RectI(ti.max(self.l, other.l), ti.min(self.u, other.u))

    @ti.pyfunc
    def F(self) -> Rect:
        return Rect(self.l, self.u)


@ti.pyfunc
def RectI_full(size: VecI) -> 'RectI':
    return RectI(VecI(0), size)


RectI.full = RectI_full
