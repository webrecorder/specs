#!/bin/bash
set -e

pip install --upgrade pip setuptools
pip install coverage pytest-cov coveralls
pip install codecov
pip install coverage pytest-cov codecov

git clone https://github.com/webrecorder/wacz-format.git
cd wacz-format/py-wacz
python setup.py -q install
pip install --upgrade -r requirements.txt    
