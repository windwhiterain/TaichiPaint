from TaichiLib import *
from .. import kernel
from ..ui import block
from ..ui import event
from .. import common
from . import brush


@ti.data_oriented
@dataclass
class Paint:
    canvas: common.Texture
    brush: brush.Brush

    def __post_init__(self):
        self.alpha_inv = common.Texture(
            ti.field(float, self.canvas.rect().I().size()))
        self.alpha_inv.resource.fill(1)
        self.block = block.ColorBlock(Color(1, 1, 1)).block
        self.canvas_block = block.Texture(self.canvas).block
        self.canvas_block.rect_scale = Rect.full
        self.block.children.append(self.canvas_block)
        self.block.event_id = event.screen_event_manager.add(self.canvas_block, event.MouseEventActionTable(
            button=event.MouseButton.LMB, click=self.stroke_click, drag=self.stroke_drag))

    def transform(self, _: Vec) -> Vec:
        return self.canvas.rect().mul_point(self.canvas_block.canvas.rect().div_point(_))

    def stroke_click(self, position: Vec):
        if self.brush is not None:
            position = self.transform(position)
            self.brush.stroke_click(
                brush.PaintContext(color=self.canvas, alpha_inv=self.alpha_inv), position)

    def stroke_drag(self, start_position: Vec, end_position: Vec):
        if self.brush is not None:
            start_position = self.transform(start_position)
            end_position = self.transform(end_position)
            self.brush.stroke_drag(brush.PaintContext(
                color=self.canvas, alpha_inv=self.alpha_inv), start_position, end_position)
