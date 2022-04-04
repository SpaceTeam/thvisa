# install requirements, needs py3, maintained (for usb libs)
sudo apt install python3 python3-pip libatlas-base-dev
python3 -m pip install wheel
python3 -m pip install -r requirements.txt
# install udev rules for instruments
sudo cp usb_msr.rules /etc/udev/rules.d/usb_msr.rules
