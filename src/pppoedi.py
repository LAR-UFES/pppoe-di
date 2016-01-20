#!/usr/bin/python
'''
Created on Jan 14, 2016

@author: analista
'''

from gi.repository import Gtk as gtk
import os
import commands
import threading
import time

quit_pppoedi=False
connect_active=False
active_status=False
timesleep=3

class Pppoe(object):
    def __init__(self):
        object.__init__(self)
        builder = gtk.Builder()
        builder.add_from_file("/opt/pppoedi/pppoedi.glade")
        self.window = builder.get_object("main_window")
        self.entry_login = builder.get_object("entry_login")
        self.entry_password = builder.get_object("entry_password")
        self.status = builder.get_object("status")
        self.checkbutton_savepass = builder.get_object("checkbutton_savepass")
        self.window.show()
        builder.connect_signals({"gtk_main_quit":self.quit_pppoe,
                                 "on_entry_login_activate":self.connect,
                                 "on_entry_password_activate":self.connect,
                                 "on_button_connect_clicked":self.connect,
                                 "on_button_disconnect_clicked":self.disconnect})
        self.pap="/etc/ppp/pap-secrets"
        f=open('/etc/os-release','r')
        line=''
        while line.find('NAME') == -1:
            line=f.readline()
        f.close()
        self.linux_os = line
        home=os.getenv("HOME")
        self.file_pppoe=home+"/.pppoedi"
        if os.path.isfile(self.file_pppoe):
            f=open(self.file_pppoe,'r')
            login_pass = f.read()
            login_pass=login_pass.split(",")
            if len(login_pass)>1:
                login=login_pass[0]
                password=login_pass[1]
                self.entry_login.set_text(login)
                self.entry_password.set_text(password)
                self.checkbutton_savepass.set_active(True)
        check_conn=CheckConnection(self.status)
        check_conn.start()
        net=commands.getoutput('route -n')
        net=net.split("\n")[2].split(' ')[9]
        os.system("route add -net 200.137.66.0/24 gw "+net)

    def quit_pppoe(self, widget):
        global quit_pppoedi
        global connect_active
        quit_pppoedi=True
        if connect_active:
            self.disconnect(widget)
        gtk.main_quit()
    
    def save_pass(self):
        login = self.entry_login.get_text()
        password = self.entry_password.get_text()
        f=open(self.file_pppoe,'w')
        f.write(login+","+password)
        f.close()
    
    def connect(self, widget):
        global connect_active
        global active_status
        global timesleep
        login = self.entry_login.get_text()
        password = self.entry_password.get_text()
        interface=commands.getoutput('route -n')
        interface=interface.split("\n")[2].split(' ')[-1]
        f=open(self.pap,'w')
        line='"'+login+'" * "'+password+'"'
        f.write(line)
        f.close()
        if self.linux_os.find("Ubuntu") != -1:
            lar="/etc/ppp/peers/lar"
            f=open(lar,"w")
            f.write('noipdefault\ndefaultroute\nreplacedefaultroute\nhide-password\nnoauth\npersist\nplugin rp-pppoe.so '+interface+'\nuser "'+login+'"\nusepeerdns')
            f.close()
            os.system("pon lar")
        elif self.linux_os.find("Fedora") != -1:
            lar="/etc/sysconfig/network-scripts/ifcfg-ppp"
            f=open(lar,"w")
            f.write('USERCTL=yes\nBOOTPROTO=dialup\nNAME=DSLppp0\nDEVICE=ppp0\nTYPE=xDSL\nONBOOT=no\nPIDFILE=/var/run/pppoe-adsl.pid\nFIREWALL=NONE\nPING=.\nPPPOE_TIMEOUT=80\nLCP_FAILURE=3\nLCP_INTERVAL=20\nCLAMPMSS=1412\nCONNECT_POLL=6\nCONNECT_TIMEOUT=60\nDEFROUTE=yes\nSYNCHRONOUS=no\nETH='+interface+'\nPROVIDER=DSLppp0\nUSER='+login+'\nPEERDNS=no\nDEMAND=no')
            f.close()
            os.system("ifup ppp0")
            os.system("route add default ppp0")
        self.status.set_from_file("/opt/pppoedi/images/disconnected.png")
        active_status=False
        timesleep=3
        connect_active=True
        if self.checkbutton_savepass.get_active():
            self.save_pass()
    
    def disconnect(self, widget):
        global connect_active
        f=open(self.pap,'w')
        f.close()
        if self.linux_os.find("Ubuntu") != -1:
            os.system("poff lar")
        elif self.linux_os.find("Fedora") != -1:
            os.system("ifdown ppp0")
        self.status.set_from_file("/opt/pppoedi/images/inactive.png")
        connect_active = False
    
class CheckConnection(threading.Thread):
    def __init__(self, status):
        threading.Thread.__init__(self)
        self.status = status
    
    def run(self):
        global quit_pppoedi
        global connect_active
        global active_status
        global timesleep
        threading.Thread.run(self)
        active_status=False
        timesleep=3
        while not quit_pppoedi:
            if connect_active:
                interface=commands.getoutput('route -n')
                interface=interface.split("\n")[2].split(' ')[-1]
                if interface == "ppp0" and not active_status:
                    self.status.set_from_file("/opt/pppoedi/images/connected.png")
                    self.active_status=True
                    timesleep=60
                elif interface != "ppp0" and active_status:
                    self.status.set_from_file("/opt/pppoedi/images/disconnected.png")
                    self.active_status=False
                    timesleep=3
            time.sleep(timesleep)
if __name__ == '__main__':
    pppoe = Pppoe()
    gtk.main()
