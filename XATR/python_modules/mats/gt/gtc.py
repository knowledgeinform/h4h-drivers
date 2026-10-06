

class GtContact:
    def __init__(self, pos: tuple = None, eid: int = None, side: str = None,
                 ctype: int = None, mlo: bool = None, note: str = None,
                 fn: str = None, enabled: bool = None):
        if pos is None:
            self.position = []
        else:
            self.position = pos

        if eid is None:
            self.eid = 0
        else:
            self.eid = eid

        if side is None:
            self.side = 'PORT'
        else:
            self.side = side

        if ctype is None:
            self.type = 0
        else:
            self.type = ctype

        if note is None:
            self.note = ''
        else:
            self.note = note
        if enabled is None:
            self.enabled = True
        else:
            self.enabled = enabled
        if fn is None:
            self.fn = ''
        else:
            self.fn = fn
        if mlo is None:
            self.mlo = True
        else:
            self.mlo = mlo
        self.dimensions = [0, 0]
        self.image_size = [0, 0]

    def __iter__(self):
        yield 'x', self.x
        yield 'y', self.y
        yield 'num', self.num
        yield 'dim', self.dimensions
        yield 'type', self.type
        yield 'fn', self.fn
        yield 'side', self.side
        yield 'enable', self.enabled
        yield 'MLO', self.mlo

    @property
    def x(self):
        return self.position[0]

    @property
    def y(self):
        return self.position[1]

    @property
    def num(self):
        return max(0, self.eid)
