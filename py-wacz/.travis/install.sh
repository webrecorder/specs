#!/bin/bash
set -e

pip install --upgrade pip setuptools

pip install --upgrade -r py-wacz/requirements.txt 
git clone https://github.com/webrecorder/wacz-format.git
cd wacz-format/py-wacz
python setup.py -q install
