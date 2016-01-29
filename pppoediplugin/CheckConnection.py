#!/usr/bin/env python3

from subprocess import getoutput
import multiprocessing
import time
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk

class CheckConnection(multiprocessing.Process):
    def __init__(self, status, settings):
        multiprocessing.Process.__init__(self)
        self.status = status
        self.settings = settings

    def run(self):
        multiprocessing.Process.run(self)
        self.settings.active_status = False
        self.settings.time_sleep = 3

        while not self.settings.quit_pppoedi:
            if self.settings.connect_active:
                interface=getoutput(["ifconfig ppp0 | grep inet"])

                if interface.find("inet") != -1 and not self.settings.active_status:
                    self.status.set_from_icon_name("network-transmit-receive",
                                                         gtk.IconSize.BUTTON)
                    self.settings.active_status = True
                    self.settings.time_sleep = 60
                elif interface.find("inet") == -1 and self.settings.active_status:
                    self.status.set_from_icon_name(
                        "network-idle", gtk.IconSize.BUTTON)
                    self.settings.active_status = False
                    self.settings.time_sleep = 3

            time.sleep(self.settings.time_sleep)
