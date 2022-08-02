import birdnetlib
from birdnetlib import add_one as add_da_one


def test_import():
    assert birdnetlib.add_one(1) == 2
    assert add_da_one(1) == 2
