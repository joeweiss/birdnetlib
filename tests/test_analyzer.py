from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer, MODEL_PATH, LABEL_PATH

from pprint import pprint
import pytest
import os
import tempfile
import csv
from unittest.mock import patch


def test_without_species_list():

    # Process file with command line utility, then process with python library and ensure equal commandline_results.

    lon = -120.7463
    lat = 35.4244
    week_48 = 18
    min_conf = 0.25
    input_path = os.path.join(os.path.dirname(__file__), "test_files/soundscape.wav")

    tf = tempfile.NamedTemporaryFile(suffix=".csv")
    output_path = tf.name

    # Process using python script as is.
    birdnet_analyzer_path = os.path.join(os.path.dirname(__file__), "BirdNET-Analyzer")

    cmd = f"python analyze.py --i '{input_path}' --o={output_path} --lat {lat} --lon {lon} --week {week_48} --min_conf {min_conf} --rtype=csv"
    print(cmd)
    os.system(f"cd {birdnet_analyzer_path}; {cmd}")

    with open(tf.name) as f:
        for line in f:
            print(line)

    with open(tf.name, newline="") as csvfile:
        # reader = csv.reader(csvfile, delimiter=";", quotechar="|")
        reader = csv.DictReader(csvfile)
        commandline_results = []
        for row in reader:
            commandline_results.append(
                {
                    "start_time": float(row["Start (s)"]),
                    "end_time": float(row["End (s)"]),
                    "common_name": row["Common name"],
                    "scientific_name": row["Scientific name"],
                    "confidence": float(row["Confidence"]),
                }
            )

    # pprint(commandline_results)
    assert len(commandline_results) > 0

    analyzer = Analyzer()
    recording = Recording(
        analyzer,
        input_path,
        lat=lat,
        lon=lon,
        week_48=week_48,
        min_conf=min_conf,
    )
    recording.analyze()
    pprint(recording.detections)

    # Check that birdnetlib results match command line results.
    assert len(recording.detections) == len(commandline_results)
    assert (
        len(analyzer.custom_species_list) == 130
    )  # Check that this matches the number printed by the cli version.

    # Check that detection confidence is float.
    assert type(recording.detections[0]["confidence"]) is float


def test_with_species_list():

    # Process file with command line utility, then process with python library and ensure equal commandline_results.

    lon = -120.7463
    lat = 35.4244
    week_48 = 18
    min_conf = 0.25
    input_path = os.path.join(os.path.dirname(__file__), "test_files/soundscape.wav")
    custom_list_path = os.path.join(
        os.path.dirname(__file__), "test_files/species_list.txt"
    )

    tf = tempfile.NamedTemporaryFile(suffix=".csv")
    output_path = tf.name

    # Process using python script as is.
    birdnet_analyzer_path = os.path.join(os.path.dirname(__file__), "BirdNET-Analyzer")

    cmd = f"python analyze.py --i '{input_path}' --o={output_path} --min_conf {min_conf} --slist {custom_list_path} --rtype=csv"
    os.system(f"cd {birdnet_analyzer_path}; {cmd}")

    with open(tf.name) as f:
        for line in f:
            print(line)

    with open(tf.name, newline="") as csvfile:
        # reader = csv.reader(csvfile, delimiter=";", quotechar="|")
        reader = csv.DictReader(csvfile)
        commandline_results = []
        for row in reader:
            commandline_results.append(
                {
                    "start_time": float(row["Start (s)"]),
                    "end_time": float(row["End (s)"]),
                    "common_name": row["Common name"],
                    "scientific_name": row["Scientific name"],
                    "confidence": float(row["Confidence"]),
                }
            )

    pprint(commandline_results)
    assert len(commandline_results) > 0

    analyzer = Analyzer(custom_species_list_path=custom_list_path)
    recording = Recording(
        analyzer,
        input_path,
        week_48=week_48,
        min_conf=min_conf,
    )
    recording.analyze()

    assert recording.duration == 120

    pprint(recording.detections)

    assert (
        commandline_results[0]["common_name"] == recording.detections[0]["common_name"]
    )

    commandline_birds = [i["common_name"] for i in commandline_results]
    detected_birds = [i["common_name"] for i in recording.detections]
    assert commandline_birds == detected_birds

    assert len(recording.detections) == len(commandline_results)
    assert (
        len(analyzer.custom_species_list) == 41
    )  # Check that this matches the number printed by the cli version.

    # Run a recording with lat/lon and throw an error when used with custom species list.
    with pytest.raises(ValueError):
        recording = Recording(
            analyzer,
            input_path,
            lon=lon,
            lat=lat,
            week_48=week_48,
            min_conf=min_conf,
        )
        recording.analyze()


def test_with_custom_classifier():

    # Process file with command line utility, then process with python library and ensure equal commandline_results.

    input_path = os.path.join(os.path.dirname(__file__), "test_files/soundscape.wav")
    min_conf = 0.25
    lon = -120.7463
    lat = 35.4244
    week_48 = 18

    # Note, we're using the BirdNET_GLOBAL_3K_V2.3 as the "custom" classifier.

    custom_model_path = MODEL_PATH
    custom_label_path = LABEL_PATH

    analyzer = Analyzer(
        classifier_label_path=custom_label_path, classifier_model_path=custom_model_path
    )

    recording = Recording(
        analyzer,
        input_path,
        lon=lon,
        lat=lat,
        week_48=week_48,
        min_conf=min_conf,
    )
    recording.analyze()

    # Ensure that there is no BirdNET generated species list (from lon/lat or week)
    # Custom classifiers do not use BirdNET generated species list as labels will likely not match.
    assert analyzer.custom_species_list == []

    assert len(recording.detections) == 12

    detected_birds = [i["common_name"] for i in recording.detections]
    assert detected_birds == [
        "Black-capped Chickadee",
        "Black-capped Chickadee",
        "House Finch",
        "Blue Jay",
        "Blue Jay",
        "Dark-eyed Junco",
        "Dark-eyed Junco",
        "Dark-eyed Junco",
        "Dark-eyed Junco",
        "Black-capped Chickadee",
        "House Finch",
        "House Finch",
    ]


def test_species_list_calls():

    lon = -120.7463
    lat = 35.4244
    week_48 = 18
    min_conf = 0.25
    analyzer = Analyzer()

    input_path = os.path.join(os.path.dirname(__file__), "test_files/soundscape.wav")

    # Run another recording, and check that the species generation isn't run again.
    with patch.object(
        analyzer,
        "return_predicted_species_list",
        wraps=analyzer.return_predicted_species_list,
    ) as wrapped_return_predicted_species_list:
        recording = Recording(
            analyzer,
            input_path,
            lon=lon,
            lat=lat,
            week_48=week_48,
            min_conf=min_conf,
        )
        recording.analyze()
        assert wrapped_return_predicted_species_list.call_count == 1

        # Second recording with the same position/time should not regerate the species list.
        recording = Recording(
            analyzer,
            input_path,
            lon=lon,
            lat=lat,
            week_48=week_48,
            min_conf=min_conf,
        )
        recording.analyze()
        assert wrapped_return_predicted_species_list.call_count == 1
