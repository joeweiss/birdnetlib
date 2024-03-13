from birdnetlib.analyzer import Analyzer
from birdnetlib import Recording
from pprint import pprint
from datetime import datetime
import csv
import os
import pytest
import shutil
import tempfile


# The commit numbers refer to the commit of the model release on BirdNET-Analyzer.
# NOTE: These models need to be mirrored to the birdnet-models-nc-sa repo prior to inclusion here.
VERSION_SHAS_TO_TEST = {
    "2.4.1": "9e23983b18ccfbcc75416e066ad889efe0563456",
    "2.4": "b32cdc54c9f2344b028e6378e9eae66e39110d27",
    "2.3": "3d88880b82acb826e4a94c63b7d4f400a1e1efaa",
    "2.2": "cb3707813f4465922823bcfba31358f6c5d0c370",
    "2.1": "e6a976a98cfd8ed17b1eedd59d97e947998710e2",
}


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    clean_up_temp_installed_versions()
    yield  # Test occurs here.
    clean_up_temp_installed_versions()
    # Restore main branch for BirdNET-Analyzer to origin/main.
    birdnet_analyzer_path = os.path.join(os.path.dirname(__file__), "BirdNET-Analyzer")
    os.system(f"cd {birdnet_analyzer_path}; git clean -fd; git switch main; git status")


def clean_up_temp_installed_versions():
    # Remove any temp versions as needed.
    versions = VERSION_SHAS_TO_TEST.keys()
    for v in versions:
        try:
            shutil.rmtree(f"src/birdnetlib/models/analyzer/{v}")
        except FileNotFoundError:
            pass


def test_downloading_models():
    # Test downloading models by version string or version number.

    # Initialize analyzer current included along with the library, will not download.

    version = "2.4.1"
    analyzer = Analyzer(version=version)
    assert analyzer.model_download_was_required is True
    assert analyzer.version == version
    assert analyzer.version_date == datetime(year=2024, month=1, day=15)

    version = "2.4"
    analyzer = Analyzer(version=version)
    assert analyzer.model_download_was_required is False
    assert analyzer.version == version
    assert analyzer.version_date == datetime(year=2023, month=6, day=1)

    version = "2.3"
    analyzer = Analyzer(version=version)
    assert analyzer.model_download_was_required is True
    assert analyzer.version == version
    assert analyzer.version_date == datetime(year=2023, month=4, day=26)

    version = 2.2  # Test by version float.
    analyzer = Analyzer(version=version)
    assert analyzer.model_download_was_required is True
    assert analyzer.version == "2.2"
    assert analyzer.version_date == datetime(year=2022, month=8, day=16)

    # Test on second run (should not have to re-download)
    version = "2.2"
    analyzer = Analyzer(version=version)
    assert analyzer.model_download_was_required is False
    assert analyzer.version_date == datetime(year=2022, month=8, day=16)

    # Test exception raised when using a unavailable version
    with pytest.raises(Exception) as e_info:
        version = "1.2"
        analyzer = Analyzer(version=version)

    assert "No matching version could be found." == str(e_info.value)


def test_default_model():
    analyzer = Analyzer()
    assert analyzer.version is not None


def test_version_matches_values_from_commandline():
    # Cycle through all available versions and check that BirdNET-Analyzer command line
    # results equal the results returned from the birdnetlib library.

    versions = VERSION_SHAS_TO_TEST.keys()
    # versions = ["2.2"]

    for v in versions:
        check_version_results_against_commandline(v)


def check_version_results_against_commandline(version):
    print("-" * 80)
    print("Testing version: ", version)
    print("-" * 80)

    # Checkout version from repo.

    # Run commandline.
    lon = -120.7463
    lat = 35.4244
    week_48 = 18
    min_conf = 0.25
    input_path = os.path.join(os.path.dirname(__file__), "test_files/soundscape.wav")

    tf = tempfile.NamedTemporaryFile(suffix=".csv")
    output_path = tf.name

    # Process using python script as is.
    birdnet_analyzer_path = os.path.join(os.path.dirname(__file__), "BirdNET-Analyzer")

    # TODO: do something here to roll back to the correct commit in BirdNET-Analyzer.

    cmd = (
        f"python analyze.py --i '{input_path}' --o={output_path} --lat {lat} "
        + f"--lon {lon} --week {week_48} --min_conf {min_conf} --rtype=csv"
    )
    print(cmd)
    # Find the sha for this version.

    commit_sha = VERSION_SHAS_TO_TEST[str(version)]
    os.system(f"cd {birdnet_analyzer_path}; git checkout {commit_sha}; {cmd}")

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

    analyzer = Analyzer(version=version)
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

    lib_detection = recording.detections[0]

    sorted_commandline_results = sorted(
        commandline_results, key=lambda x: x["start_time"]
    )  # Commandline results were not always sorted by BirdNET-Analyzer.
    command_detection = sorted_commandline_results[0]

    assert lib_detection["common_name"] == command_detection["common_name"]
    assert lib_detection["start_time"] == command_detection["start_time"]
    assert round(lib_detection["confidence"], 3) == round(
        command_detection["confidence"], 3
    )

    # Check that detection confidence is float.
    assert isinstance(lib_detection["confidence"], float)

    assert recording.analyzer.version == str(version)
