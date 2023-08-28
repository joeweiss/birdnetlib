---
hide:
  - navigation
---

### Utility classes

#### DirectoryAnalyzer

`DirectoryAnalyzer` can process a directory and analyze contained files.

```python
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

#### DirectoryMultiProcessingAnalyzer

`DirectoryMultiProcessingAnalyzer` can process a directory and analyze contained files, using multiple processes asynchronously.

```python
def on_analyze_directory_complete(recordings):
    for recording in recordings:
        pprint(recording.detections)

directory = "."
batch = DirectoryMultiProcessingAnalyzer(
    "/Birds/mp3_dir",
    patterns=["*.mp3", "*.wav"]
)

batch.on_analyze_directory_complete = on_analyze_directory_complete
batch.process()

```

See the [full example](https://github.com/joeweiss/birdnetlib/blob/main/examples/batch_multiprocessing_directory.py) for analyzer options and error handling callbacks.

#### DirectoryWatcher

`DirectoryWatcher` can watch a directory and analyze new files as they are created.

```python
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

```python
species = SpeciesList()
species_list = species.return_list(
    lon=-120.7463, lat=35.4244, date=datetime(year=2022, month=5, day=10)
)
print(species_list)
# [{'scientific_name': 'Haemorhous mexicanus', 'common_name': 'House Finch', 'threshold': 0.8916686}, ...]
```
