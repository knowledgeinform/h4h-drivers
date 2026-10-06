"""
DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
Ave, Panama City, FL 32407.

POC:

Bradley Marchand
NSWC Panama City Division, Code X24 (850)-230-7385
bradley.marchand@navy.mil

Derek Kolacinski
NSWC Panama City Division, Code X23 (850)-230-7218
derek.kolacinski@navy.mil
"""
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons

from matplotlib.widgets import AxesWidget
import six
import mats


class VertSlider(AxesWidget):
    """
    A slider representing a floating point range.

    For the slider to remain responsive you must maintain a
    reference to it.

    The following attributes are defined
      *ax*        : the slider :class:`matplotlib.axes.Axes` instance

      *val*       : the current slider value

      *hline*     : a :class:`matplotlib.lines.Line2D` instance
                     representing the initial value of the slider

      *poly*      : A :class:`matplotlib.patches.Polygon` instance
                     which is the slider knob

      *valfmt*    : the format string for formatting the slider text

      *label*     : a :class:`matplotlib.text.Text` instance
                     for the slider label

      *closedmin* : whether the slider is closed on the minimum

      *closedmax* : whether the slider is closed on the maximum

      *slidermin* : another slider - if not *None*, this slider must be
                     greater than *slidermin*

      *slidermax* : another slider - if not *None*, this slider must be
                     less than *slidermax*

      *dragging*  : allow for mouse dragging on slider

    Call :meth:`on_changed` to connect to the slider event
    """
    def __init__(self, ax, label, valmin, valmax, valinit=0.5, valfmt='%1.2f',
                 closedmin=True, closedmax=True, slidermin=None,
                 slidermax=None, dragging=True, **kwargs):
        """
        Create a slider from *valmin* to *valmax* in axes *ax*.

        Additional kwargs are passed on to ``self.poly`` which is the
        :class:`matplotlib.patches.Rectangle` which draws the slider
        knob.  See the :class:`matplotlib.patches.Rectangle` documentation
        valid property names (e.g., *facecolor*, *edgecolor*, *alpha*, ...).

        Parameters
        ----------
        ax : Axes
            The Axes to put the slider in

        label : str
            Slider label

        valmin : float
            The minimum value of the slider

        valmax : float
            The maximum value of the slider

        valinit : float
            The slider initial position

        label : str
            The slider label

        valfmt : str
            Used to format the slider value, fprint format string

        closedmin : bool
            Indicate whether the slider interval is closed on the bottom

        closedmax : bool
            Indicate whether the slider interval is closed on the top

        slidermin : Slider or None
            Do not allow the current slider to have a value less than
            `slidermin`

        slidermax : Slider or None
            Do not allow the current slider to have a value greater than
            `slidermax`


        dragging : bool
            if the slider can be dragged by the mouse

        """
        AxesWidget.__init__(self, ax)

        self.valmin = valmin
        self.valmax = valmax
        self.val = valinit
        self.valinit = valinit
        self.poly = ax.axhspan(valmin, valinit, 0, 1, **kwargs)

        self.hline = ax.axhline(valinit, 0, 1, color='r', lw=1)

        self.valfmt = valfmt
        ax.set_xticks([])
        ax.set_ylim((valmin, valmax))
        ax.set_yticks([])
        ax.set_navigate(False)

        self.connect_event('button_press_event', self._update)
        self.connect_event('button_release_event', self._update)
        if dragging:
            self.connect_event('motion_notify_event', self._update)
        self.label = ax.text(0.5, 1.03, label, transform=ax.transAxes,
                             verticalalignment='center',
                             horizontalalignment='center')

        self.valtext = ax.text(0.5, -0.03, valfmt % valinit,
                               transform=ax.transAxes,
                               verticalalignment='center',
                               horizontalalignment='center')

        self.cnt = 0
        self.observers = {}

        self.closedmin = closedmin
        self.closedmax = closedmax
        self.slidermin = slidermin
        self.slidermax = slidermax
        self.drag_active = False

    def _update(self, event):
        """update the slider position"""
        if self.ignore(event):
            return

        if event.button != 1:
            return

        if event.name == 'button_press_event' and event.inaxes == self.ax:
            self.drag_active = True
            event.canvas.grab_mouse(self.ax)

        if not self.drag_active:
            return

        elif ((event.name == 'button_release_event') or
              (event.name == 'button_press_event' and
               event.inaxes != self.ax)):
            self.drag_active = False
            event.canvas.release_mouse(self.ax)
            return

        val = event.ydata
        if val <= self.valmin:
            if not self.closedmin:
                return
            val = self.valmin
        elif val >= self.valmax:
            if not self.closedmax:
                return
            val = self.valmax

        if self.slidermin is not None and val <= self.slidermin.val:
            if not self.closedmin:
                return
            val = self.slidermin.val

        if self.slidermax is not None and val >= self.slidermax.val:
            if not self.closedmax:
                return
            val = self.slidermax.val

        self.set_val(val)

    def set_val(self, val):
        xy = self.poly.xy
        xy[1] = 0, val
        xy[2] = 1, val
        self.poly.xy = xy
        self.valtext.set_text(self.valfmt % val)
        if self.drawon:
            self.ax.figure.canvas.draw_idle()
        self.val = val
        if not self.eventson:
            return
        for cid, func in six.iteritems(self.observers):
            func(val)

    def on_changed(self, func):
        """
        When the slider value is changed, call *func* with the new
        slider position

        A connection id is returned which can be used to disconnect
        """
        cid = self.cnt
        self.observers[cid] = func
        self.cnt += 1
        return cid

    def disconnect(self, cid):
        """remove the observer with connection id *cid*"""
        try:
            del self.observers[cid]
        except KeyError:
            pass

    def reset(self):
        """reset the slider to the initial value if needed"""
        if (self.val != self.valinit):
            self.set_val(self.valinit)


def display(data):
    img = data.data(data['ref_name'])
    aspect = img['ares']/img['cres']
    asamples = math.ceil(40/img['ares'])
    ablocks = math.floor(img['anum']/asamples)

    if not img.is_complex() and img['format'] == 'REAL_IMAG':
        img = img['real']
    else:
        img = img['abs']

    fig = plt.figure()
    plt.subplots_adjust(bottom=0.0, top=1.0, left=0.1, right=0.755)
    plt.imshow(img[0:asamples,:], cmap='copper')
    plt.axes().set_aspect(aspect=aspect)

    axcolor = 'lightgoldenrodyellow'
    axblk = plt.axes([0.8, 0.0, 0.08, 0.755], facecolor=axcolor)
    sblk = VertSlider(axblk, '', 1, ablocks, valinit=1)

    def update(val):
        blk = sblk.val
        print(f'Along Track Block: {blk}\n')
        fig.canvas.draw_idle()
    sblk.on_changed(update)

    plt.show()


def imshow(inp: mats.Input, *args):
    # TODO: Create Display modules for sensors that can be use to handle the
    #       sensor switching
    if inp.sensor == 'Image-RGB':
        print(f'Filaname: {inp.filename}\n')
        print(inp.data('IMG-R').storage)
        rchan = inp.data('IMG-R').data
        gchan = inp.data('IMG-G').data
        bchan = inp.data('IMG-B').data
        if inp.data('IMG-R').storage == 'COL_MAJOR':
            rchan = rchan.T
            gchan = gchan.T
            bchan = bchan.T
        img = np.stack((rchan, gchan, bchan), axis=2)
    else:
        raise ValueError('Unhandled sensor')
    return plt.imshow(img, *args)
