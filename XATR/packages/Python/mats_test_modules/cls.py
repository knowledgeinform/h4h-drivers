"""MATS Test Suite Classifiers."""
import random
import mats


class ClsAll(mats.Classifier):
    """
    MATS ClsAll classifier module.

    Classifier that labals all contacts as targets and assigns random
    confidence value.
    """

    def __init__(self):
        """Initialize classifier."""
        self.TEST_MODULE = True

    def classify(self, conlist, ecdlist):
        """Classify contacts."""
        for n in range(len(conlist)):
            if conlist[n]['gt'] is True:
                conlist[n]['cls'] = 1
                conlist[n]['classconf'] = random.randrange(100) / 100.0
            else:
                conlist[n]['cls'] = 0
                conlist[n]['classconf'] = 0

    def configure(self, config):
        pass

    def tunable(self, val):
        return False

    # def trainable(self):
    #     return False

    def train(self):
        pass
    # def train(self, datafiles, reader, gt, in_struct, out_struct):
    #     raise RuntimeError('Not implemented')
