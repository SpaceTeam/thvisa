# thvisa
object-oriented easyness to access dsox1102g and spd3303c in linux/wdos

# install
* first follow linux/windows specific section

* python3 -m pip install wheel pyvisa pyvisa-py pyusb python-usbtmc numpy matplotlib


# linux specific #
update system and install python3 with pip, libatlas to avoid numpy error
* sudo apt update
* sudo apt dist-upgrade
* sudo apt install python3-pip
* sudo apt-get install libatlas-base-dev
* then setup git and udev

## git setup
* users don't need a git client, download the zip and ignore this section from hereon
* suggested git client: git-gui
* sudo apt install git git-gui
* git config --global user.name $gusername
* git config --global user.email $gemail
* run gitgui via: "git gui"
* note: gitgui can't be run via ssh since it would need a gui, use a vnc if desired (or plain cmd git)

## linux: setup udev-rules
An example of how to change _/etc/udev/rules.d/usb.rules_ to accomodate not being sudo for accessing pyvisa/usbtmc devices is in usb.rules.
However, the group "thomas" has to be changed to reflect a group your active user is in (execute "groups" command)

* udev troubleshoot with LL and alternative entries https://pypi.org/project/udmx-pyusb/
* comprehensive udev manual : http://www.reactivated.net/writing_udev_rules.html
* examples: https://pypi.org/project/udmx-pyusb/ 

# windows specific #
* for anaconda management of python3, substitute "python3 -m pip install .." with "conda install .."
* ignore
..TBD..

## git setup ##
* users don't need a git client, download the zip and ignore this section from hereon
* use any git client you want
