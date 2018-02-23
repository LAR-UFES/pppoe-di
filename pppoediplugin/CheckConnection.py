#!/usr/bin/env python3

from subprocess import getoutput
import threading
import time
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk

class CheckConnection(threading.Thread):
    def __init__(self, settings, pppoedi):
        super(CheckConnection,self).__init__()
        self.settings = settings
        self.pppoedi = pppoedi

    def run(self):
        super(CheckConnection,self).run()
        self.settings.active_status = False

        while not self.settings.quit_pppoedi:
            if self.settings.connect_active:
                ppp_status = getoutput('tail /var/log/syslog | grep pppd')
                if ppp_status != '':
                    if 'PAP authentication succeeded' in ppp_status and not self.settings.active_status:
                        print ('ppp connected')
                        self.settings.active_status = True
                        self.pppoedi.button_conn_disconn.set_label("Disconnect")
                        self.pppoedi.button_conn_disconn.set_sensitive(True)
                    elif 'PAP authentication failed' in ppp_status:
                        print ('authentication failed')
                        self.settings.active_status = False
                        self.pppoedi.disconnect()
                    elif 'Connection terminated.' in ppp_status or 'Unable to complete PPPoE Discovery' in ppp_status:
                        print ('ppp disconnected')
                        self.settings.active_status = False
                        self.pppoedi.disconnect()
            time.sleep(1)
