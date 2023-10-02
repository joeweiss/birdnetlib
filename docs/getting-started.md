---
hide:
  - navigation
---

## Installation

`birdnetlib` requires Python 3.9+ and prior installation of Tensorflow Lite, librosa and ffmpeg. See [BirdNET-Analyzer](https://github.com/kahst/BirdNET-Analyzer#setup-ubuntu) for more details on installing the Tensorflow-related dependencies.

```bash
pip install birdnetlib
```

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
