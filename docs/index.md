---
hide:
  - navigation
---

# birdnetlib

[![PyPI](https://img.shields.io/pypi/v/birdnetlib.svg)](https://pypi.org/project/birdnetlib/)
[![Python 3.x](https://img.shields.io/pypi/pyversions/birdnetlib.svg?logo=python&logoColor=white)](https://pypi.org/project/birdnetlib/)
[![Test](https://github.com/joeweiss/birdnetlib/actions/workflows/test.yml/badge.svg)](https://github.com/joeweiss/birdnetlib/actions/workflows/test.yml)

A python api for BirdNET-Analyzer and BirdNET-Lite

## Installation

`birdnetlib` requires Python 3.9+ and prior installation of Tensorflow Lite, librosa and ffmpeg. See [BirdNET-Analyzer](https://github.com/kahst/BirdNET-Analyzer#setup-ubuntu) for more details on installing the Tensorflow-related dependencies.

```bash
pip install birdnetlib
```

## Documentation

`birdnetlib` provides a common interface for BirdNET-Analyzer and BirdNET-Lite.

### Using BirdNET-Analyzer

To use the latest BirdNET-Analyzer model, use the `Analyzer` class.

```python
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from datetime import datetime

# Load and initialize the BirdNET-Analyzer models.
analyzer = Analyzer()

recording = Recording(
    analyzer,
    "sample.mp3",
    lat=35.4244,
    lon=-120.7463,
    date=datetime(year=2022, month=5, day=10), # use date or week_48
    min_conf=0.25,
)
recording.analyze()
print(recording.detections)
```

`recording.detections` contains a list of detected species, along with time ranges and confidence value.

```bash
[{'common_name': 'House Finch',
  'confidence': 0.5744,
  'end_time': 12.0,
  'scientific_name': 'Haemorhous mexicanus',
  'start_time': 9.0,
  'label': 'Haemorhous mexicanus_House Finch'},
 {'common_name': 'House Finch',
  'confidence': 0.4496,
  'end_time': 15.0,
  'scientific_name': 'Haemorhous mexicanus',
  'start_time': 12.0,
  'label': 'Haemorhous mexicanus_House Finch'}]
```

The `Recording` class takes a file path as an argument. You can also use `RecordingFileObject` to analyze an in-memory object, or `RecordingBuffer` for handling an array buffer.

## About BirdNET-Analyzer

`birdnetlib` uses models provided by BirdNET-Analyzer and BirdNET-Lite under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International Public License](https://github.com/kahst/BirdNET-Analyzer/blob/main/LICENSE).

BirdNET-Analyzer and BirdNET-Lite were developed by the [K. Lisa Yang Center for Conservation Bioacoustics](https://www.birds.cornell.edu/ccb/) at the [Cornell Lab of Ornithology](https://www.birds.cornell.edu/home).

For more information on BirdNET analyzers, please see the project repositories below:

[BirdNET-Analyzer](https://github.com/kahst/BirdNET-Analyzer)

[BirdNET-Lite](https://github.com/kahst/BirdNET-Lite)

`birdnetlib` is not associated with BirdNET-Lite, BirdNET-Analyzer or the K. Lisa Yang Center for Conservation Bioacoustics.

## About `birdnetlib`

`birdnetlib` is maintained by Joe Weiss. Contributions are welcome.

### Project Goals

- Establish a unified API for interacting with Tensorflow-based BirdNET analyzers
- Enable python-based test cases for BirdNET analyzers
- Make it easier to use BirdNET in python-based projects
- Make it easier to migrate to new BirdNET versions/models as they become available
