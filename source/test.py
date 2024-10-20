from TaichiPaint.paint import pattern
from TaichiLib import *
from TaichiPaint.ui.main import UI
from TaichiPaint.ui.block import Horizontal, ColorBlock
from TaichiPaint.paint.main import Paint
from TaichiPaint.paint import brush
from TaichiPaint import common

ti.init(arch=ti.cuda)

test_canvas = ti.field(Color, (1024, 1024))
test_mask = ti.field(Color, (4, 4))


@ti.kernel
def setup():
    for i, j in test_canvas:
        test_canvas[i, j] = Color(0, float(i)/1024, float(j)/1024)
    for i, j in test_mask:
        test_mask[i, j] = Color(0, 0, 0)


setup()

background = Horizontal(blocks=[
    ColorBlock(Color(0, 1, 0)).block,
    Paint(common.Texture(test_canvas), brush=brush.Stamp(
        pattern=pattern.Sphere(), size=10, length_per_stroke=4, alpha=0.2)).block,
], partition=[0.3,]).block
ui = UI(root=background)
ui.run()
