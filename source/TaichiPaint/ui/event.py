from TaichiLib import *
from enum import Enum
from . import block
from . import main

class MouseButton(Enum):
    LMB=0
    RMB=1
    MMB=2

class MouseEventType(Enum):
    Click=0
    Drag=1

class Event:
    pass

@dataclass
class MouseEvent(Event):
    type:MouseEventType
    button:MouseButton

@dataclass
class MouseEventActionTable:
    button:MouseButton
    click:Callable[[Vec],None]|None=None
    drag:Callable[[Vec,Vec],None]|None=None

@dataclass
class ScreenEventManager:
    @dataclass
    class Register:
        block:block.Block
        action:MouseEventActionTable
    invalid_id:ClassVar[int]=-1
    next_id:int=0
    registers:dict[int,Register]=field(default_factory=lambda:{})
    def add(self,block:block.Block,action:MouseEventActionTable)->int:
        id=self.next_id
        self.next_id+=1
        self.registers[id]=self.Register(block,action)
        return id
    def remove(self,id:int):
        self.registers.pop(id)

screen_event_manager=ScreenEventManager()

@dataclass
class MouseEventManager:
    @dataclass 
    class ButtonEventManager:
        get_is_down:Callable[[],bool]
        is_down:bool=False
        def update(self,delta_position:Vec) -> MouseEventType|None:
            ret=None
            is_down_new=self.get_is_down()
            if is_down_new:
                if not self.is_down:
                    ret=MouseEventType.Click
                elif (delta_position!=0).any():
                    ret=MouseEventType.Drag
            self.is_down=is_down_new
            return ret
    ui:'main.UI'
    position:Optional[Vec]=None
    def __post_init__(self):
        self.buttons={
            MouseButton.LMB:self.ButtonEventManager(lambda:self.ui.window.is_pressed(ti.ui.LMB)),
            MouseButton.RMB:self.ButtonEventManager(lambda:self.ui.window.is_pressed(ti.ui.RMB)),
            MouseButton.MMB:self.ButtonEventManager(lambda:self.ui.window.is_pressed(ti.ui.MMB)),
        }
    def update(self):
        position_new=self.ui.canvas_screen.rect().mul_point(self.ui.window.get_cursor_pos())
        delta_position=Vec(0) if self.position is None else position_new-self.position
        event_id=self.ui.canvas_screen_event.sample(position_new)
        if event_id!=ScreenEventManager.invalid_id:
            register=screen_event_manager.registers.get(event_id)
            if register is not None:
                action=register.action
                def transform(_:Vec):
                    return register.block.canvas.rect_resource.sub_point(_)
                for k,v in self.buttons.items():
                    event=v.update(delta_position)
                    if event==MouseEventType.Click:
                        if action.click is not None:
                            if k==action.button:
                                action.click(transform(position_new))
                    elif event==MouseEventType.Drag:
                        if action.drag is not None:
                            if k==action.button:
                                action.drag(transform(self.position),transform(position_new))
        self.position=position_new