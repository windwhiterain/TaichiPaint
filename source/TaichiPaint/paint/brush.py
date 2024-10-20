from math import ceil
from TaichiLib import *
from .. import kernel
from .. import common
from . import pattern


@dataclass
class PaintContext:
    color: common.Texture
    alpha_inv: common.Texture


class Brush:
    def stroke_click(self, context: PaintContext, position: Vec): pass
    def stroke_drag(self, context: PaintContext,
                    start_position: Vec, end_position: Vec): pass


@dataclass
class Stamp(Brush):
    pattern: pattern.Pattern
    color: Color = Color(0, 0, 0)
    alpha: float = 1
    size: float = 1
    length_per_stroke: float = 1

    def __post_init__(self):
        self.prev_length = 0
        self.positions = ti.field(Vec, (8, 64))
        self.num_position = 0

    def stroke_click(self, context: PaintContext, position: Vec):
        # global space: context.texture.resource
        match self.pattern:
            case pattern.Texture(texture):
                kernel.draw_texture(context.color.add(Rect.center_size(
                    position, self.size)),
                    texture, self.color, self.alpha)
            case pattern.Function():
                kernel.draw_function(context.color.add(Rect.center_size(
                    position, self.size)), self.pattern.sample, self.color, self.alpha)

    def stroke_drag(self, context: PaintContext, start_position: Vec, end_position: Vec):
        target_length = (end_position-start_position).norm()
        length = 0
        self.stroke_per_size = tm.max(
            1, tm.min(self.positions.shape[0], ceil(self.size/self.length_per_stroke)))
        while True:
            delta_length = self.length_per_stroke-self.prev_length
            if delta_length <= target_length-length:
                length += delta_length
                self.prev_length = 0
                self.positions[self.num_position % self.stroke_per_size, self.num_position // self.stroke_per_size] = lerp(
                    start_position, end_position, length/target_length)
                self.num_position += 1
                if self.num_position >= self.stroke_per_size*self.positions.shape[1]:
                    self.stroke_positions(context)
            else:
                self.prev_length += target_length-length
                break
        self.stroke_positions(context)
        kernel.colorize(context.color, context.alpha_inv, self.color)
        context.alpha_inv.resource.fill(1)

    def stroke_positions(self, context: PaintContext):
        if self.num_position > 0:
            match self.pattern:
                case pattern.Function():
                    kernel.mul_functions(context.alpha_inv.add(Rect.center_size(Vec(0), Vec(
                        self.size))), self.pattern.sample, self.positions, self.num_position, self.stroke_per_size, self.alpha)
            self.num_position = 0
