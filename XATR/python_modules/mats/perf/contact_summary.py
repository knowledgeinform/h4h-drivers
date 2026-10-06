import mats
import re
import math


class ContactSummary:
    def __init__(self, con=None):
        """Summary of contact information for the purpose of performance
        statistics.

        :param con: Contact to be used for initialization
        :type con: mats.Contact or dict, optional
        :returns: None
        """
        self._conf = 0.0
        self._detscore = 0.0

        # Default values
        self.x = -1
        self.y = -1
        self.type = -99
        self.conf = 0.0
        self.side = None
        self.fn = None
        self.gt = -1
        self.gt_type = -99
        self.observable = True
        self.detscore = 0.0
        self.range = 0.0
        self.eid = -1

        if con is None:
            return

        if type(con) == dict:
            if 'x' in con:
                self.x = con.get('x', -1)
            else:
                self.x = con.get('X', -1)
            if 'y' in con:
                self.y = con.get('y', -1)
            else:
                self.y = con.get('Y', -1)
            if 'type' in con:
                self.type = con.get('type', -99)
            else:
                self.type = con.get('Type', -99)
            if 'conf' in con:
                self.conf = con.get('conf', 0.0)
            else:
                self.conf = con.get('Conf', 0.0)
            if 'side' in con:
                self.side = con.get('side', None)
            else:
                self.side = con.get('Side', None)

            if 'num' in con:
                self.eid = con['num']
            elif 'Eid' in con:
                self.eid = con['Eid']
            else:
                self.eid = con.get('eid', -1)

            if 'fn' in con:
                self.fn = con['fn']
            elif 'filename' in con:
                self.fn = con['filename']
            elif 'Filename' in con:
                self.fn = con['Filename']

            if 'Gt' in con:
                self.gt = con['Gt']
            elif 'gt' in con:
                self.gt = con['gt']
            if 'GtType' in con:
                self.gt_type = con['GtType']
            elif 'gt_type' in con:
                self.gt_type = con['gt_type']
            if 'Observable' in con:
                self.observable = con['Observable']
            if 'Detscore' in con:
                self.detscore = con['Detscore']
            elif 'detscore' in con:
                self.detscore = con['detscore']
            if 'Range' in con:
                self.range = con['Range']
        else:  # Assumes mats.Contact
            self.x = con.x
            self.y = con.y
            self.type = con.cls
            self.conf = con.classconf
            self.side = con.side
            self.fn = con.filename
            self.gt = con.gt
            # self.eid = con.id  # TODO(Bradley): This may not be a good idea...
            self.eid = -1
        return

    def __lt__(self, other):
        return self.conf < other.conf

    def __repr__(self):
        return (
            f'{self.fn} {self.side} {self.eid} {self.gt} '
            f'[{self.type}, {self.gt_type}] @ '
            f'({self.x}, {self.y}) - ({self.detscore}, {self.conf}) '
            f'[{self.observable} - {self.range}]'
        )

    def __str__(self):
        return (
            f'         x: {self.x}\n'
            f'         y: {self.y}\n'
            f'       eid: {self.eid}\n'
            f'        gt: {self.gt}\n'
            f'      type: {self.type}\n'
            f'   gt_type: {self.gt_type}\n'
            f'observable: {self.observable}\n'
            f'      conf: {self.conf}\n'
            f'  detscore: {self.detscore}\n'
            f'     range: {self.range}\n'
            f'      side: {self.side}\n'
            f'        fn: {self.fn}'
        )

    def __iter__(self):
        yield 'X', self.x
        yield 'Y', self.y
        yield 'Eid', self.eid
        yield 'Conf', self.conf
        yield 'Detscore', self.detscore
        yield 'Type', self.type
        yield 'Side', self.side
        yield 'Gt', self.gt
        yield 'GtType', self.gt_type
        yield 'Observable', self.observable
        yield 'Range', self.range
        yield 'Filename', self.fn

    @property
    def conf(self):
        return self._conf

    @conf.setter
    def conf(self, val):
        if math.isnan(val):
            val = 0.0
        elif val > 1:
            val = 1
        elif val < 0:
            val = 0
        self._conf = val
        return

    @property
    def detscore(self):
        return self._detscore

    @detscore.setter
    def detscore(self, val):
        if math.isnan(val):
            val = 0.0
        self._detscore = val
        return

    @classmethod
    def from_str(cls, repr_str):
        c = re.search(
                r'(?P<fn>[/.\w]+) (?P<side>\w+) (?P<eid>-*\d+) (?P<gt>-*\d+) '
                r'\[(?P<type>-*\d+), (?P<gt_type>-*\d+)\] @ '
                r'\((?P<x>-*\d+), (?P<y>-*\d+)\) - '
                r'\((?P<detscore>\d+\.\d+), (?P<conf>\d+\.\d+)\) '
                r'\[(?P<observable>\w+) - (?P<range>\d+.\d)\]',
                repr_str)
        c = c.groupdict()
        for fld in ['eid', 'gt', 'x', 'y', 'type', 'gt_type']:
            c[fld] = int(c[fld])
        for fld in ['detscore', 'conf', 'range']:
            c[fld] = float(c[fld])
        c['observable'] = bool(c['observable'])
        return cls(c)

    @classmethod
    def from_dict(cls, data):
        cs = cls()

        cs.conf = data["Conf"]
        cs.detscore = data["Detscore"]
        cs.x = data["X"]
        cs.y = data["Y"]
        cs.type = data["Type"]
        cs.side = data["Side"]
        cs.gt = int(data["Gt"])
        cs.gt_type = data["GtType"]
        cs.observable = data["Observable"]
        cs.range = data["Range"]
        cs.fn = data["Filename"]
        cs.eid = data.get('Eid', None)
        return cs

    def set_observable(self, xy_max=None, sweetspot=None):
        """Sets whether contact is observable.

        :param xy_max: Maximum X and Y values.
        :type xy_max: list, optional
        :param sweetspot: Sensor sweetspot.
        :type sweetspot: list, optional
        :returns: None
        """
        if xy_max is not None and (self.y >= xy_max[0] or self.x >= xy_max[1]):
            mats.log.warn(f"GT outside image bounds ({self.fn} - {self.side}).")
            self.observable = False
            return
        elif sweetspot is not None and\
                (self.x < sweetspot[0] or self.x > sweetspot[1]):
            self.observable = False
            return
        self.observable = True
        return


class EnsembleContactSummary:
    def __init__(self, cons):
        self.contacts = cons

        confs = [c.conf for c in self.contacts]
        self.max_idx = confs.index(max(confs))
        return

    @property
    def gt(self):
        return self.contacts[0].gt >= 0

    @property
    def eid(self):
        return self.contacts[0].eid

    @property
    def type(self):
        return self.contacts[self.max_idx].type

    @property
    def gt_type(self):
        # All the gt types should be the same.
        return self.contacts[0].gt_type

    @property
    def conf(self):
        return self.contacts[self.max_idx].conf

    @property
    def detscore(self):
        return max([c.detscore for c in self.contacts])

    @property
    def side(self):
        return self.contacts[0].side
