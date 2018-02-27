#!/usr/bin/env python3

from subprocess import getoutput
import os

from pppoediplugin.CheckConnectionCli import CheckConnectionCli
from pppoediplugin.Settings import Settings

import dbus
#from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib


import sys
import signal
import time
import getpass

class PppoeDiCli(object):
    def __init__(self):
        object.__init__(self)
        self.pap_secrets_file = '/etc/ppp/pap-secrets'
        self.set_distro()
        self.settings = Settings()
        self.current_desktop = os.getenv("XDG_CURRENT_DESKTOP")
        self.initialize_pppoedi_bus()
        self.check_conn = CheckConnectionCli(self)
        self.check_conn.start()
        try:
            self.login = input('Login: ')
            self.password = getpass.getpass()
            print('\033[93m'+"Use Ctrl-C to disconnect"+'\033[0m')
            self.connect()
            GLib.MainLoop().run()
        except KeyboardInterrupt:
            self.quit_pppoe()

    def initialize_pppoedi_bus(self):
        system_bus = dbus.SystemBus()
        try:
            self.pppoedi_bus = system_bus.get_object("com.lar.PppoeDi","/PppoeDiService")
            self.pppoedi_bus_interface = dbus.Interface(self.pppoedi_bus, "com.lar.PppoeDi")
        except dbus.DBusException:
            #TODO: add pop-up
            sys.exit(1)
    
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
            print('\033[91m'+"System is not supported."+'\033[0m')
            #TODO: add pop-up
            sys.exit(1)

    def quit_pppoe(self):
        self.settings.quit_pppoedi = True
        if self.settings.connect_active:
            self.disconnect()
        self.pppoedi_bus_interface.Exit()

        GLib.MainLoop().quit()

    def connect(self):
        #route = getoutput('route -n')
        route = getoutput('ip route show')

        #gw=route.split("\n")[2].split(' ')[9]
        gw=route.split('\n')[0].split(' ')[2]
        net_list=["200.137.66.0/24","10.9.10.0/24","10.10.10.0/24"]
        for net in net_list:
            if self.linux_distro_type == 1:  # Se a distro e baseada em Debian
                self.pppoedi_bus_interface.RouteAddNetGw(net,gw)
            elif self.linux_distro_type == 2:  # Se a distro e baseada em
                self.pppoedi_bus_interface.RouteAddNetGwF(net,gw)
            else:
                print('\033[91m'+"System is not supported."+'\033[0m')
                sys.exit(1)

        line='"'+self.login+'" * "'+self.password+'"'
        self.pppoedi_bus_interface.PrintToFile(line,self.pap_secrets_file)

        #interface = route.split("\n")[2].split(' ')[-1]
        interface = route.split('\n')[0].split(' ')[4]

        if self.linux_distro_type == 1:  # Se a distro e baseada em Debian
            peer_lar="/etc/ppp/peers/lar"
            config_peer='noipdefault\ndefaultroute\nreplacedefaultroute\n' + \
                        'hide-password\nnoauth\npersist\nplugin rp-pppoe.' + \
                        'so '+interface+'\nuser "'+self.login+'"\nusepeerdns'
            self.pppoedi_bus_interface.PrintToFile(config_peer,peer_lar)
            interface="lar"
            self.pppoedi_bus_interface.Pon(interface)
            '''
            release=getoutput("lsb_release -r")
            if self.current_desktop == "MATE" or (self.current_desktop == "Unity" and release.find("15.10") != -1):
                time.sleep(3.5)
                interface="ppp0"
                self.pppoedi_bus_interface.RouteAddDefault(interface)
            '''
        elif self.linux_distro_type == 2:  # Se a distro e baseada em
            # RHEL/Fedora
            peer_lar="/etc/sysconfig/network-scripts/ifcfg-ppp"
            config_peer='USERCTL=yes\nBOOTPROTO=dialup\nNAME=DSLppp0\nDEV' + \
                        'ICE=ppp0\nTYPE=xDSL\nONBOOT=no\nPIDFILE=/var/run' + \
                        '/pppoe-adsl.pid\nFIREWALL=NONE\nPING=.\nPPPOE_TI' + \
                        'MEOUT=80\nLCP_FAILURE=3\nLCP_INTERVAL=20\nCLAMPM' + \
                        'SS=1412\nCONNECT_POLL=6\nCONNECT_TIMEOUT=60\nDEF' + \
                        'ROUTE=yes\nSYNCHRONOUS=no\nETH='+interface+'\nPR' + \
                        'OVIDER=DSLppp0\nUSER='+self.login+'\nPEERDNS=no\nDEMAND=no'
            self.pppoedi_bus_interface.PrintToFile(config_peer,peer_lar)
            interface="ppp0"
            self.pppoedi_bus_interface.Ifup(interface)
            self.pppoedi_bus_interface.RouteAddDefaultF(interface)
        else:
            print('\033[91m'+"System is not supported."+'\033[0m')
            sys.exit(1)

        self.settings.active_status = False
        self.settings.connect_active = True

    def disconnect(self):
        self.pppoedi_bus_interface.FileBlank(self.pap_secrets_file)

        if self.linux_distro_type == 1:
            interface="lar"
            self.pppoedi_bus_interface.Poff(interface)
        elif self.linux_distro_type == 2:
            interface="ppp0"
            self.pppoedi_bus_interface.Ifdown(interface)
        else:
            print('\033[91m'+"System is not supported."+'\033[0m')
            sys.exit(1)

        self.settings.connect_active = False