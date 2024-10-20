from TaichiLib import *

@dataclass
class Texture:
    resource:ti.Field
    rect_resource:Rect=None
    def __post_init__(self):
        if self.rect_resource is None:
            self.rect_resource=self.resource_rect()
    def rect(self)->Rect:
        return self.rect_resource.origin()
    def resource_rect(self)->Rect:
        return RectI.full(VecI(self.resource.shape)).F()
    def to_rect_resource(self,rect:Rect)->Rect:
        return self.rect_resource.add(rect)
    def mul(self,sub_rect:Rect)->'Texture':
        return Texture(self.resource,self.rect_resource.mul(sub_rect))
    def add(self,rect:Rect)->'Texture':
        return Texture(self.resource,self.rect_resource.add(rect))
    def sample(self,position:Vec):
        idx=self.rect_resource.I().add_point(position)
        return self.resource[idx.x,idx.y]