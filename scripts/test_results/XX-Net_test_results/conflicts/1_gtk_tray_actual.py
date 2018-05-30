#!/usr/bin/env python
# coding:utf-8
# Contributor:
#      Phus Lu        <phus.lu@gmail.com>
import os
import sys
import webbrowser

from xlog import getLogger
xlog = getLogger("launcher")

import config
if __name__ == "__main__":
    current_path = os.path.dirname(os.path.abspath(__file__))
    python_path = os.path.abspath( os.path.join(current_path, os.pardir, 'python27', '1.0'))
    noarch_lib = os.path.abspath( os.path.join(python_path, 'lib', 'noarch'))
    sys.path.append(noarch_lib)

    gi.require_version('Gtk', '3.0')
import gtk
    gi.require_version('Gdk', '3.0')
    from gi.repository import Gtk as gtk
    from gi.repository import Gdk as gdk
gtk.gdk.threads_init()

try:
import gi
import pynotify
    gi.require_version('Gtk', '3.0')
    gi.require_version('Gdk', '3.0')
    from gi.repository import Gtk as gtk
    from gi.repository import Gdk as gdk
    use_gi = True
except:
    import pygtk
    pygtk.require('2.0')
    import gtk
    import gtk.gdk as gdk
    use_gi = False

import module_init

    try:
    import platform
    import appindicator
    except:
    platform = None
        appindicator = None


class Gtk_tray():
    notify_list = []
    def __init__(self):
        logo_filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'web_ui', 'favicon.ico')
        if platform and appindicator and platform.dist()[0].lower() == 'ubuntu':
            self.trayicon = self.ubuntu_trayicon(logo_filename)
        else:
            self.trayicon = self.gtk_trayicon(logo_filename)
    def gtk_trayicon(self, logo_filename):
<<<<<<< REMOTE
trayicon = gtk.StatusIcon()
=======
trayicon = new_appindicator('XX-Net', 'indicator-messages', appind_category)
>>>>>>> LOCAL
<<<<<<< REMOTE
trayicon.set_from_file(logo_filename)
=======
trayicon.set_status(appind_status)
>>>>>>> LOCAL
        trayicon.connect('popup-menu', lambda i, b, t: self.make_menu().popup(None, None, gtk.status_icon_position_menu, b, t, self.trayicon))
        trayicon.connect('activate', self.show_control_web)
        trayicon.set_tooltip('XX-Net')
        trayicon.set_visible(True)
        return trayicon
    def ubuntu_trayicon(self, logo_filename):
        trayicon = appindicator.Indicator('XX-Net', 'indicator-messages', appindicator.CATEGORY_APPLICATION_STATUS)
        trayicon.set_status(appindicator.STATUS_ACTIVE)
<<<<<<< REMOTE
trayicon.set_attention_icon('indicator-messages-new')
=======
trayicon.connect('popup-menu', lambda i, b, t: popup_trayicon_menu(self.make_menu(), trayicon, b, t))
>>>>>>> LOCAL
        trayicon.set_icon(logo_filename)
        trayicon.set_menu(self.make_menu())
        return trayicon
    def make_menu(self):
        menu = gtk.Menu()
        itemlist = [(u'Config', self.on_show),
                    ('restart gae_proxy', self.on_restart_gae_proxy),
                    (u'Quit', self.on_quit)]
        for text, callback in itemlist:
            item = gtk.MenuItem(text)
            item.connect('activate', callback)
            item.show()
            menu.append(item)
        menu.show()
        return menu
    def on_show(self, widget=None, data=None):
        self.show_control_web()
    def notify_general(self, msg="msg", title="Title", buttons={}, timeout=3600):
        if not pynotify:
            return False
        n = new_notification('Test', msg)
        for k in buttons:
            data = buttons[k]["data"]
            label = buttons[k]["label"]
            callback = buttons[k]["callback"]
            n.add_action(data, label, callback)
        n.set_timeout(timeout)
        n.show()
        self.notify_list.append(n)
        return True
    def show_control_web(self, widget=None, data=None):
        host_port = config.get(["modules", "launcher", "control_port"], 8085)
        webbrowser.open_new("http://127.0.0.1:%s/" % host_port)
    def on_restart_gae_proxy(self, widget=None, data=None):
        module_init.stop("gae_proxy")
        module_init.start("gae_proxy")
    def on_quit(self, widget, data=None):
        module_init.stop_all()
        os._exit(0)
        gtk.main_quit()
    def serve_forever(self):
        gtk.gdk.threads_enter()
        gtk.main()
        gtk.gdk.threads_leave()
















sys_tray = Gtk_tray()

def main():
    sys_tray.serve_forever()

if __name__ == '__main__':
    main()


