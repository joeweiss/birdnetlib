---
hide:
  - navigation
---

# Examples

[Extract detections as audio file samples and/or spectrograms](https://github.com/joeweiss/birdnetlib/blob/main/examples/analyze_and_extract.py)

Supports audio extractions as .flac, .wav and .mp3. Spectrograms exported as .png, .jpg, or other matplotlib.pyplot supported formats. Can be filtered to only extract files above a separate minimum confidence value.

[Download and analyzer an audio file from a URL](https://github.com/joeweiss/birdnetlib/blob/main/examples/analyze_from_url.py)

[Analyze an entire directory](https://github.com/joeweiss/birdnetlib/blob/main/examples/batch_directory.py)

[Analyze an entire directory with multithreading support](https://github.com/joeweiss/birdnetlib/blob/main/examples/batch_multiprocessing_directory.py)

[Watch a directory and analyze files as they are added](https://github.com/joeweiss/birdnetlib/blob/main/examples/watch_directory.py)

[On Linux, record live audio and analyze in 3 sec segments](https://github.com/joeweiss/birdnetlib/blob/main/examples/linux_arecord_and_watch.py)

Note: `arecord` only works on Linux.

[Limit detections to certain species by passing a predefined species list to the analyzer](https://github.com/joeweiss/birdnetlib/blob/main/examples/predefined_species_list.py)

Useful when searching for a particular set of bird detections.

[Analyze an audio stream in realtime using RecordingBuffer class](https://github.com/joeweiss/birdnetlib/blob/main/examples/simple_tcp_server.py)

[Watch a directory for new files, then analyze with both analyzer models as files are saved](https://github.com/joeweiss/birdnetlib/blob/main/examples/watch_directory_both_analyzers.py)

[Watch a directory for new files, and apply datetimes by parsing file names (eg _2022-08-15-birdnet-21:05:52.wav_) prior to analyzing](https://github.com/joeweiss/birdnetlib/blob/main/examples/watch_directory_date_filenames.py)

This example can also be used to modify lat/lon, min_conf, etc., based on file name prior to analyzing.

[Watch a directory for new files, and apply datetimes by parsing file names (eg _2022-08-15-birdnet-21:05:52.wav_) prior to analyzing and save results to SQLite](https://github.com/joeweiss/birdnetlib/blob/main/examples/watch_directory_date_filenames_sqlite.py)
