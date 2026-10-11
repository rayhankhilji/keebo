import numpy as np

from keebo.art.canvas import DEVICE, SIZE, Canvas
from keebo.art.character import FORM_NAMES, Pose, render
from keebo.art.palette import CLEAR, MINT, PALETTE, flat_palette


def test_palette_fits_one_gif_table():
    assert 16 <= len(PALETTE) < CLEAR
    assert len(flat_palette()) % 3 == 0


def test_canvas_draws_and_scales_to_device():
    c = Canvas()
    c.rect(2, 2, 4, 4, MINT)
    assert c.get(3, 3) == MINT and c.get(0, 0) == CLEAR
    img = c.to_image()
    assert img.size == (DEVICE, DEVICE) == (128, 128)


def test_out_of_bounds_drawing_is_clipped():
    c = Canvas()
    c.rect(-10, -10, 200, 200, MINT)
    c.line(-5, -5, 100, 100, MINT)
    assert (c.data == MINT).all()


def test_every_form_renders_inside_the_canvas():
    for form in FORM_NAMES:
        c = render(Pose(form=form, hat="crown", face_acc="glasses", neck="scarf", back="cape"))
        drawn = np.argwhere(c.data != CLEAR)
        assert len(drawn) > 100
        assert drawn.min() >= 0 and drawn.max() < SIZE


def test_poses_change_the_picture():
    a = render(Pose()).data
    b = render(Pose(eyes="happy", mouth="grin")).data
    assert (a != b).any()


def test_skins_look_different_but_share_the_rig():
    from keebo.art.character import SKINS

    imgs = [render(Pose(skin=s)) for s in SKINS]
    assert len(SKINS) >= 2
    assert (imgs[0].data != imgs[1].data).any()
    for s in SKINS:
        assert (render(Pose(skin=s, lying=True)).data != CLEAR).any()
