import time

from SkopeClip import SkopeClip
scene = bpy.context.scene
clip = SkopeClip(scene,180)
clip.random()
while clip.step():
    clip.apply(scene)
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    time.sleep(.5)
