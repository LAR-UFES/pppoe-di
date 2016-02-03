#!/bin/bash
rm /usr/share/dbus-1/system-services/com.lar.PppoeDi.service
rm /usr/share/polkit-1/actions/com.lar.pppoedi.policy
rm /etc/dbus-1/system.d/com.lar.PppoeDi.conf
rm /usr/local/lib/python3.4/dist-packages/PPPoEDI*
rm -rf /usr/local/lib/python3.4/dist-packages/PPPoEDI*
rm /usr/lib/python3.4/site-packages/PPPoEDI*
rm -rf /usr/lib/python3.4/site-packages/PPPoEDI*
rm /usr/local/bin/pppoedi
rm /usr/local/bin/pppoedi-service
rm /usr/bin/pppoedi
rm /usr/bin/pppoedi-service
rm -rf build
rm -rf /usr/share/pppoedi
rm /usr/share/applications/pppoedi.desktop
rm -rf /usr/local/lib/python3.4/dist-packages/pppoediplugin
rm -rf /usr/lib/python3.4/site-packages/pppoediplugin
rm -rf pppoedi/__pycache__
rm pppoediplugin/*.pyc
rm *.pyc
rm script/*.pyc
