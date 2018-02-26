#!/usr/bin/env python3

from subprocess import getoutput
import threading
import time
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk
from gi.repository import GLib

class CheckConnection(threading.Thread):
    def __init__(self, pppoedi):
        super(CheckConnection,self).__init__()
        self.pppoedi = pppoedi

    def run(self):
        super(CheckConnection,self).run()
        self.pppoedi.settings.active_status = False
        fsyslog = open('/var/log/syslog','r')
        while not self.pppoedi.settings.quit_pppoedi:
            ppp_status=fsyslog.read()
            if self.pppoedi.settings.connect_active:
                if ppp_status != '':
                    if 'PAP authentication succeeded' in ppp_status and not self.pppoedi.settings.active_status:
                        self.pppoedi.settings.active_status = True
                        self.pppoedi.button_conn_disconn.set_label("Desconectar")
                        self.pppoedi.button_conn_disconn.set_sensitive(True)
                    elif 'PAP authentication failed' in ppp_status:
                        self.pppoedi.settings.active_status = False
                        self.pppoedi.disconnect()
                        GLib.idle_add(self.pppoedi.showAlertMsg,'Falha na autenticação.', gtk.MessageType.ERROR)
                    elif 'Connection terminated.' in ppp_status or 'Unable to complete PPPoE Discovery' in ppp_status:
                        self.pppoedi.settings.active_status = False
                        self.pppoedi.disconnect()
            time.sleep(0.5)
        fsyslog.close()
