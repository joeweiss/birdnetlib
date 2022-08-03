# Tests

Tests require installing the git submodules.

```
# After cloning the repo.
cd birdnetlib
git submodule update --init

```

# Ubuntu 22

Note: tensorflow does not build on ec2 micro instance (at least as of Aug 2022)

```

# After clone

cd birdnetlib
git submodule update --init
sudo apt install ffmpeg -y

pip install tensorflow librosa pytest

pip install -e .

pytest


```