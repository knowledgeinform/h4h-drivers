import mats
import random


class DetRandom(mats.Detector):
    def __init__(self):
        pass

    def detect(self, inp):
        band = inp['ref_name']
        conlist = mats.ContactList()
        ecdlist = mats.EcdataList()

        # Generate some random contact locations
        num_targets = random.randint(1, 5)  # generate 1 to 5 contacts
        ylimit, xlimit = inp.data(band).size()
        xs = []
        ys = []
        for n in range(num_targets):
            xs.append(random.randrange(xlimit))
            ys.append(random.randrange(ylimit))

        # Initialize contact list
        conlist.resize(num_targets)
        ecdlist.resize(num_targets)

        # Fill contact list
        for n in range(num_targets):
            # Contact pixel location
            conlist[n]['x'] = xs[n]
            conlist[n]['y'] = ys[n]

            # Detection score
            ecdlist[n]['detscore'] = 1.0

        return conlist, ecdlist

    def configure(self, config):
        pass

    def train(self):
        pass
    # def train(self, datafiles, reader, gt, inStruct, outStruct):
    #     raise RuntimeError('Not implemented')
