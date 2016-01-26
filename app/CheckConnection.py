#!/usr/bin/env python

from subprocess import getoutput
import os
import threading
import time

import Settings


class CheckConnection(threading.Thread):
    def __init__(self, status):
        threading.Thread.__init__(self)
        self.status = status

    def run(self):
        threading.Thread.run(self)
        Settings.active_status = False
        Settings.timesleep = 3

        while not Settings.quit_pppoedi:
            if Settings.connect_active:
                interface = getoutput(["route", "-n"])
                interface = interface.split("\n")[2].split(' ')[-1]

                if interface == "ppp0" and not Settings.active_status:
                    self.status.gtk.Image.from_icon_name("network-offline", Gtk.IconSize.BUTTON)
                    Settings.active_status = True
                    Settings.timesleep = 60
                elif interface != "ppp0" and Settings.active_status:
                    self.status.gtk.Image.from_icon_name("network-transmit-receive", Gtk.IconSize.BUTTON)
                    Settings.active_status = False
                    Settings.timesleep = 3

            time.sleep(Settings.timesleep)
