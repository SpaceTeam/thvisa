# thvisa
object-oriented easyness to access dsox1102g and spd3303c in linux/wdos

# install
* first follow linux/windows specific section

* python3 -m pip install wheel pyvisa pyvisa-py pyusb python-usbtmc numpy matplotlib


# linux specific #
update system and install python3 with pip
* sudo apt update
* sudo apt dist-upgrade
* sudo apt install python3-pip
* then setup git and udev

## git setup
*  sudo apt instal git git-gui
*  git config --global user.name $gusername
*  git config --global user.email $gemail
*  run gitgui via: "git gui"
* gitgui can't be run via ssh since it would need a gui, use a vnc if desired

## linux: setup udev-rules
An example of how to change _/etc/udev/rules.d/usb.rules_ to accomodate not being sudo for accessing pyvisa/usbtmc devices is in usb.rules.
However, the group "thomas" has to be changed to reflect a group your active user is in (execute "groups" command)

* udev troubleshoot with LL and alternative entries https://pypi.org/project/udmx-pyusb/
* comprehensive udev manual : http://www.reactivated.net/writing_udev_rules.html
* examples: https://pypi.org/project/udmx-pyusb/ 

# windows specific #
TBD
