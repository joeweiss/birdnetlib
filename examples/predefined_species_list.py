from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

custom_list_path = "predefined_species_list.txt"  # See example file for formatting.
input_path = "audio.mp3"  # Use your own audio file here.

analyzer = Analyzer(custom_species_list_path=custom_list_path)
recording = Recording(
    analyzer,
    input_path,
    min_conf=0.5,
)
recording.analyze()
print(recording.detections)

"""
Returns:

[{'common_name': 'Spotted Towhee',
  'confidence': 0.7593773603439331,
  'end_time': 51.0,
  'scientific_name': 'Pipilo maculatus',
  'start_time': 48.0}]

"""
