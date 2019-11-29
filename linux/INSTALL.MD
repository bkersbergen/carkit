## Raspberry Pi: Install Operating System

Raspberry Pi 4B 4GB Starter Kit met heatsink case
https://www.bol.com/nl/p/raspberry-pi-4b-4gb-starter-kit-met-heatsink-case/9200000121607543/

I replaced the slow 16 SD card by a fast 32GB
https://www.bol.com/nl/p/sandisk-ultra-micro-sdhc-32gb-uhs1-a1-met-adapter/9200000080737253 writes 4MB/s on the Pi

### Install NOOBS raspberry PI is pretty straightforward. 
The install will use 7GB of the SDCard.
* during installation, Pi will ask you to set the password for default user ```pi```:
* after installation it will download and install OS updates.
* ```ifconfig``` will tell you the IP of your Pi 

### Setup Remote Access 
run  ```sudo raspi-config```  
* enable ssh-server: Interfacing-options -> ssh -> enable
* enable VNC-server: Interfacing-options -> vnc -> enable

Download and install the RealVNC viewer onto your PC
Connect to your PI's IP using Real VNC viewer. 
The VNC connection is slow at 4K resolution.
Change the background image on the Pi to a single color so remote access will be a lot faster.

Remove monitor, keyboard and mouse from the Pi computer

### Measuring the Temperature of Raspberry Pi 
```pi@localhost: vcgencmd measure_temp```

temp=38.6C

### Modifications to my bashrc
```bash
pi@localhost: sudo vi ~/.bashrc
... 
# note: `sudo ls` runs `ls` command in administrator mode
# route all calls to python (version 2) to python3,
# pip (version 2) to pip3, even in sudo mode
# print CPU temperature on console
alias sudo='sudo '
alias python=python3
alias pip=pip3
vcgencmd measure_temp
 

usb webcam
Apparently most raspberry pi software assumes the webcam is connected 
via the header on the rpi board.
```bash
pi@raspberrypi:~ $ vcgencmd get_camera
supported=0 detected=0

pi@raspberrypi:~ $ lsusb
Bus 003 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 001 Device 003: ID 1908:2311 GEMBIRD 
Bus 001 Device 002: ID 2109:3431 VIA Labs, Inc. Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub

pi@raspberrypi:~ $ sudo apt-get install fswebcam
```
```bash
fswebcam /tmp/a.jpg
```
