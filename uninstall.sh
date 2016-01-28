#!/bin/bash
rm /usr/share/dbus-1/system-services/com.lar.PppoeDi.service
rm /usr/share/polkit-1/actions/com.lar.pppoedi.policy
rm /etc/dbus-1/system.d/com.lar.PppoeDi.conf
rm /usr/local/lib/python3.4/dist-packages/PPPoEDI-0.0.91.egg-info
rm /usr/local/bin/pppoedi
rm /usr/local/bin/pppoedi-service
rm -rf build
rm -rf /usr/share/pppoedi
#rm /usr/share/icons/pppoedi.xpm
rm /usr/share/applications/pppoedi.desktop
rm -rf /usr/local/lib/python3.4/dist-packages/pppoedi
rm -rf pppoedi/__pycache__
rm pppoedi/*.pyc
