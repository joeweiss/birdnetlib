# Tests

## M1 Mac using Docker

```

docker-compose build
docker-compose up -d
docker-compose exec main pip install -r dev/docker-m1-requirements.txt
docker-compose exec main pytest

```

## Ubuntu 22

Note: tensorflow does not install without intervention on ec2 micro instance (at least as of Aug 2022)

```

# After clone

cd birdnetlib
git submodule update --init
sudo apt install ffmpeg -y

pip install tensorflow librosa pytest

pip install -e .

pytest


```
