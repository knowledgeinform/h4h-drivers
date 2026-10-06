import mats
from mats.sensor import Sensor, data_description
from mats.data import Precision


class sensImageRGB(Sensor):
    def __init__(self):
        Sensor.__init__(self)
        self._version = "1.0"
        self._name = "Image-RGB"
        self._gt_dist_thresh = 20.0
        self._has_nav = False
        self._ref_name = 'IMG-R'
        self._data['IMG-R'] = data_description(
            "OPTICAL", "FORWARD", Precision.DOUBLE, "BLOCK", [1.0, 1.0])
        self._data['IMG-G'] = data_description(
            "OPTICAL", "FORWARD", Precision.DOUBLE, "BLOCK", [1.0, 1.0])
        self._data['IMG-B'] = data_description(
            "OPTICAL", "FORWARD", Precision.DOUBLE, "BLOCK", [1.0, 1.0])

    def snippet_generator(self, inp, con, ecd):
        """
        Generate variable size snippets. Uses Contact feature vector for
        position and size. First 4 features are respectively assumed to be x,
        y, width, and height.

        Parameters
        ----------
        inp : mats.Input
            Sensor data for given contacts.
        con : mats.Contact
            Contact
        ecd : mats.Ecdata
            Extra contact data

        Returns
        -------
        None
        """
        # We are assuming there is no change in resolution between data bands.
        # print(con.featureset)
        if 'BoundingBox' in con.featureset:
            bb = con.feature('BoundingBox')
            height = bb[2]
            width = bb[3]
        else:
            width = 20
            height = 20
        for band in self._data:
            snip = inp.data(band).snippet(con.x, con.y, width, height)
            snip.ares = inp.data(band).ares
            snip.cres = inp.data(band).cres
            ecd.set_snippet(band, snip)
        return
