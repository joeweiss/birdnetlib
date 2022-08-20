# Raspberry Pi

## Pi4, 64bit with python 3.7

Note: Depending on your Pi installation, you may have a different version of Python. These instructions are for 3.7.x.

```

sudo apt update
sudo apt upgrade

sudo apt install ffmpeg -y

cd birdnetlib

git submodule update --init --progress

# Or for shallow submodule clone:
git submodule update --init --progress --depth=1

python -m pip install -r dev/raspberry-pi4-py37-requirements.txt
python -m pip install .

python -m pytest


```

Auto recording

```

arecord -f S16_LE -c2 -r48000 -t wav --max-file-time 15 --use-strftime /home/pi/recordings/%F-birdnet-%H:%M:%S.wav

```
