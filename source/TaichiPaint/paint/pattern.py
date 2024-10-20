from TaichiLib import *
from TaichiPaint import common


class Pattern:
    pass


@dataclass
class Texture(Pattern):
    texture: common.Texture


class Function(Pattern):
    def sample(self, parameter: Vec) -> float: pass


@ti.data_oriented
@dataclass
class Sphere(Function):
    power = 2

    @ti.func
    def sample(self, parameter: Vec) -> float:
        return tm.max(0, 1-tm.pow((parameter-Vec(0.5)).norm()*2, self.power))
