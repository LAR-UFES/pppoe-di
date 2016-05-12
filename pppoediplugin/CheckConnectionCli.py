#!/usr/bin/env python3

from subprocess import getoutput
import threading
import time

class CheckConnectionCli(threading.Thread):
    def __init__(self, settings, pppoedi):
        super(CheckConnectionCli,self).__init__()
        self.settings = settings
        self.pppoedi = pppoedi

    def run(self):
        super(CheckConnectionCli,self).run()
        keyintout = True
        self.settings.active_status = False
        self.settings.time_sleep = 3
        try:
            while not self.settings.quit_pppoedi:
                if self.settings.connect_active:
                    if (time.time()-self.settings.time_start) > 10 and not self.settings.active_status:
                        self.pppoedi.disconnect()
                        print('\033[91m'+"Login error:\nIncorrect password or fail in access the server."+'\033[0m')
                        print('Press Ctrl-C to close')
                    interface=getoutput(["ifconfig ppp0 | grep inet"])
    
                    if interface.find("inet") != -1 and not self.settings.active_status:
                        self.settings.active_status = True
                        self.settings.time_sleep = 30
                        print('\033[92m'+"You are on-line."+'\033[0m')
                    elif interface.find("inet") == -1 and self.settings.active_status:
                        self.settings.active_status = False
                        self.settings.time_sleep = 3
    
                time.sleep(self.settings.time_sleep)
        except KeyboardInterrupt:
            if not keyintout:
                raise KeyboardInterrupt