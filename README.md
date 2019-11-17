# thvisa
object-oriented easyness to access dsox1102g and spd3303c in linux/wdos

# install
python3 -m pip install wheel pandas pyvisa pyvisa-py pyusb usbtmc


# linux specific #

## git setup
*  sudo apt instal git git-gui
*  git config --global user.name $gusername
*  git config --global user.email $gemail
*  run gitgui via: "git gui"

## linux: setup udev-rules
An example of how to change _/etc/udev/rules.d/usb.rules_ to accomodate not being sudo for accessing pyvisa/usbtmc devices is in usb.rules.
However, the group "thomas" has to be changed to reflect a group your active user is in (execute "groups" command)

* udev troubleshoot with LL and alternative entries https://pypi.org/project/udmx-pyusb/
* comprehensive udev manual : http://www.reactivated.net/writing_udev_rules.html
* examples: https://pypi.org/project/udmx-pyusb/ 