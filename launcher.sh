#!/usr/bin/env bash
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home
#ssh pi@ise-pi-999499.luddy.indiana.edu
#python test.py 
cd /
cd home/pi/Engr-2022-Capstone
set -e
/home/pi/Engr-2022-Capstone/.conda/envs/py36/bin/python3 superscript.py
cd /
