---
hide:
  - navigation
---

# Classes

## Recording Classes

### Recording

Use the `Recording` class to open and analyze a file from disk.

```python
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

analyzer = Analyzer()

recording = Recording(
    analyzer,
    "sample.mp3",
    min_conf=0.25,
)
recording.analyze()
print(recording.detections)
```

### RecordingFileObject

Use the `RecordingFileObject` class to analyze an in-memory file object.

```python
with io.BytesIO(r.content) as fileObj:
    recording = RecordingFileObject(
        analyzer,
        fileObj,
        lat=35.6,
        lon=-77.3,
        date=datetime(year=2023, month=6, day=27),  # use date or week_48
        min_conf=0.25,
    )
    recording.analyze()
    pprint(recording.detections)
```

See [Download and analyzer an audio file from a URL](https://github.com/joeweiss/birdnetlib/blob/main/examples/analyze_from_url.py) for a working implementation of `RecordingFileObject`.

### RecordingBuffer

Use the `RecordingBuffer` class to analyze an in-memory array buffer.

See the example [Analyze an audio stream in realtime using RecordingBuffer class](https://github.com/joeweiss/birdnetlib/blob/main/examples/simple_tcp_server.py) for more information.

## Analyzer classes

### Analyzer

#### Using specific versions of BirdNET-Analyzer

To use a specific version of BirdNET-Analyzer model, pass the version to the `Analyzer` class.

```python
# Load and initialize the BirdNET-Analyzer 2.3 model.
analyzer = Analyzer(version="2.3")
```

Note: `birdnetlib` is compatible with BirdNET-Analyzer model versions 2.1 and higher. For more information on specific versions of BirdNET-Analyzer, see their [model version history](https://github.com/kahst/BirdNET-Analyzer/tree/main/checkpoints).

#### Using a custom classifier with BirdNET-Analyzer

To use a [model trained with BirdNET-Analyzer](https://github.com/kahst/BirdNET-Analyzer#training), pass your labels and model path to the `Analyzer` class.

```python
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

# Load and initialize BirdNET-Analyzer with your own model/labels.

custom_model_path = "custom_classifiers/trogoniformes.tflite"
custom_labels_path = "custom_classifiers/trogoniformes.txt"

analyzer = Analyzer(
    classifier_labels_path=custom_labels_path, classifier_model_path=custom_model_path
)

recording = Recording(
    analyzer,
    "sample.mp3",
    min_conf=0.25,
)
recording.analyze()
print(recording.detections)
```

### LiteAnalyzer - using BirdNET-Lite

To use the legacy BirdNET-Lite model, use the `LiteAnalyzer` class.

Note: The BirdNET-Lite project has been [deprecated](https://github.com/kahst/BirdNET-Lite). The BirdNET-Lite model is no longer included in the PyPi `birdnetlib` package. This model and label file will be downloaded and installed the first time the `LiteAnalyzer` is initialized in your Python environment.

```python
from birdnetlib import Recording
from birdnetlib.analyzer_lite import LiteAnalyzer
from datetime import datetime

# Load and initialize the BirdNET-Lite models.
# If this is the first time using LiteAnalyzer, the model will be downloaded into your Python environment.
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
