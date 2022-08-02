# To build and upload to PyPI.

```
rm -rf dist/
python -m build
python -m twine upload --repository testpypi dist/*
```

# To install the example package.

```
python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps birdnetlib
```

# To install as editable

```
# Upgrade pip if you haven't already.
# pip install pip --upgrade

pip install . -e


```
