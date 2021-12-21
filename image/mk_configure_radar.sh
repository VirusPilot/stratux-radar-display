#!/bin/bash

# script configures basic libraries necessary for stratux-radar
# script to be run as root
# called via qemu

# remove desktop packages
apt purge xserver* lightdm* vlc* lxde* chromium* desktop* gnome* gstreamer* gtk* hicolor-icon-theme* lx* mesa* -y
apt-get autoremove -y

# luma files and more
apt-get update -y
apt-get upgrade -y
apt-get install git python3-pip python3-pil -y libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7 libtiff5 -y
pip3 install luma.oled


#websockets for radar
pip3 install websockets

# espeak-ng for sound output
apt-get install espeak-ng espeak-ng-data libespeak-ng-dev -y
pip3 install py-espeak-ng

# bluetooth configs
apt-get install libbluetooth-dev -y
pip3 install pybluez pydbus
pip3 install --upgrade PILLOW
apt purge piwiz -y
# necessary to disable bluetoothmessage "To turn on ..."

# get files from repo
sudo -u pi cd /home/pi && git clone https://github.com/TomBric/stratux-radar-display.git

# include autostart into crontab, so that radar starts on every boot
sudo -u pi echo "@reboot /bin/bash /home/pi/stratux-radar-display/image/stratux_radar.sh" | c
rontab -
# only works if crontab is empty, otherwise use
# crontab -l | sed "\$a@reboot /bin/bash /home/pi/stratux-radar-display/image/start_radar" |
crontab -


# bluetooth configuration
# Enable a system wide pulseaudio server, otherwise audio in non-login sessions is not working
#
# configs in /etc/pulse/system.pa
sed -i '$ a load-module module-bluetooth-discover' /etc/pulse/system.pa
sed -i '$ a load-module module-bluetooth-policy' /etc/pulse/system.pa
sed -i '$ a load-module module-switch-on-connect' /etc/pulse/system.pa

# configs in /etc/pulse/client.conf to disable client spawns
sed -i '$ a default-server = /var/run/pulse/native' /etc/pulse/client.conf
sed -i '$ a autospawn = no' /etc/pulse/client.conf

# allow user pulse bluetooth access
addgroup pulse bluetooth
addgroup pi pulse-access

# start pulseaudio system wide
cp /home/pi/stratux-radar-display/image/pulseaudio.service /etc/systemd/system/
systemctl --system enable pulseaudio.service
# systemctl --system start pulseaudio.service

# enable spi
# raspi-config nonint do_spi 0

