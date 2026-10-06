import os.path as osp
# import math
import json
# import re
import numpy as np

from .contact_summary import ContactSummary, EnsembleContactSummary
from .perf_summary import ArchiveSummary

try:
    from sklearn.metrics import confusion_matrix
except:
    pass

try:
    from tabulate import tabulate
except:
    pass

class PerfReport:
    def __init__(self, class_info=False, class_labels=None):
        self.Files = []
        self.Contacts = []
        self.Gt = []
        self.PrunedContacts = []
        self.FileProcessTime = []
        self.Time = []
        self.Area = []
        #: float: Confidence Threshold for statistics.
        self.Threshold = 0.0
        self.Edt = 3  # Ensemble Detection Threshold
        self.class_info = class_info
        self.class_labels = class_labels
        
    @property
    def ProcessingTime(self) -> float:  # noqa N802
        """Average file processing time."""
        times = [t for t in self.FileProcessTime if t >= 0]
        if len(times) == 0:
            return -1.0
        return sum(times) / len(times)

    @property
    def MissionTime(self) -> float:  # noqa N802
        """Total mission collection time."""
        return sum([t for t in self.Time if t >= 0])

    @property
    def MissionArea(self) -> float:  # noqa N802
        """Total mission collection area."""
        return sum([t for t in self.Area if t >= 0])

    @property
    def TotalGt(self) -> int:  # noqa N802
        """Number of ground truth contacts."""
        return len(self.Gt)

    @property
    def TotalDetections(self) -> int:  # noqa N802
        """Number of contact detections."""
        return len(self.Contacts)

    @property
    def DetectedTargets(self) -> [ContactSummary]:  # noqa N802
        """Ground truth contacts that were detected."""
        return [c for c in self.Contacts if c.gt >= 0]

    @property
    def DetectorMissedTargets(self) -> [ContactSummary]:  # noqa N802
        """Ground truth contacts not detected."""
        return [g for g in self.Gt if g.gt < 0]

    @property
    def DetectorFalseAlarms(self) -> int:  # noqa N802
        """Number of detection contacts that are false alarms."""
        return len([c for c in self.Contacts if c.gt < 0])

    @property
    def ClassifierMissedTargets(self):  # noqa N802
        """Number of missed target contacts."""
        return [c for c in self.Contacts
                if c.conf < self.Threshold and c.gt >= 0]

    @property
    def ClassifierFalseAlarms(self) -> int:  # noqa N802
        """Number of classifier false alarms."""
        return self.Fp

    @property
    def Tp(self) -> int:  # noqa N802
        """Number of true positives contacts."""
        return len([c for c in self.Contacts
                    if c.conf >= self.Threshold and c.gt >= 0])

    @property
    def Fp(self) -> int:  # noqa N802
        """Number of false positives contacts."""
        return len([c for c in self.Contacts
                    if c.conf >= self.Threshold and c.gt < 0])

    @property
    def Fn(self) -> int:  # noqa N802
        """Number of false negative contacts."""
        return len(self.ClassifierMissedTargets)

    @property
    def Tn(self) -> int:  # noqa N802
        """Number of true negative contacts."""
        return len([c for c in self.Contacts
                    if c.conf < self.Threshold and c.gt < 0])

    @property
    def Pd(self) -> float:  # noqa N802
        """Single-look probability of detection."""
        if self.TotalGt == 0:
            return -1.0
        return len([c for c in self.Contacts if c.gt >= 0]) / self.TotalGt

    @property
    def Pc(self) -> float:  # noqa N802
        """Single-look probability of classification."""
        if self.TotalGt == 0:
            return -1.0
        return self.Tp / len(self.DetectedTargets)

    @property
    def PdPc(self) -> float:  # noqa N802
        tp = self.Tp
        fn = self.Fn
        if tp + fn == 0:
            return -1.0
        return tp / self.TotalGt
    
    ### class scores
    @property
    def clsTypes(self):
        # Get union of gt types and prediction types, then remove non-target -99 type
        gt_types = [x.type for x in self.Gt]
        pred_types = [x.type for x in self.Contacts]
        class_types = sorted(list(set(gt_types + pred_types) - set([-99])))
        return class_types
    
    @property
    def clsTotalGt(self) -> int:
        return [len([g for g in self.Gt if g.type == x]) for x in self.clsTypes]
    
    @property
    def clsDetectedTargets(self) -> [[ContactSummary]]:  # noqa N802
        """Ground truth contacts that were detected."""
        return [[c for c in self.Contacts if c.gt >= 0 and c.gt_type == x] for x in self.clsTypes]
    
    @property
    def clsDetectorMissedTargets(self) -> [[ContactSummary]]:  # noqa N802
        """Ground truth contacts not detected."""
        return [[g for g in self.Gt if g.gt < 0 and g.type == x] for x in self.clsTypes]
    
    @property
    def clsNumDetectorMissedTargets(self) -> [[ContactSummary]]:  # noqa N802
        """Ground truth contacts not detected."""
        return [len(x) for x in self.clsDetectorMissedTargets]
    
    @property
    def clsClassifierMissedTargets(self):  
        """Number of missed target contacts."""
        return [[c for c in self.Contacts if c.conf < self.Threshold and c.gt_type == x] for x in self.clsTypes]
    
    @property
    def clsNumClassifierMissedTargets(self):  
        """Number of missed target contacts."""
        return [len(x) for x in self.clsClassifierMissedTargets]
    
    @property
    def clsClassifierFalseAlarms(self) -> int:  
        """Number of classifier false alarms."""
        return self.clsFp

    @property
    def clsClassifierPreds(self):
        return [len([c for c in self.Contacts if c.type == x]) for x in self.clsTypes]

    @property
    def clsTp(self): 
        return [len([c for c in self.Contacts if c.type == x and c.gt_type == x]) for x in self.clsTypes]
        
    @property
    def clsFp(self):
        return [len([c for c in self.Contacts if c.type == x and c.gt_type != x]) for x in self.clsTypes]
    
    @property
    def clsFn(self):
        """Number of false negative contacts."""
        return [len([c for c in self.Contacts if c.type != x and c.gt_type == x]) for x in self.clsTypes]
    
    @property
    def clsTn(self):
        """Number of true negative contacts."""
        return [len([c for c in self.Contacts if c.conf < self.Threshold and c.gt_type == x]) for x in self.clsTypes]
    
    @property
    def clsConfusion(self):
        preds = [c.type for c in self.Contacts]
        gts = [c.gt_type for c in self.Contacts]
        labels = [-99] + self.clsTypes
        conf_mat = confusion_matrix(gts, preds, labels=labels).tolist()
        
        return conf_mat
        
    def printConfusion(self):
        try:
            if self.class_labels is not None:
                labels = ['non-tar'] + [self.class_labels[k] for k in self.clsTypes]
            else:
                labels = [-99] + self.clsTypes
            conf_mat = tabulate(self.clsConfusion, headers=labels, showindex=labels, tablefmt='github')
            
            return conf_mat
        except:
            print('Install tabulate for confusion matrix pretty print')
        
    
    @property
    def clsPd(self):
        """Single-look probability of detection."""
        if self.TotalGt == 0:
            return -1.0
        pd = np.array([len([c for c in self.Contacts if c.gt_type == x]) for x in self.clsTypes]) / np.array(self.clsTotalGt)
        return pd.tolist()
    
    @property
    def clsPc(self):
        """Single-look probability of classification."""
        if self.TotalGt == 0:
            return -1.0
        tmp = np.array(self.clsTp) / np.array([len(x) for x in self.clsDetectedTargets])
        return tmp.tolist()
    
    @property
    def clsPdPc(self):
        tp = self.clsTp
        fn = self.clsFn
        if tp + fn == 0:
            return -1.0
        pdpc = np.array(tp) / np.array(self.clsTotalGt)
        
        return pdpc.tolist()
    
    #######
    @property
    def target_ensembles(self) -> []:
        """List of ground truth ensemble IDs."""
        return list(set([c.eid for c in self.Gt if c.eid >= 0]))

    def target_ensemble(self, eid):
        gt = [c for c in self.Gt if c.eid == eid]
        return gt

    def _max_target_type(self):
        mdt = max([c.type for c in self.Contacts])
        mgt = max([c.type for c in self.Gt])
        return max(mdt, mgt)

    def _update_extend_contact_gt(self, cons, pcons, gtd, eid_shift=None):
        if eid_shift is None:
            eid_shift = True

        gt_offset = self.TotalGt
        con_offset = len(self.Contacts)
        try:
            eid_offset = max([c.eid for c in self.Gt])
        except ValueError:
            eid_offset = 0

        for c in cons:
            if c.gt < 0:
                continue
            c.gt += gt_offset

        for c in pcons:
            if c.gt < 0:
                continue
            c.gt += gt_offset

        # For GT contacts, the gt file contains the index of the contact matched
        # to the GT. Here we shift it to keep the indices correct.
        for c in gtd:
            if c.gt < 0:
                continue
            c.gt += con_offset

        # If the EIDs are present (value greater than zero) then we should keep
        # them unique.
        if eid_shift and len([c.eid for c in gtd if c.eid > 0]) > 0 and eid_offset > min([c.eid for c in gtd if c.eid > 0]):
            for c in gtd:
                if c.eid < 0:
                    continue
                if c.eid == 0:
                    print('WARNING: Zero EID value found. Multi-look stats '
                          'could have problems.')
                    continue
                c.eid += eid_offset
        return

    def add_archive(self, arc: dict):
        self.Files.append(osp.basename(arc['fn']))
        self.FileProcessTime.append(arc['ProcTime'])
        self.Time.append(arc['MissionTime'])
        self.Area.append(arc['MissionArea'])

        cons = arc['Contacts'].copy()
        pcons = arc['PrunedContacts'].copy()
        gtd = arc['Gt'].copy()
        self._update_extend_contact_gt(cons, pcons, gtd, False)

        self.Contacts.extend(cons)
        self.PrunedContacts.extend(pcons)
        self.Gt.extend(gtd)

        return

    def load(self, filename):
        if not osp.exists(filename):
            raise FileNotFoundError(f'{filename} does not exist.')
        with open(filename, 'r') as fp:
            data = json.load(fp)

        gtd = [ContactSummary.from_str(c) for c in data['Gt']]
        cons = [ContactSummary(c) for c in data['Contacts']]
        pruned = [ContactSummary.from_str(c) for c in data['PrunedContacts']]
        if len(self.Files) == 0:
            self.Threshold = data['Threshold']
            self.Time = data['Time']
            self.Area = data['Area']
            self.FileProcessTime = data['ProcessingTime']
            self.Files = data['Files']
            self.Gt = gtd
            self.Contacts = cons
            self.PrunedContacts = pruned
        else:
            self.Threshold.extend(data['Threshold'])
            self.Time.extend(data['Time'])
            self.Area.extend(data['Area'])
            self.FileProcessTime.extend(data['ProcessingTime'])
            self.Files.extend(data['Files'])

            self._update_extend_contact_gt(cons, pruned, gtd)
            self.Gt.extend(gtd)
            self.Contacts.extend(cons)
            self.PrunedContacts.extend(pruned)
        return
    
    def label_classes(self, clsList):
        if self.class_labels is not None:
            keys = [self.class_labels[k] for k in self.clsTypes]
        else:
            keys = self.clsTypes
            
        return {keys[x]: clsList[x] for x in range(len(clsList))}

    def dict(self):
        drep = {
            "Threshold": self.Threshold,
            **( {"clsTypes": self.label_classes(self.clsTypes)} if self.class_info else {}),
            "PdPc": self.PdPc,
            **( {"clsPdPc": self.label_classes(self.clsPdPc)} if self.class_info else {}),
            "TotalGt": self.TotalGt,
            "NumberFiles": len(self.Files),
            "MissionTime": self.MissionTime,
            "MissionArea": self.MissionArea,
            "ProcessingTime": self.ProcessingTime,
            "Detector": {
                "Pd": self.Pd,
                **( {"clsPd": self.label_classes(self.clsPd)} if self.class_info else {}),
                "FalseAlarms": self.DetectorFalseAlarms,
                "NumberMissedTargets": len(self.DetectorMissedTargets),
                **( {"clsNumberMissedTargets": self.label_classes(self.clsNumDetectorMissedTargets)} if self.class_info else {}),
                "MissedTargets": [repr(c) for c in self.DetectorMissedTargets]
            },
            "Classifier": {
                "Pc": self.Pc, "FalseAlarms": self.ClassifierFalseAlarms,
                **( {"clsPc": self.label_classes(self.clsPc)} if self.class_info else {}),
                "NumberMissedTargets": len(self.ClassifierMissedTargets),
                **( {"clsNumberMissedTargets": self.label_classes(self.clsNumClassifierMissedTargets)} if self.class_info else {}),
                'MissedTargets': [repr(c) for c in self.ClassifierMissedTargets],
                **( {"clsConfusion": self.clsConfusion} if self.class_info else {}),
                **( {"printedClsConfusion": self.printConfusion().split('\n')} if self.class_info else {}),
            },
            "Time": self.Time,
            "Area": self.Area,
            "Contacts": [dict(c) for c in self.Contacts],
            "Gt": [repr(c) for c in self.Gt],
            "PrunedContacts": [repr(c) for c in self.PrunedContacts],
            "Files": self.Files
        }

        return drep

    def save(self, fn, keys=None, remove_keys=None):
        """Save report to JSON file.

        :param fn: Filename for report.
        :type fn: str
        """
        if keys is not None:
            out_dict = {k: self.dict()[k] for k in keys}
        else:
            out_dict = self.dict()
            
        if remove_keys is not None:
            out_dict = {k: v for k,v in out_dict.items() if k not in remove_keys}
            
        with open(fn, 'w') as fp:
            json.dump(out_dict, fp, indent=2)
        return

    def single_look(self):
        print(f'PdPc: {self.PdPc}')
        print(f'  Pd: {self.Pd}')
        print(f'  Pc: {self.Pc}')
        print(f' # Detections: {self.TotalDetections}')
        print(f' # Target Opportunties: {self.TotalGt}')
        print(f' # Missed Opportunties: {len(self.DetectorMissedTargets)}')

        print('Target Specific Performance')
        print('---------------------------')
        max_type = self._max_target_type()

        # Counts collected: Detected | Classified | Error | FalseAlarms
        type_perf = np.zeros((max_type+2, 4), dtype=np.int)
        for con in self.Contacts:
            if con.gt_type < 0:  # False alarm detection
                if con.conf >= self.Threshold:  # False alarm
                    type_perf[con.type, 3] += 1
                    continue
                continue
            type_perf[con.gt_type, 0] += 1  # Detected
            if con.conf < self.Threshold:
                # Classifier Miss
                continue
            if con.type == con.gt_type:
                type_perf[con.type, 1] += 1  # Classified
                continue
            type_perf[con.gt_type, 2] += 1  # Missclassified

        # Get Gt Type totals
        for t in range(max_type+2):
            tot = len([c.type for c in self.Gt if c.type == t])
            print(f'{t:02} | {tot:03} {type_perf[t,0]:03} {type_perf[t,1]:03} '
                  f'{type_perf[t,2]:03} {type_perf[t,3]:03}')
        return type_perf

    def multi_look(self):
        egtd = []  # Ensemble GT Contacts
        max_type = self._max_target_type()
        eids = self.target_ensembles
        edets = 0  # Ensemble detections
        ecls = 0  # Ensemble Classifications
        # Counts collected: Detected | Classified | Error | FalseAlarms
        type_perf = np.zeros((max_type + 2, 4), dtype=np.int)
        for eid in eids:
            gtd = self.target_ensemble(eid)
            egtd.append(EnsembleContactSummary(gtd))
            if len([c for c in gtd if c.gt >= 0]) < self.Edt:
                continue
            edets += 1

            cons = [c for c in self.Contacts if c.eid == eid]
            econ = EnsembleContactSummary(cons)

            if econ.conf >= self.Threshold:
                ecls += 1

            # TODO: False Alarms are not counted since non-targets are not given
            #       an EID yet.
            # if con.gt_type < 0:  # False alarm detection
            #     if con.conf >= self.Threshold:  # False alarm
            #         type_perf[con.type, 3] += 1
            #         continue
            #     continue
            type_perf[econ.gt_type, 0] += 1  # Detected
            if econ.conf < self.Threshold:
                # Classifier Miss
                continue
            if econ.type == econ.gt_type:
                type_perf[econ.type, 1] += 1  # Classified
                continue
            type_perf[econ.gt_type, 2] += 1  # Missclassified

        print(f'PdPc: {ecls/len(eids)}')
        print(f'  Pd: {edets/len(eids)}')
        print(f'  Pc: {ecls/edets}')

        # Get Gt Type totals
        for t in range(max_type + 2):
            tot = len([c.type for c in egtd if c.type == t])
            print(
                f'{t:02} | {tot:03} {type_perf[t, 0]:03} {type_perf[t, 1]:03} '
                f'{type_perf[t, 2]:03} {type_perf[t, 3]:03}')
        return
