# thvisa #
object-oriented easyness for pythonic access to

* Keysight oscilloscope DSOX1102G (1000x series in general) 
* Keysight/Agilent Fieldfox N991xA VNA
* Siglent rspd3303c/spd3303c 2.5CH lab PSU
  
via the SCPI standard. Or to be more precise, the specific implementations, utilizing the pyvisa framwork.
## examples ##
see "main" sections of InfiniiVision_thisa.py and spd3303c_thvisa.py

## install ##
* first follow linux/windows specific section
* then:
* python3 -m pip install wheel pyvisa pyvisa-py pyusb python-usbtmc numpy matplotlib


### linux specific ##
update system and install python3 with pip, libatlas to avoid numpy error
* sudo apt update
* sudo apt dist-upgrade
* sudo apt install python3-pip
* sudo apt-get install libatlas-base-dev
* then setup git and udev

#### git setup ####
* users don't need a git client, download the zip and ignore this section from hereon
* suggested git client: git-gui
* sudo apt install git git-gui
* git config --global user.name $gusername
* git config --global user.email $gemail
* run gitgui via: "git gui"
* note: gitgui can't be run via ssh since it would need a gui, use a vnc if desired (or plain cmd git)

#### setup udev-rules ####
An example of how to change _/etc/udev/rules.d/usb.rules_ to accomodate not being sudo for accessing pyvisa/usbtmc devices is in usb.rules.
However, the group "thomas" has to be changed to reflect a group your active user is in (execute "groups" command)

* append or make the file _/etc/udev/rules.d/usb.rules_ according to usb.rules provided
* either _udevadm control --reload-rules_ or _udevcontrol reload_rules_ dependent on kernel version

further info:
* udev rules examples: https://pypi.org/project/udmx-pyusb/ 
* comprehensive udev manual : http://www.reactivated.net/writing_udev_rules.html


### windows specific ###
* for anaconda management of python3, substitute "python3 -m pip install .." with "conda install .."


#### git setup ####
* users don't need a git client, download the zip and ignore this section from hereon
* use any git client you want
