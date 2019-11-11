### Raspberry Pi Operating System Set up

Raspberry Pi 4B 4GB Starter Kit met heatsink case
https://www.bol.com/nl/p/raspberry-pi-4b-4gb-starter-kit-met-heatsink-case/9200000121607543/

I replaced the slow 16 SD card by a fast 32GB

Install NOOBS pretty straightforward. The install will use 7GB of the SDCard.
* during installation, Pi will ask you to set the password for default user ```pi```:
* after installation it will download and install OS updates.
* ```ifconfig``` will tell you the IP of your Pi 

Setup Remote Access 
run  ```sudo raspi-config```  
* enable ssh-server: Interfacing-options -> ssh -> enable
* enable VNC-server: Interfacing-options -> vnc -> enable

Download and install the RealVNC viewer onto your PC
Connect to your PI's IP using Real VNC viewer. 
The VNC connection is slow at 4K resolution.
Change the background image on the Pi to a single color so remote access will be a lot faster.

Remove monitor, keyboard and mouse from the Pi computer

Setup Remote File Access
```
pi@localhost: sudo apt-get update && sudo apt-get upgrade -y
pi@localhost: sudo apt-get install samba samba-common-bin -y```

pi@localhost: sudo rm /etc/samba/smb.conf
pi@localhost: sudo vi /etc/samba/smb.conf

[global]
netbios name = pi4
server string = The fs of Pi4
workgroup = WORKGROUP

[HOMEPI]
path = /home/pi
comment = pi home directory
browsable = yes
writable = Yes
create mask = 0777
directory mask = 0777
public = no

pi@localhost: sudo smbpasswd -a pi
New SMB password:
Retype new SMB password:
Added user pi.

pi@localhost: sudo service smbd restart
```


