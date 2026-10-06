import numpy as np
import skimage.transform


class Resize(object):
    """
    Resize numpy array image to desired size maintaining aspect ratio.
    """
    def __init__(self, output_size, pad_mode):
        assert isinstance(output_size, tuple)
        self.output_size = output_size
        self.pad_mode = pad_mode

    def __call__(self, img):
        h, w = self.output_size
        scale = (h/img.shape[0], w/img.shape[1])

        if scale[0] < scale[1]:
            data = skimage.transform.rescale(img, scale[0], multichannel=True)
            pad = w - data.shape[1]
            pad1 = int(np.floor(pad / 2))
            pad2 = int(np.ceil(pad / 2))
            data = np.pad(
                data,
                pad_width=((0, 0), (pad1, pad2), (0, 0)),
                mode=self.pad_mode
            )
        else:
            data = skimage.transform.rescale(img, scale[1], multichannel=True)
            pad = h - data.shape[0]
            pad1 = int(np.floor(pad / 2))
            pad2 = int(np.ceil(pad / 2))
            data = np.pad(
                data,
                pad_width=((pad1, pad2), (0, 0), (0, 0)),
                mode=self.pad_mode
            )
        return data
