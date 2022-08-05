
# Raspberry Pi


## Pi4, 64bit with python 3.7

Note: Depending on your Pi installation, you may have a different version of Python. These instructions are for 3.7.x. 

```

sudo apt update
sudo apt upgrade

sudo apt install ffmpeg -y

cd birdnetlib

git submodule update --init --progress

python -m pip install -r dev/raspberry-pi4-py37-requirements.txt
python -m pip install .

python -m pytest


```

