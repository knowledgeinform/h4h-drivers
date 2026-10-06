import math
from mats import Archive
import mats.sensor
from .contact_summary import ContactSummary


# Returns index of closest GT to contact.
def find_gt_match(ares, cres, con, gt):
    ix = 0
    da = ares*(con.y - gt[0].y)
    dc = cres*(con.x - gt[0].x)
    val = math.sqrt(da*da+dc*dc)

    for k in range(1, len(gt)):
        da = ares*(con.y - gt[k].y)
        dc = cres*(con.x - gt[k].x)
        dist = math.sqrt(da*da+dc*dc)

        if dist < val:
            ix = k
            val = dist
    return ix


def prune_repeat_contacts(con):
    pruned = []
    # Figure out the number of gt.
    max_gt = -99
    for c in con:
        max_gt = max(max_gt, c.gt)
    if max_gt < 0:
        return pruned

    for ngt in range(max_gt+1):
        gt_cons = [c for c in con if c.gt == ngt]
        if not gt_cons:
            continue

        # remove last calls first since indices will shift with removal.
        gt_cons.sort(reverse=True)
        for k in range(1, len(gt_cons)):
            con.remove(gt_cons[k])
            pruned.append(gt_cons[k])
    return pruned





class ArchiveSummary:
    def __init__(self, arc_fn):
        #: str: Archive filename
        self.fn = arc_fn
        self.arc = Archive()

        #: float: Logged time it took to process archives input file.
        try:
            self.ProcTime = self.arc.timing()
        except RuntimeError:
            self.ProcTime = -1.0

        self.arc.load(self.fn)
        gtd = self.arc.groundtruth()
        cons = self.arc.contact()

        #: [ContactSummary]: Archive ground truth.
        self.Gt = [ContactSummary(g) for g in gtd]

        #: [ContactSummary]: Summary of archive contacts.
        self.Contacts = [ContactSummary(c) for c in cons]

        inp = self.arc.input()
        sns = mats.sensor.mats_sensor(inp['sensor'])
        if sns.has_nav:
            t = inp['time']
            self.MissionTime = t[-1] - t[0]
        else:
            self.MissionTime = -1

        ares = inp['data'][sns.ref_name]['ares']
        cres = inp['data'][sns.ref_name]['cres']
        anum = inp['data'][sns.ref_name]['anum']
        cnum = inp['data'][sns.ref_name]['cnum']
        self.MissionArea = ares*cres*anum*cnum

        self._associate_gt()

        #: [ContactSummary]: Duplicate contacts removed.
        self.PrunedContacts = prune_repeat_contacts(self.Contacts)

        return

    @property
    def TotalGt(self) -> int:  # noqa N802
        return len(self.Gt)

    @property
    def TotalContacts(self) -> int:  # noqa N802
        """Number of detection contacts"""
        return len(self.Contacts)

    @property
    def DetectorMissedTargets(self) -> [ContactSummary]:  # noqa N802
        """Ground truth contacts not detected."""
        return [g for g in self.Gt if g.gt < 0]

    def __repr__(self):
        return (
            f'ArchiveSummary[{self.TotalContacts}, {self.TotalGt}]'
        )

    def __str__(self):
        return (
            f'        TotalContacts: {self.TotalContacts}\n'
            f'              TotalGt: {self.TotalGt}\n'
            f'DetectorMissedTargets: [{len(self.DetectorMissedTargets)}]\n'
            f'             Contacts: [{len(self.Contacts)}]\n'
            f'             ProcTime: {self.ProcTime}\n'
        )

    def __iter__(self):
        yield 'fn', self.fn
        yield 'ProcTime', self.ProcTime
        yield 'Gt', self.Gt
        yield 'Contacts', self.Contacts
        yield 'MissionTime', self.MissionTime
        yield 'MissionArea', self.MissionArea
        yield 'PrunedContacts', self.PrunedContacts

    def _associate_gt(self):
        inp = self.arc.input()
        sns = mats.sensor.mats_sensor(inp['sensor'])

        ares = inp['data'][sns.ref_name]['ares']
        cres = inp['data'][sns.ref_name]['cres']
        anum = inp['data'][sns.ref_name]['anum']
        cnum = inp['data'][sns.ref_name]['cnum']
        ss = inp['sweetspot']
        ecd = self.arc.ecdata()

        # If no sweetspot is set, then it shouldn't be used to calculate whether
        # a contact is observable.
        if ss[0] == ss[1]:
            ss = None

        # Match GT with contact list. Note, gt_match contains positive
        for (k, cs) in enumerate(self.Contacts):
            cs.detscore = ecd[k].detscore
            cs.range = cres * cs.x
            cs.set_observable([anum, cnum], ss)
            if type(cs.gt) == bool:
                if not cs.gt:
                    cs.gt = -1
                    continue
            elif cs.gt < 0:
                continue

            # This shouldn't happen. If it does then all the metrics are going
            # to be messed up, because we have a ground truth contact without
            # any noted ground truth opportunities.
            if self.TotalGt == 0:
                mats.log.warn(f"GT Contact without associated GT "
                              f"({cs.fn}). Demoting contact.")
                cs.gt = -1
                continue

            # Here we are assuming the contact gt field was set correctly, and
            # we match it to the closest one gt. Hence, if a contact is mark GT,
            # but the GT is not in the GT list, then bad things start to happen.
            cs.gt = find_gt_match(ares, cres, cs, self.Gt)
            cs.gt_type = self.Gt[cs.gt].type
            cs.eid = self.Gt[cs.gt].eid

            # Check if GT match has already been matched. If it has then we only
            # list the contact with the highest confidence. This ensures that
            # detection rate will not be affected by repeated calls.
            if self.Gt[cs.gt].gt < 0:  # No other matches
                self.Gt[cs.gt].gt = k
            else:
                if self.Contacts[self.Gt[cs.gt].gt].conf < cs.conf:
                    self.Gt[cs.gt].gt = k
        return
