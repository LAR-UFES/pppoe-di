#!/usr/bin/env python3

from subprocess import getoutput
import threading
import time
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk

class CheckConnection(threading.Thread):
    def __init__(self, status, settings, pppoedi):
        super(CheckConnection,self).__init__()
        self.status = status
        self.settings = settings
        self.pppoedi = pppoedi

    def run(self):
        super(CheckConnection,self).run()
        self.settings.active_status = False
        self.settings.time_sleep = 3

        while not self.settings.quit_pppoedi:
            if self.settings.connect_active:
                if (time.time()-self.settings.time_start) > 10 and not self.settings.active_status:
                    self.pppoedi.disconnect()
                interface=getoutput(["ifconfig ppp0 | grep inet"])

                if interface.find("inet") != -1 and not self.settings.active_status:
                    self.status.set_from_icon_name("network-transmit-receive",
                                                         gtk.IconSize.BUTTON)
                    self.settings.active_status = True
                    self.settings.time_sleep = 60
                elif interface.find("inet") == -1 and self.settings.active_status:
                    self.status.set_from_icon_name(
                        "network-error", gtk.IconSize.BUTTON)
                    self.settings.active_status = False
                    self.settings.time_sleep = 3

            time.sleep(self.settings.time_sleep)
