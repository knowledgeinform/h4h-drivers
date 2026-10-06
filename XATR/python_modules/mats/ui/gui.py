import math
import gi
from gi.repository import Gtk
import mats.pkg


gi.require_version('Gtk', '3.0')
_widget_height = 20
_widget_width = 80
_label_width = 16
_text_len = 28

def str_shorten(s, n):
    if n < 3:
        raise ValueError('\'n\' ({}) must be greater then 3.'.format(n))
    if n < 0:
        raise ValueError('\'n\' ({}) must be positive.'.format(n))

    # Check if truncation is needed
    if len(s) <= n:
        return s

    left_len = int(math.floor(n/2) - 1)
    right_len = int(math.ceil(n/2))
    rix = len(s) - right_len + 1
    if not (n % 2):
        left_len -= 1
    return s[0:left_len] + '...' + s[rix:]


def ui_create_label(name):
    lbl = Gtk.Label(name)
    # lbl.set_size_request(_label_width, _widget_height)
    lbl.set_width_chars(_label_width)
    lbl.set_justify(Gtk.Justification.RIGHT)
    lbl.set_alignment(0, 0.5)
    return lbl


def ui_DirSlt_Callback(widget, data):
    print('DirSlt')


def ui_DirSlt(gObj, label, value, func):
    box = Gtk.Box(spacing=6)
    gObj.add(box)

    lbl = ui_create_label(label)
    btn = Gtk.Button(label=value)
    btn.set_size_request(_widget_width, _widget_height)
    btn.connect('clicked', func)
    box.pack_start(lbl, False, True, 0)
    box.pack_start(btn, True, True, 0)

    return box


def ui_FileSlt(gObj, label, value, func):
    box = Gtk.Box(spacing=6)
    gObj.add(box)

    lbl = ui_create_label(label)
    btn = Gtk.Button(label=value)
    btn.set_size_request(_widget_width, _widget_height)
    btn.connect('clicked', func)
    box.pack_start(lbl, False, True, 0)
    box.pack_start(btn, False, True, 0)

    return box


def ui_FileOpts(gObj, label, value, func):
    box = Gtk.Box(spacing=6)
    gObj.add(box)

    lbl = ui_create_label(label)
    btn = Gtk.Button(label=value)
    btn.set_size_request(_widget_width, _widget_height)
    btn.connect('clicked', func)
    box.pack_start(lbl, False, True, 0)
    box.pack_start(btn, False, True, 0)

    return box


def fet(gObj, path, data):
    return 'hi'


def ui_Drop(gObj, label, value, func):
    box = Gtk.Box(spacing=6)
    gObj.add(box)

    lbl = ui_create_label(label)
    drp = Gtk.ComboBoxText()
    drp.set_entry_text_column(0)
    drp.set_size_request(_widget_width, _widget_height)
    drp.connect("changed", func)

    for v in value:
        drp.append_text(v)
    box.pack_start(lbl, False, True, 0)
    box.pack_start(drp, True, True, 0)

    return box


def ui_Text(gObj, label, value):
    box = Gtk.Box(spacing=6)
    gObj.add(box)

    lbl = ui_create_label(label)
    txt = Gtk.Entry()
    txt.set_editable(False)
    txt.set_size_request(_widget_width, _widget_height)
    if value:
        txt.set_text(value)
    box.pack_start(lbl, True, True, 0)
    box.pack_start(txt, True, True, 0)

    return box


def ui_Panel(gObj, label):
    frame = Gtk.Frame(label=label)
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    box.set_border_width(10)
    frame.add(box)
    gObj.add(frame)

    return box

class MATSGUI(Gtk.Window):
    """MATS Main GUI."""

    def __init__(self):
        """Create MATS GUI."""
        mats.pkg.scan()

        Gtk.Window.__init__(self, title="MATS")
        self.set_size_request(400, 600)
        self.set_border_width(10)
        # self.set_resizable(False)

        self.connect('delete_event', Gtk.main_quit)
        self._spacing = 6

        readers = ['MSHDF', 'MST', 'JSF']
        sensors = mats.pkg.sensor_list()

        self.main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                            spacing=self._spacing)
        self.add(self.main)

        self.iodata = ui_Panel(self.main, 'I/O Data')
        ui_DirSlt(self.iodata, 'Source Directory:', '**Choose**',
                  self.dialog_dir_slt)
        ui_Drop(self.iodata, 'Data Reader:', readers, self.reader_changed)
        ui_Drop(self.iodata, 'Sensor:', sensors, self.reader_changed)
        ui_FileOpts(self.iodata, 'Data Files:', '**Choose**', self.hello)
        ui_FileSlt(self.iodata, 'Ground Truth File:', '**Choose**', self.hello)
        ui_DirSlt(self.iodata, 'Output Directory:', '**Choose**',
                  self.dialog_dir_slt)

        # self.envmod = ui_Panel(self.main, 'Environmental Modules')
        # ui_Drop(self.envmod, 'Segmenter:', [], self.reader_changed)
        # ui_Drop(self.envmod, 'Seg. Configuration:', [], self.reader_changed)
        # ui_Text(self.envmod, 'Estimators:', '')

        self.atrmod = ui_Panel(self.main, 'ATR Modules')
        ui_Drop(self.atrmod, 'Detector:', mats.pkg.get_type('detector'),
                self.reader_changed)
        ui_Drop(self.atrmod, 'Det. Configuration:', [], self.reader_changed)
        ui_Drop(self.atrmod, 'Normalizer:', mats.pkg.get_type('normalizer'),
                self.reader_changed)
        ui_Drop(self.atrmod, 'Classifier:', mats.pkg.get_type('classifier'),
                self.reader_changed)
        ui_Drop(self.atrmod, 'Class. Configuration:', [], self.reader_changed)
        ui_Text(self.atrmod, 'Features:', '')
        # ui_Drop(self.atrmod, 'Performance Est.:', [], self.reader_changed)
        # ui_Drop(self.atrmod, 'Contact Correlation:', [], self.reader_changed)

        self.show_all()

        self.params = {
            'source_dir': ''
        }

#     def main(self):
#         """Main for PyGTK application."""
#         gtk.main()
#
#     def destroy(self, widget, data=None):
#         """PyGTK application quit."""
#         gtk.main_quit()
#
#     def close_event(self, widget, event, data=None):
#         """Close MATS GUI."""
#         print("delete event occurred")
#
#         # Change FALSE to TRUE and the main window will not be destroyed
#         # with a "delete_event".
#         return False
#
    def dialog_dir_slt(self, widget, func=None):
        dialog = Gtk.FileChooserDialog(
            'Choose source directory',
            self,
            Gtk.FileChooserAction.SELECT_FOLDER,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select",
             Gtk.ResponseType.OK)
        )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            fn = dialog.get_filename()
            self.params['source_dir'] = fn
            widget.set_label(str_shorten(fn, _text_len))
            widget.set_tooltip_text(fn)
            print("Folder selected: " + fn)
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
        dialog.destroy()

    def hello(self, widget, data=None):
        """Example callback."""
        print("Hello World")

    def reader_changed(self, widget):
        text = widget.get_active_text()
        if text:
            print("Reader: %s" % text)


def app():
    a = MATSGUI()
    Gtk.main()
