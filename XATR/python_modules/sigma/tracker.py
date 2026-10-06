from glob import glob
import os.path as osp
import yaml
try:
    import natsort
    __NATSORT__ = True
except:
    __NATSORT__ = False


def load_tracker_contacts(track_dir):
    dns = glob(osp.join(track_dir, '*'))
    dns = [d for d in dns if osp.isdir(d)]
    if __NATSORT__:
        dns = natsort.os_sorted(dns)
    else:
        dns.sort()
    cons = []
    for d in dns:
        con_fn = osp.join(d, 'contact.yaml')
        with open(con_fn, 'r') as fh:
            con = yaml.safe_load(fh)
        if len(con) > 1:
            print('!! More than one contact detected.')
        con = con[0]
        max_val = max(con['Confidences'])
        max_ix = con['Confidences'].index(max_val)
        con['Type'] = con['Types'][max_ix]
        con['Confidence'] = max_val
        cons.append(con)
    return cons