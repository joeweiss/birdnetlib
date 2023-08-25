from birdnetlib import Recording, RecordingFileObject
from birdnetlib.analyzer import Analyzer
import io
from pprint import pprint
import os


def test_without_species_list():
    # Process file with command line utility, then process with python library and ensure equal commandline_results.

    lon = -120.7463
    lat = 35.4244
    week_48 = 18
    min_conf = 0.25
    input_path = os.path.join(os.path.dirname(__file__), "test_files/soundscape.wav")

    analyzer = Analyzer()

    # Analyzer with file path.

    recording_from_path = Recording(
        analyzer,
        input_path,
        lat=lat,
        lon=lon,
        week_48=week_48,
        min_conf=min_conf,
    )
    recording_from_path.analyze()
    pprint(recording_from_path.detections)

    # Analyze with file object.
    with open(input_path, "rb") as file:
        binary_data = file.read()

        with io.BytesIO(binary_data) as fileObj:
            recording_from_file_obj = RecordingFileObject(
                analyzer,
                fileObj,
                lat=lat,
                lon=lon,
                week_48=week_48,
                min_conf=min_conf,
            )
            recording_from_file_obj.analyze()
            pprint(recording_from_file_obj.detections)

    # Check that detections match.
    assert len(recording_from_path.detections) > 0
    assert recording_from_path.detections == recording_from_file_obj.detections
