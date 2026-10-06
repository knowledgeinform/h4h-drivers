import mats
import PyMATS_core as mc


class XATRCPP(mats.Interface):
    def __init__(self):
        self._interface = mc.MATS_C()

    def engine(self):
        return self._interface.engine()

    def scan(self):
        return self._interface.autoScan()

    def getType(self, mod_type):
        return self._interface.getType(mod_type)

    def module(self, mod_name):
        return self._interface.module(mod_name)

    def create(self, mod_type, mod_name):
        return self._interface.create(mod_type, mod_name)

    def configure(self, cfg):
        self._interface.configure(cfg)
        return

    def process(self, inp):
        return self._interface.process(inp)
