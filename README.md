# stratux-radar-display
Implementation of a standalone Radar display for Stratux Europe Edition. Can run on a separate Raspberry (e.g. Zero W or Zero 2 W). Reads the aircraft data from Stratux and displays them on the specified display. The newest version now has a user interface included. You can connect 3 pushbuttons to the device and use them for changing the radar radius, the height difference and sound options. A clock with a stop and lap timer, a g-meter, an artificial horizon, a compass (based on GPS) and a VSI display are also implemented.
- update in version 1.4: external sound connection is now supported by using a USB sound card (approx. 4 Euro). With that you can connect your display to your intercom. This external sound output is also functioning on the stratux only, without an additional Zero.

Current supported displays are:
- Oled Display 1.5 inch (waveshare)
- Epaper Display 3.7 inch (waveshare)

More displays can be integrated.
You can find 3D printer files for cases of both variants in the repo (no-code). The Oled-case is designed for a 2 1/4 inch mounting hole, the E-paper case is designed for a 3 1/8 inch (80 mm) mounting hole. Instructions e.g. how to build the 2 1/4 Oled case can be found in the wiki (https://github.com/TomBric/stratux-radar-display/wiki/All-in-one-aluminum-case-(Stratux-with-oled-display).

Find below a photo of the current supported displays
- the oled display is relatively small, but can be build into a 2 1/4" or larger instrument mounting hole
- the epaper display is larger and has optimal readability in sunlight. As e-paper it has a slower update of approx. twice per second. For the radar display this update rate is appropriate

![Display photo](https://github.com/TomBric/stratux-radar-display/blob/main/no-code/images/StratuxRadar.jpg)

## Hardware-List
- Raspberry Hardware: Since the code is pure python, no special hardware is required. I recommend a current "raspbian standard desktop os" as operating system. Performance requirements are not so high, so I recommend a "Rasperry Zero or Zero 2 W 512MByte RAM". Normal Raspberry 3B or 4 are also possible. The Raspi Zero has the smallest form factor and best battery consumption. 
- Waveshare 18381 3.7inch e-Paper Display + Waveshare Universal e-Paper Raw Panel Driver HAT 13512. Please make sure to switch the "Display Config" switch to A.
(Alternatively Waveshare 18057 3.7inch e-Paper HAT: Directly mountable on the Raspi as a HAT, if you buy an Raspi Zero WH, but then you can't connect the buttons).

![Epaper photo](https://github.com/TomBric/stratux-radar-display/blob/main/no-code/images/Epaper_3in7.jpg)

- Oled-Display: Waveshare 14747, 128x128, General 1.5inch RGB OLED display Module
   ![Oled photo](https://github.com/TomBric/stratux-radar-display/blob/main/no-code/images/Oled_1in5.jpg)
   
 - Optional power supply suggestion: If you need a reliable display power supply in your airplane, I have good experiences with small step-down converters LM2596. Then you can use the aircraft power supply (up to 40V). Calibrate the LM2596 at home for a power output at 5 V e.g. using an old laptop power supply. LM2596 also work well for the stratux itself. No problems with radio noise.  
   
 # Hardware connection of the OLED 1.5 inch display
 
| Connection  | PIN# on Raspberry  | Cable color |
|:-----------:|:------------------:|:-----------:|
| VCC | 17 | red |
| GND | 20 | black |
| DIN/MOSI | 19 | blue |
| CLK/SCK | 23| yellow  |
| CS/CE0 | 24 | orange |
| DC | 18 | green |
| RST | 22 | white |

# Hardware connection of the Epaper 3.7 inch display (if not using the hat version)
 
| Connection  | PIN# on Raspberry  |
|:-----------:|:------------------:|
| VCC | 17 |
| GND | 20 | 
| DIN/MOSI | 19 |
| CLK/SCK | 23|
| CS/CE0 | 24 |
| DC | 22 | 
| RST | 11 |
| BUSY | 18 |

Remark: If you have a barometric sensor or ahrs connected you may have conflict with GPIO Pin 11. 
You can also use PIN 16 (GPIO 23) for the RST line.

To do that please modify in /home/pi/stratux-radar-display/main/displays/Epaper_3in7/epdconfig.py line 38/39:
```
   # RST_PIN         = 17    # if directly as hat
   RST_PIN = 23  # for cable mounted in stratux on different GPIO 23, which is PIN 16
```

# Hardware connection of the pushbuttons for the user interface
 
| Pushbutton  | PIN# on Raspberry  |
|:-----------:|:------------------:|
| Left | 37 |
| Middle | 38 | 
| Right | 40 | 

All pushbuttons are used as pull down. Connect the other side of all buttons to GND (PIN39).
   
   ## Software Installation Instructions
   ### Standard setup
   1. Download the image under Releases/Assets to your local computer. Image with "oled" is preconfigured for the Oled 1.5 inch display. Image with "epaper" is the version for the waveshare 3.7 inch epaper displays. Both versions will support Bluetooth
   2. Flash the image using Raspberry Pi Imager (select "OwnImage") or Win32DiskImager to your SD card (32 GB cards recommended)
   3. Insert the SD into you raspberry and let it boot. It should automatically startup and connect to the Stratux-Europe edition. 
   Remark: Current configuration is for Stratux-Europe on IP address 192.168.10.1. If you have a different configuration please update /home/pi/stratux-radar-display/image/stratux_radar.sh accordingly.
   
   ### Expert setup 
   1. Configure a clean Raspbian installation on your SD card. E.g. using Raspberry Pi Imager. Image to flash is the standard image "Raspbian Pi OS (recommended)". 
   2. Setup your main stratux in the following way:  Install version eu-027 on ther stratux or newer. Go to "Settings" and set Wifi-Mode: AP+Client. Enable "Internet-Passthrough" as well. Then "Add wifi client network" and add the data of your local home network. This all enables your stratux to have Internet connection and gives the display the possibility to access internet as well. 
   3. Startup your Stratux and boot your new raspberry. Connect your PC/workstation to the standard "stratux WLAN" network and figure out the IP-adress of your display-raspberry, e.g. by using "arp -a".
   4. From your workstation open a remote shell on the display-raspberry:  ssh pi@192.168.x.x. Password is standard for the pi.
   5. Clone the stratux-radar-display repository by the command: "git clone https://github.com/TomBric/stratux-radar-display.git"
   6. Execute the configuration script as user pi. "/bin/bash /home/pi/stratux-radar-display/image/configure_radar.sh".  This will take some time since it does an update on the pi. 
   7. Depending on your display modify /home/pi/stratux-radar-display/image/stratux_radar.sh. In paramater "-c" enter the IP address of your stratux and in parameter "-d" the device. E.g.
         - cd /home/pi/stratux-radar-display/main && python3 radar.py -s -d Oled_1in5 -c 192.168.10.1 &            
         - cd /home/pi/stratux-radar-display/main && python3 radar.py -s -r -d Epaper_3in7 -c 192.168.10.1 & 
   8. The configuration skript will make an entry in crontab of user pi, so that radar will start automatically after reboot. 

   
   ### Installation on a standard stratux device (for stratux versions eu027 or newer!)
   stratux-radar-display can run also directly on your stratux device. You can find an example of a case with everything installed in the [wiki](https://github.com/TomBric/stratux-radar-display/wiki/All-in-one-aluminum-case-(Stratux-with-oled-display)). Connect the displays to the GPIO pins of the Stratux. 
   Installation is only for expert users! To install the software perform the following steps:
   
   1. Connect your stratux to a network, e.g. by integrating into your WLAN: go to "Settings" and add your local wifi network.
   This will connect your stratux to your local wlan. Alternatively connect Stratux via network cable.
   2. Enable a writeable persistent filesystem in the settings tab by setting "Persistent Logging". 
   3. Reboot and log on to your Stratux as user pi, directory /home/pi
   4. Clone the stratux repository by "git clone https://github.com/TomBric/stratux-radar-display.git"
   3. Execute the configuration skript: "/bin/bash /home/pi/stratux-radar-display/image/configure_radar_on_stratux.sh". It will take some time.
   4. Configure the startup skript "image/stratux-radar.sh": remove the option "-s" and use the corresponding display option with "-d Oled_1in5" or "-d Epaper_3in7"
   5. Reboot stratux. If everything if installed correctly, the display software will automatically startup.

The Oled display uses different GPIO-Pins as the baro-sensor, so there is no conflict. Also the e-Paper display can be connected (not the HAT version) with the baro and ahrs sensors in place.
   Remark: Bluetooth is currently not properly supported by Stratux, so if you want audio output to your headset, please use Raspian OS Desktop on a Raspberry Zero 2 or Zero W.
   
   ### External Sound output
   
   You can connect your stratux device with your intercom if it has an input for external audio (e.g. TQ KRT2 has one). This is possible on the Pi Zero or the PI3B with an external USB sound card (using the builtin headphone output does not work on the Pi3B). I used a simple "3D USB 5.1 Sound card" available for 4 Euro. The sound volume can be controlled via the option "-y" or can be modified with the pushbuttons under ->Status-> Net/Opt -> External Volume.
   The following link gives some good hints, which USB sound card can be used and it also shows how to solder it to the Pi Zero, if you do not want an adapter or space is an issue (https://www.raspberrypi-spy.co.uk/2019/06/using-a-usb-audio-device-with-the-raspberry-pi/)
   
   ### Bluetooth devices
   
   stratux-radar-display will automatically connect the your headset if their bluetooth is switched on. 
   But once you need to do the pairing of a new bluetooth device. 
   
   There are two options for pairing:
   
   **Option 1: Directly on the device via buttons:**
   
   * Change to Status-Mode (long press middle button, to change from Radar-> Timer -> AHRS -> Status)
   * Press "scan" (right button). The display now scans 30 secs for new devices. Set your headset as visible and it will be detected (For Bose A20 this is a 5 second press on the Bluetooth-Button until it flashes blue-red)
   * A list of detected devices is shown, press "yes" for the detected device. Sometimes you need to repeat the scan until your headset is detected.
      
   **Option 2: via ssh and bluetoothctl**
   
   * Logon on your radar as user pi:  ssh pi@192.168.x.x
   * Start bluetoothctl:   
   ```
      -> bluetoothctl
      -> scan on      set your device in pairing mode (for Bose A20, do a 5 sec press on the bluetooth button until it flashes magenta)
      -> wait till your device is displayed, this will look like:  
            [NEW] Device 04:52:C7:02:C0:01 Bose A20,              04:52:C7:02:C0:01 is the device id, which will be different for you
      -> scan off
      -> trust <device-id>   <replace with your device id>
      -> pair <device-id>, eventually your pin is requested (for Bose A20 enter "0000")
      -> connect <device-id>
   If everything works fine, the pi displays connected and your device name.
      -> exit
   ```
   
   The bluetooth configuration is now ready and each time the radar has your device in reachability, it will connect. On the display the bluetooth symbol will be visible in the right corner.
   
 # Manual of stratux-radar-display (user interface with 3 pushbuttons) (thanks SiggiS)
### In all screen modes:
   - middle button (>1 sec): switch to next mode (radar -> timer -> ahrs -> radar)
   - left button (>1 sec): start shutdown, press any other button to cancel shutdown
   - after shutdown, display can be reactivated by switching on/off
   
### Radar screen mode:
   - left button short: change radar range (2nm -> 5nm -> 10nm -> 40nm)
   - middle button short: enable/disable sound (if bluetooth speaker/headset is connected)
   - right button short: change height difference for traffic (1000ft -> 2000 ft -> 5000 ft -> 10k ft -> 50k ft)
   - right button long: screen refresh. This is relevant for Epaper only since it becomes "dirty" over time with partial refresh.
     
![Radar](https://github.com/TomBric/stratux-radar-display/blob/main/no-code/images/Epaper-Radar-Mode.jpg)

Recommended setting for normal piston aircraft is 5 nm and 2000 ft.

### Timer screen mode:
   - right button short:  start or stop timer (displayed in the middle)
   - left button short: start lap-timer (displayed on bottom)
   - middle short: change to countdown-setting. Here a countdown timer can be set. If the countdown runs down to 0:00, this will also be signalled by sound output in your headset
   - press middle short again to end countdown-setting. Countdown will be started, wenn timer is started. It timer is already running, countdown will start as soon as you leave the countdown setting mode

   - in countdown-setting mode:
      - press middle short again to end countdown-setting. Countdown will be started, wenn timer is started. It timer is already running, countdown will start as soon as you leave the countdown setting mode
      - press left button to increase countdown time by 10 mins
      - press right button to increase countdown time by 1 mins
      - max countdown time is 2 hours. If you set countdown time > 2 h, countdone timer will be cleared

    
![Timer](https://github.com/TomBric/stratux-radar-display/blob/main/no-code/images/Epaper-TimerMode.jpg)

 ### AHRS mode:
 - no special interaction, press long middle for next mode

![AHRS](https://github.com/TomBric/stratux-radar-display/blob/main/no-code/images/Epaper-AHRS-Mode.jpg)

### G-Meter mode:
    - press short right to reset min and max values
    - press long middle for next mode

![Gmeter](https://github.com/TomBric/stratux-radar-display/blob/main/no-code/images/Epaper-G-Meter-Mode.jpg)

### Compass mode:
    - press long middle for next mode

![Compass](https://github.com/TomBric/stratux-radar-display/blob/main/no-code/images/Epaper-CompassMode.jpg)

# Shell command parameters
```
usage: radar.py [-h] -d DEVICE [-b] [-sd] [-n] [-t] [-a] [-x] [-g] [-o] [-i] [-z] [-c CONNECT] [-v] [-r] [-e]
                [-y EXTSOUND]

Stratux radar display

optional arguments:
  -h, --help            show this help message and exit
  -d DEVICE, --device DEVICE
                        Display device to use
  -b, --bluetooth       Bluetooth speech warnings on
  -sd, --speakdistance  Speech with distance
  -n, --north           Ground mode: always display north up
  -t, --timer           Start mode is timer
  -a, --ahrs            Start mode is ahrs
  -x, --status          Start mode is status
  -g, --gmeter          Start mode is g-meter
  -o, --compass         Start mode is compass
  -i, --vsi             Start mode is vertical speed indicator
  -z, --strx            Start mode is stratux-status
  -c CONNECT, --connect CONNECT
                        Connect to Stratux-IP
  -v, --verbose         Debug output on
  -r, --registration    Display registration no (Epaper only)
  -e, --fullcircle      Display full circle radar (Epaper only)
  -y EXTSOUND, --extsound EXTSOUND
                        Ext sound on with volume [0-100]
  ```


