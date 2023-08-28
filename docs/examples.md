# Examples

- [Watch a directory for new files, then analyze with both analyzer models as files are saved](https://github.com/joeweiss/birdnetlib/blob/main/examples/watch_directory_both_analyzers.py)
- [Watch a directory for new files, and apply datetimes by parsing file names (eg _2022-08-15-birdnet-21:05:52.wav_) prior to analyzing](https://github.com/joeweiss/birdnetlib/blob/main/examples/watch_directory_date_filenames.py) This example can also be used to modify lat/lon, min_conf, etc., based on file name prior to analyzing.
- [Limit detections to certain species by passing a predefined species list to the analyzer](https://github.com/joeweiss/birdnetlib/blob/main/examples/predefined_species_list.py) Useful when searching for a particular set of bird detections.
- [Extract detections as audio file samples and/or spectrograms](https://github.com/joeweiss/birdnetlib/blob/main/examples/analyze_and_extract.py) Supports audio extractions as .flac, .wav and .mp3. Spectrograms exported as .png, .jpg, or other matplotlib.pyplot supported formats. Can be filtered to only extract files above a separate minimum confidence value.
