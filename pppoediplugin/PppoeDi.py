#!/usr/bin/env python3

from subprocess import getoutput
import os

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk

from pppoediplugin.CheckConnection import CheckConnection
from pppoediplugin.Settings import Settings

import dbus
from dbus.mainloop.glib import DBusGMainLoop
import sys
import signal

class PppoeDi(object):
    def __init__(self):
        object.__init__(self)
        builder = gtk.Builder()
        glade_file=os.path.abspath(__file__).replace("PppoeDi.py","ui/pppoedi.glade")
        builder.add_from_file(glade_file)
        self.window = builder.get_object("main_window")
        self.entry_login = builder.get_object("entry_login")
        self.entry_password = builder.get_object("entry_password")
        self.button_conn_disconn = builder.get_object("button_conn_disconn")
        self.window.show()
        builder.connect_signals({"gtk_main_quit": self.quit_pppoe,
                                 "on_entry_login_activate": self.conn_disconn,
                                 "on_entry_password_activate": self.conn_disconn,
                                 "on_button_conn_disconn_clicked": self.conn_disconn})
        self.pap_secrets_file = '/etc/ppp/pap-secrets'
        self.set_distro()
        self.settings = Settings()
        self.initialize_dbus_session()
        self.initialize_pppoedi_bus()
        self.check_conn = CheckConnection(self)
        self.check_conn.start()
        self.disconnect()
        self.showAlertMsg('Lembre-se de deslogar do PPPoE ao sair do computador.')
    
    def showAlertMsg(self, msg, messageType=gtk.MessageType.WARNING):
        msgDialog = gtk.MessageDialog(parent=self.window, type=messageType, buttons=gtk.ButtonsType.OK,message_format=msg)
        if msgDialog.run():
            msgDialog.destroy()
            return None

    def initialize_pppoedi_bus(self):
        system_bus = dbus.SystemBus()
        try:
            self.pppoedi_bus = system_bus.get_object("com.lar.PppoeDi","/PppoeDiService")
            self.pppoedi_bus_interface = dbus.Interface(self.pppoedi_bus, "com.lar.PppoeDi")
        except dbus.DBusException:
            self.showAlertMsg("Serviço ppppoedi não pode ser inicializado.",gtk.MessageType.ERROR)
            sys.exit(1)

    def initialize_dbus_session(self):
        DBusGMainLoop(set_as_default=True)
        session_bus = dbus.SessionBus()
        self.current_desktop = os.getenv("XDG_CURRENT_DESKTOP")
        if self.current_desktop == "Unity":#TUDO: Ubuntu 17 diferente
            session_bus.add_match_string("type='signal',interface='com.ubuntu.Upstart0_6'")
        elif self.current_desktop == "MATE":
            session_bus.add_match_string("type='signal',interface='org.mate.ScreenSaver'")
        elif self.current_desktop == "GNOME":
            session_bus.add_match_string("type='signal',interface='org.gnome.ScreenSaver'")
        elif self.current_desktop == "X-Cinnamon":
            session_bus.add_match_string("type='signal',interface='org.cinnamon.ScreenSaver'")
        elif self.current_desktop == "LXDE":
            return
        #elif self.current_desktop == "XFCE":
            #return
        else:
            self.showAlertMsg("Sistema não suportado.",gtk.MessageType.ERROR)
            sys.exit(1)
        signal.signal(signal.SIGTERM, self.dbus_quit)
        session_bus.call_on_disconnection(self.dbus_quit)
        session_bus.add_message_filter(self.filter_cb)

    def set_distro(self):
        distro_name = ''  # Inicializa a variavel que armazena o nome da
        # distribuicao em uso

        # Le o nome da distribuicao em uso no arquivo '/etc/os-release' e
        # armazena na variavel 'distro_name'
        with open('/etc/os-release', 'r') as f:
            while 'NAME' not in distro_name:
                distro_name = f.readline()

        # Lista com as distribuicoes mais populares baseadas em Debian
        debian_like_distro = ('Ubuntu', 'Ubuntu Studio', 'Ubuntu MATE',
                              'Kubuntu', 'Xubuntu', 'Lubuntu', 'Linux Mint',
                              'Kali Linux', 'Zorin OS', 'deepin', 'LXLE',
                              'elementary OS', 'Bodhi Linux', 'Peppermint OS',
                              'siduction', 'Raspbian', 'Debian')

        # Lista com as distribuicoes mais populares baseadas em Fedora
        fedora_like_distro = ('Fedora', 'Red Hat Enterprise Linux', 'CentOS',
                              'ClearOS', 'Pidora')

        # Inicializa a variavel que armazena o tipo da distribuicao em uso
        # Assume o valor '1' se for baseada em Debian
        # Assume o valor '2' se for baseada em RHEL/Fedora
        self.linux_distro_type = 0

        # Procura cada item da lista de distros baseadas em Debian como
        # substring do nome da distro em uso
        if any(distro in distro_name for distro in debian_like_distro):
            self.linux_distro_type = 1
        # Procura cada item da lista de distros baseadas em RHEL/Fedora como
        # substring do nome da distro em uso
        #elif any(distro in distro_name for distro in fedora_like_distro):
            #self.linux_distro_type = 2
        else:
            self.showAlertMsg("Sistema não suportado.",gtk.MessageType.ERROR)
            sys.exit(1)

    def quit_pppoe(self, widget):
        self.settings.quit_pppoedi = True

        if self.settings.connect_active:
            self.disconnect()

        self.pppoedi_bus_interface.Exit()
        #self.check_conn.terminate()
        gtk.main_quit()

    def conn_disconn(self, widget):
        if self.settings.connect_active:
            self.disconnect()
        else:
            self.connect()

    def connect(self):
        login = self.entry_login.get_text()
        password = self.entry_password.get_text()

        self.entry_login.set_editable(False)
        self.entry_login.set_has_frame(False)
        self.entry_login.set_can_focus(False)
        self.entry_login.set_sensitive(False)
        self.entry_password.set_editable(False)
        self.entry_password.set_has_frame(False)
        self.entry_password.set_can_focus(False)
        self.entry_password.set_sensitive(False)
        self.button_conn_disconn.set_label("Conectando...")
        self.button_conn_disconn.set_sensitive(False)

        #route = getoutput('route -n')
        route = getoutput('ip route show')

        #gw=route.split("\n")[2].split(' ')[9]
        gw=route.split('\n')[0].split(' ')[2]
        net_list=[]
        if gw == '192.168.1.1' or gw == '192.168.2.1':
            net_list=["10.10.10.0/24"]
        else:
            net_list=["200.137.66.0/24","10.9.10.0/24"]
        for net in net_list:
            if self.linux_distro_type == 1:  # Se a distro e baseada em Debian
                self.pppoedi_bus_interface.RouteAddNetGw(net,gw)
            elif self.linux_distro_type == 2:  # Se a distro e baseada em
                self.pppoedi_bus_interface.RouteAddNetGwF(net,gw)
            else:
                #TODO: add pop-up
                sys.exit(1)

        line='"'+login+'" * "'+password+'"'
        self.pppoedi_bus_interface.PrintToFile(line,self.pap_secrets_file)

        #interface = route.split("\n")[2].split(' ')[-1]
        interface = route.split('\n')[0].split(' ')[4]
        

        if self.linux_distro_type == 1:  # Se a distro e baseada em Debian
            peer_lar="/etc/ppp/peers/lar"
            config_peer='noipdefault\ndefaultroute\nreplacedefaultroute\n' + \
                        'hide-password\nnoauth\npersist\nplugin rp-pppoe.' + \
                        'so '+interface+'\nuser "'+login+'"\nusepeerdns'
            self.pppoedi_bus_interface.PrintToFile(config_peer,peer_lar)
            interface="lar"
            self.pppoedi_bus_interface.Pon(interface)
        elif self.linux_distro_type == 2:  # Se a distro e baseada em
            # RHEL/Fedora
            peer_lar="/etc/sysconfig/network-scripts/ifcfg-ppp"
            config_peer='USERCTL=yes\nBOOTPROTO=dialup\nNAME=DSLppp0\nDEV' + \
                        'ICE=ppp0\nTYPE=xDSL\nONBOOT=no\nPIDFILE=/var/run' + \
                        '/pppoe-adsl.pid\nFIREWALL=NONE\nPING=.\nPPPOE_TI' + \
                        'MEOUT=80\nLCP_FAILURE=3\nLCP_INTERVAL=20\nCLAMPM' + \
                        'SS=1412\nCONNECT_POLL=6\nCONNECT_TIMEOUT=60\nDEF' + \
                        'ROUTE=yes\nSYNCHRONOUS=no\nETH='+interface+'\nPR' + \
                        'OVIDER=DSLppp0\nUSER='+login+'\nPEERDNS=no\nDEMAND=no'
            self.pppoedi_bus_interface.PrintToFile(config_peer,peer_lar)
            interface="ppp0"
            self.pppoedi_bus_interface.Ifup(interface)
            self.pppoedi_bus_interface.RouteAddDefaultF(interface)
        else:
            #TODO: add pop-up
            sys.exit(1)

        self.settings.active_status = False
        self.settings.connect_active = True

    def disconnect(self):
        self.entry_login.set_editable(True)
        self.entry_login.set_has_frame(True)
        self.entry_login.set_can_focus(True)
        self.entry_login.set_sensitive(True)
        self.entry_password.set_editable(True)
        self.entry_password.set_has_frame(True)
        self.entry_password.set_can_focus(True)
        self.entry_password.set_sensitive(True)
        self.button_conn_disconn.set_label("Conectar")
        self.button_conn_disconn.set_sensitive(True)
        self.pppoedi_bus_interface.FileBlank(self.pap_secrets_file)

        if self.linux_distro_type == 1:
            interface="lar"
            self.pppoedi_bus_interface.Poff(interface)
        elif self.linux_distro_type == 2:
            interface="ppp0"
            self.pppoedi_bus_interface.Ifdown(interface)
        else:
            #TODO: add pop-up
            sys.exit(1)

        self.settings.connect_active = False

    def main(self):
        gtk.main()

    def dbus_quit(self, conn):
        self.disconnect()
    
    def filter_cb(self, bus, message):
        if message.get_member() == "1" or\
           message.get_member() == "Disconnected":
                self.quit_pppoe(None)
        elif message.get_member() == "EventEmitted" or message.get_member() == 'ActiveChanged':
            args = message.get_args_list()
            if args[0] == "session-end":
                self.quit_pppoe(None)
