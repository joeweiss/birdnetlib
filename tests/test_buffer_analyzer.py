from birdnetlib import RecordingBuffer
from birdnetlib.analyzer import Analyzer, MODEL_PATH, LABEL_PATH
import birdnetlib.wavutils as wavutils

from pprint import pprint
import pytest
import os
import tempfile
import csv
from unittest.mock import patch
import io

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
    with open(input_path,'rb') as f:
        wav_buffer = f.read()
    bytes_buffer = io.BytesIO(wav_buffer)
    for rate,buffer in wavutils.bufferwavs(bytes_buffer):
        analyzer = Analyzer()
        recording = RecordingBuffer(
            analyzer,
            buffer,
            rate,
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
            len(analyzer.custom_species_list) == 195
        )  # Check that this matches the number printed by the cli version.

        # Check that detection confidence is float.
        assert type(recording.detections[0]["confidence"]) is float


def test_with_species_list_path():

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
    with open(input_path,'rb') as f:
        wav_buffer = f.read()
    bytes_buffer = io.BytesIO(wav_buffer)
    for rate,buffer in wavutils.bufferwavs(bytes_buffer):
        analyzer = Analyzer(custom_species_list_path=custom_list_path)
        recording = RecordingBuffer(
            analyzer,
            buffer,
            rate,
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

    with open(input_path,'rb') as f:
        wav_buffer = f.read()
    bytes_buffer = io.BytesIO(wav_buffer)
    # Run a recording without path and throw an error when used with custom species list.
    for rate,buffer in wavutils.bufferwavs(bytes_buffer):
        with pytest.raises(ValueError):
            recording = RecordingBuffer(
                analyzer,
                buffer,
                rate,
                lon=lon,
                lat=lat,
                week_48=week_48,
                min_conf=min_conf,
            )
            recording.analyze()


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

    custom_species_list = [
        "Accipiter cooperii_Cooper's Hawk",
        "Anas platyrhynchos_Mallard",
        "Baeolophus bicolor_Tufted Titmouse",
        "Branta canadensis_Canada Goose",
        "Bucephala albeola_Bufflehead",
        "Bucephala clangula_Common Goldeneye",
        "Buteo jamaicensis_Red-tailed Hawk",
        "Cardinalis cardinalis_Northern Cardinal",
        "Certhia americana_Brown Creeper",
        "Columba livia_Rock Pigeon",
        "Corvus brachyrhynchos_American Crow",
        "Corvus corax_Common Raven",
        "Cyanocitta cristata_Blue Jay",
        "Dryobates pubescens_Downy Woodpecker",
        "Dryobates villosus_Hairy Woodpecker",
        "Dryocopus pileatus_Pileated Woodpecker",
        "Haemorhous mexicanus_House Finch",
        "Haemorhous purpureus_Purple Finch",
        "Haliaeetus leucocephalus_Bald Eagle",
        "Junco hyemalis_Dark-eyed Junco",
        "Larus argentatus_Herring Gull",
        "Larus delawarensis_Ring-billed Gull",
        "Larus marinus_Great Black-backed Gull",
        "Lophodytes cucullatus_Hooded Merganser",
        "Melanerpes carolinus_Red-bellied Woodpecker",
        "Meleagris gallopavo_Wild Turkey",
        "Melospiza melodia_Song Sparrow",
        "Mergus merganser_Common Merganser",
        "Passer domesticus_House Sparrow",
        "Poecile atricapillus_Black-capped Chickadee",
        "Sialia sialis_Eastern Bluebird",
        "Sitta canadensis_Red-breasted Nuthatch",
        "Sitta carolinensis_White-breasted Nuthatch",
        "Spinus pinus_Pine Siskin",
        "Spinus tristis_American Goldfinch",
        "Spizelloides arborea_American Tree Sparrow",
        "Sturnus vulgaris_European Starling",
        "Thryothorus ludovicianus_Carolina Wren",
        "Turdus migratorius_American Robin",
        "Zenaida macroura_Mourning Dove",
        "Zonotrichia albicollis_White-throated Sparrow",
    ]

    with open(input_path,'rb') as f:
        wav_buffer = f.read()
    bytes_buffer = io.BytesIO(wav_buffer)
    # Run a recording without path and throw an error when used with custom species list.
    for rate,buffer in wavutils.bufferwavs(bytes_buffer):
        analyzer = Analyzer(custom_species_list=custom_species_list)
        recording = RecordingBuffer(
            analyzer,
            buffer,
            rate,
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
    with open(input_path,'rb') as f:
        wav_buffer = f.read()
    bytes_buffer = io.BytesIO(wav_buffer)
    # Run a recording without path and throw an error when used with custom species list.
    for rate,buffer in wavutils.bufferwavs(bytes_buffer):
        with pytest.raises(ValueError):
            recording = RecordingBuffer(
                analyzer,
                buffer,
                rate,
                lon=lon,
                lat=lat,
                week_48=week_48,
                min_conf=min_conf,
            )
            recording.analyze()


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
        with open(input_path,'rb') as f:
            wav_buffer = f.read()
        bytes_buffer = io.BytesIO(wav_buffer)
        # Run a recording without path and throw an error when used with custom species list.
        for rate,buffer in wavutils.bufferwavs(bytes_buffer):
            recording = RecordingBuffer(
                analyzer,
                buffer,
                rate,
                lon=lon,
                lat=lat,
                week_48=week_48,
                min_conf=min_conf,
            )
            recording.analyze()
            assert wrapped_return_predicted_species_list.call_count == 1

        # Second recording with the same position/time should not regerate the species list.
        with open(input_path,'rb') as f:
            wav_buffer = f.read()
        bytes_buffer = io.BytesIO(wav_buffer)
        for rate,buffer in wavutils.bufferwavs(bytes_buffer):
            recording = RecordingBuffer(
                analyzer,
                buffer,
                rate,
                lon=lon,
                lat=lat,
                week_48=week_48,
                min_conf=min_conf,
            )
            recording.analyze()
            assert wrapped_return_predicted_species_list.call_count == 1
