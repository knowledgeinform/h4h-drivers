import mats
import numpy as np
import matplotlib.pyplot as plt


def imshow(ecd: mats.Ecdata, *args):
    # TODO: Create Display modules for sensors that can be use to handle the
    #       sensor switching
    if ecd.sensor == 'Image-RGB':
        img = np.stack(
            (ecd.snippet('IMG-R').data,
             ecd.snippet('IMG-G').data,
             ecd.snippet('IMG-B').data),
            axis=2
        )
    else:
        raise ValueError('Unhandled sensor')
    return plt.imshow(img, *args)


def bounding_box(con: mats.Contact, *args):
    if 'BoundingBox' in con.featureset:
        bb = con.feature('BoundingBox')
        h = bb[2]
        w = bb[3]
    else:
        w = 20
        h = 20

    hw = w // 2
    hh = h // 2
    return plt.plot(
        [con.x - hw, con.x - hw, con.x + hw, con.x + hw, con.x - hw],
        [con.y - hh, con.y + hh, con.y + hh, con.y - hh, con.y - hh], *args)
