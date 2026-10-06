import mats
import numpy


class FeatTest(mats.Feature):
    def __init__(self):
        pass

    def feature(self, conlist, ecdlist):
        # Add a single feature.
        feat = numpy.array([42])
        for n in range(len(conlist)):
            conlist[n].add_feature("FeatTest", feat)

    def configure(self, config):
        pass

    def train(self):
        pass
    # def train(self, datafiles, reader, gt, inStruct, outStruct):
    #     raise RuntimeError('Not implemented')
