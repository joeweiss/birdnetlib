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

All recording classes can accept optional `lat`, `lon`, and `date` arguments, which filter detections to species predicted to be present at that location and time. This filtering is equivalent to using the `--lat`, `--lon`, and `--week` arguments in BirdNET-Analyzer’s `analyzer.py` script.


```python
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from datetime import datetime

analyzer = Analyzer()

recording = Recording(
    analyzer,
    "sample.mp3",
    min_conf=0.25,
    lat=35.6,
    lon=-77.3,
    date=datetime(year=2023, month=6, day=27),
)
recording.analyze()
print(recording.detections)
```

It is also possible to annotate each detection — rather than filter — based on whether the species is predicted to occur at the specified location and date. Setting `return_all_detections` enables this behavior.


```python
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from datetime import datetime

analyzer = Analyzer()

recording = Recording(
    analyzer,
    "sample.mp3",
    min_conf=0.25,
    lat=35.6,
    lon=-77.3,
    date=datetime(year=2023, month=6, day=27),
    return_all_detections=True,
)
recording.analyze()
print(recording.detections)

```

When using `return_all_detections=True`, `recording.detections` contains a list of detected species, along with time ranges and confidence value, and an `is_predicted_for_location_and_date` boolean. For example, a Spotted Crake would not be predicted for the eastern United States in June.

```python
[{'common_name': 'Spotted Crake',
  'confidence': 0.7721,
  'end_time': 12.0,
  'scientific_name': 'Porzana porzana',
  'start_time': 9.0,
  'is_predicted_for_location_and_date': False,
  'label': 'Porzana porzana_Spotted Crake'},
 {'common_name': 'House Finch',
  'confidence': 0.4496,
  'end_time': 15.0,
  'scientific_name': 'Haemorhous mexicanus',
  'start_time': 12.0,
  'is_predicted_for_location_and_date': True,
  'label': 'Haemorhous mexicanus_House Finch'}]
```

#### Embeddings

To extract feature embeddings instead of class predictions, use the `extract_embeddings` method.

```python
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

analyzer = Analyzer()
recording = Recording(
    analyzer,
    "sample.mp3",
)
recording.extract_embeddings()
print(recording.embeddings)
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

See [Download and analyze an audio file from a URL](https://github.com/joeweiss/birdnetlib/blob/main/examples/analyze_from_url.py) for a working implementation of `RecordingFileObject`.

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

Note: `birdnetlib` is compatible with BirdNET-Analyzer model versions 2.1 and higher. For more information on specific versions of BirdNET-Analyzer, see their [model version history](https://birdnet-team.github.io/BirdNET-Analyzer/stable/models.html).

#### Using a custom classifier with BirdNET-Analyzer

To use a [model trained with BirdNET-Analyzer](https://birdnet-team.github.io/BirdNET-Analyzer/stable/best-practices/training.html), pass your labels and model path to the `Analyzer` class.

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

Note: The BirdNET-Lite project has been [deprecated](https://github.com/birdnet-team/BirdNET-Lite). The BirdNET-Lite model is no longer included in the PyPi `birdnetlib` package. This model and label file will be downloaded and installed the first time the `LiteAnalyzer` is initialized in your Python environment.

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
