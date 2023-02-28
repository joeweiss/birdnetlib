from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from birdnetlib.analyzer import Analyzer
from datetime import datetime
from pprint import pprint

# Load and initialize the BirdNET-Analyzer models.
analyzer = Analyzer()

recording = Recording(
    analyzer,
    "2022-08-15-birdnet-21:05:54.wav",
    lat=35.4244,
    lon=-120.7463,
    date=datetime(year=2022, month=5, day=10),  # use date or week_48
    min_conf=0.25,
)
recording.analyze()
export_dir = "extractions"  # Directory should already exist.

# Extract to default audio files (.flac)
recording.extract_detections_as_audio(directory=export_dir)

# Extract to spectrograms
recording.extract_detections_as_spectrogram(directory=export_dir)

pprint(recording.detections)

"""
[{'common_name': 'House Finch',
  'confidence': 0.5066996216773987,
  'end_time': 12.0,
  'extracted_audio_path': 'extractions/2022-08-15-birdnet-21:05:54_9s-12s.flac',
  'extracted_spectrogram_path': 'extractions/2022-08-15-birdnet-21:05:54_9s-12s.jpg',
  'scientific_name': 'Haemorhous mexicanus',
  'start_time': 9.0},
 {'common_name': 'Dark-eyed Junco',
  'confidence': 0.3555494546890259,
  'end_time': 36.0,
  'extracted_audio_path': 'extractions/2022-08-15-birdnet-21:05:54_33s-36s.flac',
  'extracted_spectrogram_path': 'extractions/2022-08-15-birdnet-21:05:54_9s-12s.jpg',
  'scientific_name': 'Junco hyemalis',
  'start_time': 33.0}
 ]
 """


recording = Recording(
    analyzer,
    "2022-08-15-birdnet-21:05:54.wav",
    lat=35.4244,
    lon=-120.7463,
    date=datetime(year=2022, month=5, day=10),  # use date or week_48
    min_conf=0.25,
)
recording.analyze()
export_dir = "extractions"  # Directory should already exist.

# Extract to .mp3 audio files, only if confidence is > 0.5 with 2 seconds of audio padding.
recording.extract_detections_as_audio(
    directory=export_dir, format="mp3", bitrate="192k", min_conf=0.5, padding_secs=2
)


pprint(recording.detections)

"""
[{'common_name': 'House Finch',
  'confidence': 0.5066996216773987,
  'end_time': 12.0,
  'extracted_audio_path': 'extractions/2022-08-15-birdnet-21:05:54_7s-14s.mp3',
  'scientific_name': 'Haemorhous mexicanus',
  'start_time': 9.0}
 ]
 """