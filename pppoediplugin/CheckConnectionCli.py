#!/usr/bin/env python3

from subprocess import getoutput
import threading
import time

class CheckConnectionCli(threading.Thread):
    def __init__(self, pppoedi):
        super(CheckConnectionCli,self).__init__()
        self.pppoedi = pppoedi

    def run(self):
        super(CheckConnectionCli,self).run()
        keyintout = True
        self.pppoedi.settings.active_status = False
        self.pppoedi.pppoedi_bus_interface.OpenSyslog()
        try:
            while not self.pppoedi.settings.quit_pppoedi:
                ppp_status=self.pppoedi.pppoedi_bus_interface.ReadSyslog()
                if self.pppoedi.settings.connect_active:
                    if ppp_status != '':
                        if 'PAP authentication succeeded' in ppp_status and not self.pppoedi.settings.active_status:
                            self.pppoedi.settings.active_status = True
                            print('\033[92m'+"You are on-line."+'\033[0m')
                        elif 'PAP authentication failed' in ppp_status:
                            self.pppoedi.settings.active_status = False
                            self.pppoedi.disconnect()
                            print('\033[91m'+"Login error:\nAuthentication failed."+'\033[0m')
                            print('Press Ctrl-C to close')
                        elif 'Connection terminated.' in ppp_status or 'Unable to complete PPPoE Discovery' in ppp_status:
                            self.pppoedi.settings.active_status = False
                            self.pppoedi.disconnect()
                            print('\033[91m'+"Connection error:\nConnection terminated."+'\033[0m')
                            print('Press Ctrl-C to close')
                time.sleep(0.5)
        except KeyboardInterrupt:
            if not keyintout:
                raise KeyboardInterrupt