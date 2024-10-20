from TaichiLib import *
from .. import kernel
from . import event 
from .. import common

@dataclass
class OnDrawContext:
    canvas:common.Texture

@dataclass
class DrawContext:
    canvas:common.Texture
    canvas_event:common.Texture


@ti.data_oriented
@dataclass
class Block:
    delegate_draw:Callable[[OnDrawContext],None]=lambda _:None
    rect_scale:Rect=None
    children:list['Block']=field(default_factory=lambda:[])
    event_id:Optional[int]=None
    def paint(self,context:DrawContext):
        self.canvas=context.canvas.mul(self.rect_scale)
        self.canvas_event=context.canvas_event.mul(self.rect_scale)
        self.delegate_draw(OnDrawContext(self.canvas))
        if self.event_id is not None:
            kernel.fill(self.canvas_event,self.event_id)
        for child in self.children:
            child.paint(DrawContext(self.canvas,self.canvas_event))
    def __del__(self):
        if self.event_id is not None and event.screen_event_manager is not None:
            event.screen_event_manager.remove(self.event_id)

@dataclass
class ColorBlock:
    color:Color
    def __post_init__(self):
        self.block=Block(delegate_draw=self.fill)
    def fill(self,context:OnDrawContext):
        kernel.fill(context.canvas,self.color)

@dataclass
class Horizontal:
    blocks:list[Block]
    partition:list[float]
    def __post_init__(self):
        self.block=Block(children=self.blocks)
        for i in range(len(self.blocks)):
            l=0 if i-1<0 else self.partition[i-1]
            u=1 if i>=len(self.partition) else self.partition[i]
            self.blocks[i].rect_scale=Rect(Vec(l,0),Vec(u,1))

@dataclass
class Texture:
    texture:common.Texture
    def __post_init__(self):
        self.block=Block(delegate_draw=self.sample)
    def sample(self,context:OnDrawContext):
        kernel.sample(context.canvas,self.texture)

