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
import dbus
from dbus.mainloop.glib import DBusGMainLoop

quit_pppoedi = False
connect_active = False
active_status = False
timesleep = 3

path_pppoe="/opt/pppoe-plugin/"
sudo_password='1a2b3c4d'

class Pppoe(object):
    def __init__(self):
        object.__init__(self)
        builder = gtk.Builder()
        builder.add_from_file(path_pppoe+"/src/pppoedi.glade")
        self.window = builder.get_object("main_window")
        self.entry_login = builder.get_object("entry_login")
        self.entry_password = builder.get_object("entry_password")
        self.entry_password_sudo = builder.get_object("entry_password_sudo")
        self.status = builder.get_object("status")
        self.checkbutton_savepass = builder.get_object("checkbutton_savepass")
        self.window.show()
        builder.connect_signals({"gtk_main_quit": self.quit_pppoe,
                                 "on_entry_login_activate": self.connect,
                                 "on_entry_password_activate": self.connect,
                                 "on_button_connect_clicked": self.connect,
                                 "on_button_disconnect_clicked": self.disconnect,
                                 "on_entry_password_sudo_activate": self.connect})

        self.pap = '/etc/ppp/pap-secrets'

        distro_name = ''

        with open('/etc/os-release', 'r') as f:
            while distro_name.find('NAME') == -1:
                distro_name = f.readline()

        debian_like_distro = ['Ubuntu',
                              'Ubuntu Studio',
                              'Ubuntu MATE'
                              'Kubuntu',
                              'Xubuntu',
                              'Lubuntu',
                              'Linux Mint',
                              'Kali Linux',
                              'Zorin OS',
                              'deepin',
                              'LXLE',
                              'elementary OS',
                              'Bodhi Linux',
                              'Peppermint OS',
                              'siduction',
                              'Raspbian',
                              'Debian']
        fedora_like_distro = ['Fedora',
                              'Red Hat Enterprise Linux',
                              'CentOS',
                              'ClearOS',
                              'Pidora']

        if distro_name in debian_like_distro:
            self.linux_distro_type = 1
        elif distro_name in fedora_like_distro:
            self.linux_distro_type = 2

        self.file_pppoe = os.getenv('HOME') + '/.pppoedi'

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
        cmd="route add -net 200.137.66.0/24 gw "+net
        os.system('echo %s|sudo -S %s' % (sudo_password, cmd))
        DBusGMainLoop(set_as_default=True)
        bus = dbus.SessionBus()

        if self.linux_distro_type == 1:
            session = commands.getoutput('ps -A | egrep -i "gnome|kde|mate|cinnamon"')

            if session.find('mate-session') != -1:
                bus.add_match_string("type='signal',interface='org.gnome.ScreenSaver'")
            elif session.find('gnome-session') != -1:
                bus.add_match_string("type='signal',interface='com.ubuntu.Upstart0_6'")
        elif self.linux_distro_type == 2:
            bus.add_match_string("type='signal',interface='org.gnome.ScreenSaver'")
        bus.add_message_filter(filter_cb)

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
        sudo_password = self.entry_password_sudo.get_text()
        self.entry_login.set_property("editable", False)
        self.entry_password.set_property("editable", False)
        self.entry_password_sudo.set_property("editable", False)
        interface=commands.getoutput('route -n')
        interface=interface.split("\n")[2].split(' ')[-1]
        home=os.getenv("HOME")
        f=open(home+"/aux",'w')
        line='"'+login+'" * "'+password+'"'
        f.write(line)
        f.close()
        cmd='mv '+home+'/aux '+self.pap
        os.system('echo %s|sudo -S %s' % (sudo_password, cmd))
        if self.linux_distro_type == 1:
            lar="/etc/ppp/peers/lar"
            f=open(home+"/aux",'w')
            text='noipdefault\ndefaultroute\nreplacedefaultroute\nhide-password\nnoauth\npersist\nplugin rp-pppoe.so '+interface+'\nuser "'+login+'"\nusepeerdns'
            f.write(text)
            f.close()
            cmd='mv '+home+'/aux '+lar
            os.system('echo %s|sudo -S %s' % (sudo_password, cmd))
            cmd="pon lar"
            os.system('echo %s|sudo -S %s' % (sudo_password, cmd))
        elif self.linux_distro_type == 2:
            lar="/etc/sysconfig/network-scripts/ifcfg-ppp"
            f=open(home+"/aux","w")
            f.write('USERCTL=yes\nBOOTPROTO=dialup\nNAME=DSLppp0\nDEVICE=ppp0\nTYPE=xDSL\nONBOOT=no\nPIDFILE=/var/run/pppoe-adsl.pid\nFIREWALL=NONE\nPING=.\nPPPOE_TIMEOUT=80\nLCP_FAILURE=3\nLCP_INTERVAL=20\nCLAMPMSS=1412\nCONNECT_POLL=6\nCONNECT_TIMEOUT=60\nDEFROUTE=yes\nSYNCHRONOUS=no\nETH='+interface+'\nPROVIDER=DSLppp0\nUSER='+login+'\nPEERDNS=no\nDEMAND=no')
            f.close()
            cmd='mv '+home+'/aux '+lar
            os.system('echo %s|sudo -S %s' % (sudo_password, cmd))
            cmd="ifup ppp0"
            os.system('echo %s|sudo -S %s' % (sudo_password, cmd))
            cmd="route add default ppp0"
            os.system('echo %s|sudo -S %s' % (sudo_password, cmd))
        self.status.set_from_file(path_pppoe+"/images/disconnected.png")
        active_status=False
        timesleep=3
        connect_active=True
        if self.checkbutton_savepass.get_active():
            self.save_pass()
    
    def disconnect(self, widget):
        global connect_active
        self.entry_login.set_property("editable", True)
        self.entry_password.set_property("editable", True)
        self.entry_password_sudo.set_property("editable", True)
        sudo_password = self.entry_password_sudo.get_text()
        cmd='bash -c "echo  > '+self.pap+'"'
        os.system('echo %s|sudo -S %s' % (sudo_password, cmd))
        if self.linux_distro_type == 1:
            cmd="poff lar"
            os.system('echo %s|sudo -S %s' % (sudo_password, cmd))
        elif self.linux_distro_type == 2:
            cmd="ifdown ppp0"
            os.system('echo %s|sudo -S %s' % (sudo_password, cmd))
        self.status.set_from_file(path_pppoe+"/images/inactive.png")
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
                interface=commands.getoutput('ifconfig ppp0 | grep inet')
                if interface != "" and not active_status:
                    self.status.set_from_file(path_pppoe+"/images/connected.png")
                    self.active_status=True
                    timesleep=60
                elif interface == "" and active_status:
                    self.status.set_from_file(path_pppoe+"/images/disconnected.png")
                    self.active_status=False
                    timesleep=3
            time.sleep(timesleep)

def filter_cb(bus, message):
    if message.get_member() != "EventEmitted":
        return
    args = message.get_args_list()
    if args[0] == "desktop-lock":
        pppoe.disconnect(None)

if __name__ == '__main__':
    pppoe = Pppoe()
    gtk.main()
