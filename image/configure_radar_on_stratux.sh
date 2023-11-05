#!/bin/bash

# script configures basic libraries necessary for stratux-radar
# script to be run as pi on stratux (without a zero pi)

# luma files, pip3 and more
#sudo apt-get update -y
sudo apt install python3-pip python3-pil python3-gi -y
sudo apt install zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7 libtiff5 -y
sudo pip3 install luma.oled

#websockets for radar
sudo pip3 install websockets ADS1x15-ADC

# sound configuration for external output
sudo apt install libasound2-dev -y
sudo pip3 install pyalsaaudio

# espeak-ng for sound output
# sudo apt-get update
sudo apt install espeak-ng espeak-ng-data libespeak-ng-dev -y
sudo pip3 install py-espeak-ng

# bluetooth configs
sudo apt install libbluetooth-dev -y
sudo pip3 install pybluez
sudo pip3 install pydbus
#mkdir -p /home/pi/tmp
sudo TMPDIR=/tmp pip3 install --upgrade PILLOW
sudo apt install python3-numpy -y

# get files from repo
# cd /home/pi && git clone https://github.com/TomBric/stratux-radar-display.git

# disable bluetooth in any case, is not working directly on Stratux
#sed -i 's/-b/ /g' /home/pi/stratux-radar-display/image/stratux_radar.sh
# include autostart into crontab, so that radar starts on every boot
#echo "@reboot /bin/bash /home/pi/stratux-radar-display/image/stratux_radar.sh" | crontab -
# only works if crontab is empty, otherwise use
# crontab -l | sed "\$a@reboot /bin/bash /home/pi/stratux-radar-display/image/start_radar" | crontab -

# add the following to /etc/rc.local
# (sleep 30; python3 /root/stratux-radar-display/main/radar.py -z -d Epaper_3in7 -c 192.168.10.1) &

# enable spi
#sudo raspi-config nonint do_spi 0