# birdnetlib

[![PyPI](https://img.shields.io/pypi/v/birdnetlib.svg)](https://pypi.org/project/birdnetlib/)
[![Test](https://github.com/joeweiss/birdnetlib/actions/workflows/test.yml/badge.svg)](https://github.com/joeweiss/birdnetlib/actions/workflows/test.yml)

A python api for BirdNET-Lite and BirdNET-Analyzer

## Installation

`birdnetlib` requires Python 3.7+ and prior installation of Tensorflow Lite, librosa and ffmpeg. See [BirdNET-Analyzer](https://github.com/kahst/BirdNET-Analyzer#setup-ubuntu) for more details on installing the Tensorflow-related dependencies.

```
pip install birdnetlib
```

## Documentation

`birdnetlib` provides a common interface for BirdNET-Lite and BirdNET-Analyzer.

### Using BirdNET-Lite

To use the BirdNET-Lite model, use the `LiteAnalyzer` class.

```
from birdnetlib import Recording
from birdnetlib.analyzer_lite import LiteAnalyzer
from datetime import datetime

# Load and initialize the BirdNET-Lite models.
analyzer = LiteAnalyzer()

recording = Recording(
    analyzer,
    "sample.mp3",
    lat=35.4244,
    lon=-120.7463,
    date=datetime(year=2022, month=5, day=10), # use date or week_48
    min_conf=0.25,
)
recording.analyze()
print(recording.detections) # Returns list of detections.
```

`recording.detections` contains a list of detected species, along with time ranges and confidence value.

```
[{'common_name': 'House Finch',
  'confidence': 0.5744,
  'end_time': 12.0,
  'scientific_name': 'Haemorhous mexicanus',
  'start_time': 9.0},
 {'common_name': 'House Finch',
  'confidence': 0.4496,
  'end_time': 15.0,
  'scientific_name': 'Haemorhous mexicanus',
  'start_time': 12.0}]
```

### Using BirdNET-Analyzer

To use the newer BirdNET-Analyzer model, use the `Analyzer` class.

```
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

### Utility classes

#### DirectoryAnalyzer

`DirectoryAnalyzer` can process a directory and analyze contained files.

```
def on_analyze_complete(recording):
    print(recording.path)
    pprint(recording.detections)

directory = DirectoryAnalyzer(
    "/Birds/mp3_dir",
    patterns=["*.mp3", "*.wav"]
)
directory.on_analyze_complete = on_analyze_complete
directory.process()
```

See the [full example](https://github.com/joeweiss/birdnetlib/blob/main/examples/batch_directory.py) for analyzer options and error handling callbacks.

#### DirectoryWatcher

`DirectoryWatcher` can watch a directory and analyze new files as they are created.

```
def on_analyze_complete(recording):
    print(recording.path)
    pprint(recording.detections)

watcher = DirectoryWatcher("/Birds/mp3_dir")
watcher.on_analyze_complete = on_analyze_complete
watcher.watch()
```

See the [full example](https://github.com/joeweiss/birdnetlib/blob/main/examples/watch_directory.py) for analyzer options and error handling callbacks.

#### SpeciesList

`SpeciesList` uses BirdNET-Analyzer to predict species lists from location and date.

```
species = SpeciesList()
species_list = species.return_list(
    lon=-120.7463, lat=35.4244, date=datetime(year=2022, month=5, day=10)
)
print(species_list)
# [{'scientific_name': 'Haemorhous mexicanus', 'common_name': 'House Finch', 'threshold': 0.8916686}, ...]
```

### Additional examples

- [Watch a directory for new files, then analyze with multiple analyzer models as files are saved](https://github.com/joeweiss/birdnetlib/blob/main/examples/watch_directory_multi_analyzer.py)
- [Watch a directory for new files, and apply datetimes by parsing file names (eg _2022-08-15-birdnet-21:05:52.wav_) prior to analyzing](https://github.com/joeweiss/birdnetlib/blob/main/examples/watch_directory_date_filenames.py) This example can also be used to modify lat/lon, min_conf, etc., based on file name prior to analyzing.
- [Limit detections to certain species by passing a predefined species list to the analyzer](https://github.com/joeweiss/birdnetlib/blob/main/examples/predefined_species_list.py) Useful when searching for a particular set of bird detections.

## About BirdNET-Lite and BirdNET-Analyzer

`birdnetlib` uses models provided by BirdNET-Lite and BirdNET-Analyzer under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International Public License](https://github.com/kahst/BirdNET-Analyzer/blob/main/LICENSE).

BirdNET-Lite and BirdNET-Analyzer were developed by the [K. Lisa Yang Center for Conservation Bioacoustics](https://www.birds.cornell.edu/ccb/) at the [Cornell Lab of Ornithology](https://www.birds.cornell.edu/home).

For more information on BirdNET analyzers, please see the project repositories below:

[BirdNET-Analyzer](https://github.com/kahst/BirdNET-Analyzer)

[BirdNET-Lite](https://github.com/kahst/BirdNET-Lite)

`birdnetlib` is not associated with BirdNET-Lite, BirdNET-Analyzer or the K. Lisa Yang Center for Conservation Bioacoustics.

## About `birdnetlib`

`birdnetlib` is maintained by Joe Weiss.

### Project Goals

- Establish a unified API for interacting with Tensorflow-based BirdNET analyzers
- Enable python-based test cases for BirdNET analyzers
- Make it easier to use BirdNET in python-based projects
- Make it easier to migrate to new BirdNET versions/models as they become available
