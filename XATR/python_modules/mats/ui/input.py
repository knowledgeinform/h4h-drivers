import numpy as np
import matplotlib.pyplot as plt
import matsui.graphics


def show(ax, inp, acenter):
    img = inp.data('HF')['abs']
    img = matsui.graphics.clip_image(img)
    img = matsui.graphics.imadjust(img, [0.001, 0.70], None, 1.0)
    ax.imshow(img[acenter-400:acenter+400, :], cmap='copper',
                    aspect='auto', vmax=0.08)
    # plt.colorbar()
    return ax