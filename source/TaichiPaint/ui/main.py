from enum import Enum
from TaichiLib import *
from TaichiPaint import common
from .. import kernel
from . import event
from . import block 




@ti.data_oriented
@dataclass
class UI:
    root:block.Block
    name:str="Taichi Paint"
    size:tuple[int,int]=(640,460)
    def __post_init__(self):
        self.root.rect_scale=Rect.full
        self.mouse_event_manager=event.MouseEventManager(self)
    def run(self):
        self.window = ti.ui.Window(name=self.name, res = self.size, fps_limit=200, pos = (150, 150))
        self.canvas_screen=common.Texture(ti.field(dtype=Color,shape=self.size))
        self.canvas_screen_event=common.Texture(ti.field(dtype=int,shape=self.size))

        self.canvas_screen_event.resource.fill(event.ScreenEventManager.invalid_id)
        self.root.paint(block.DrawContext(self.canvas_screen,self.canvas_screen_event))

        while self.window.running:

            size_new=self.window.get_window_shape()
            if size_new!=self.size:
                self.canvas_screen=common.Texture(ti.field(Color,size_new))
                self.canvas_screen_event=common.Texture(ti.field(int,size_new))
                print(f"change screen size to: {size_new}")
            self.size=size_new


            self.mouse_event_manager.update()

            self.canvas_screen_event.resource.fill(event.ScreenEventManager.invalid_id)
            self.root.paint(block.DrawContext(self.canvas_screen,self.canvas_screen_event))

            canvas = self.window.get_canvas()
            canvas.set_image(self.canvas_screen.resource)
            self.window.show()


