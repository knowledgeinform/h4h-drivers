# import matplotlib.pyplot as plt
from matplotlib.pyplot import clf, cla, Figure, plot, show, pause

import mats
from .img import imshow as imshow_input
from .ecd import imshow as imshow_ecd, bounding_box as contact_bounding_box


def bounding_box(con, *args):
    ctype = type(con)
    if mats.cpp_backend:
        if ctype == mats.mc.MATS_contact:
            return contact_bounding_box(con, *args)
        if ctype == mats.mc.MATS_contact_list:
            return [contact_bounding_box(c, *args) for c in con]
    if ctype == mats.Contact:
        return contact_bounding_box(con, *args)
    if ctype == mats.ContactList:
        return [contact_bounding_box(c, *args) for c in con]
    raise ValueError(f'Unknown data type "{ctype}."')


def imshow(data, *args):
    if mats.cpp_backend:
        if type(data) == mats.mc.MATS_ecdata:
            return imshow_ecd(data, *args)
        elif type(data) == mats.mc.MATS_input:
            return imshow_input(data, *args)

    if type(data) == mats.Ecdata:
        return imshow_ecd(data, *args)
    elif type(data) == mats.Input:
        return imshow_input(data, *args)
    raise ValueError('Unhandled sensor')
