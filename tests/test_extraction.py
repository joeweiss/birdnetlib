from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

from pprint import pprint
import os
import tempfile
import pydub
import pytest


def test_extraction():

    lon = -120.7463
    lat = 35.4244
    week_48 = 18
    min_conf = 0.25
    input_path = os.path.join(os.path.dirname(__file__), "test_files/soundscape.wav")

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

    # TODO: Remove this comment after feature is defined.

    # # Local development tests.
    
    # export_dir = os.path.join(os.path.dirname(__file__), "extractions")

    # # Export to mp3 @ 128k for all detections with min_conf of 0.8.
    # recording.extract_detections_as_audio(
    #     directory=export_dir, format="mp3", bitrate="128k", min_conf=0.5
    # )

    # # Extract spectrograms.
    # recording.extract_detections_as_spectrogram(
    #     directory=export_dir, min_conf=0.5, format="jpg"
    # )

    # return

    # Test audio extractions.

    # flac test in temporary test directory.
    with tempfile.TemporaryDirectory() as export_dir:
        recording.extract_detections_as_audio(directory=export_dir)

        # Check file list.
        files = os.listdir(export_dir)

        files.sort()
        expected_files = [
            "soundscape_102s-105s.flac",
            "soundscape_117s-120s.flac",
            "soundscape_33s-36s.flac",
            "soundscape_36s-39s.flac",
            "soundscape_39s-42s.flac",
            "soundscape_42s-45s.flac",
            "soundscape_51s-54s.flac",
            "soundscape_54s-57s.flac",
            "soundscape_60s-63s.flac",
            "soundscape_69s-72s.flac",
            "soundscape_72s-75s.flac",
            "soundscape_78s-81s.flac",
            "soundscape_84s-87s.flac",
            "soundscape_90s-93s.flac",
            "soundscape_93s-96s.flac",
            "soundscape_96s-99s.flac",
            "soundscape_9s-12s.flac",
        ]
        expected_files.sort()
        assert files == expected_files

        # Check that file format is flac, 48000, and correct size.
        with pytest.raises(pydub.exceptions.CouldntDecodeError):
            audio = pydub.AudioSegment.from_mp3(f"{export_dir}/{files[0]}")
        audio = pydub.AudioSegment.from_file(f"{export_dir}/{files[0]}")
        assert audio.frame_rate == 48000
        assert audio.duration_seconds == 3.0

    # wav test in temporary test directory.
    with tempfile.TemporaryDirectory() as export_dir:
        recording.extract_detections_as_audio(directory=export_dir, format="wav")

        # Check file list.
        files = os.listdir(export_dir)

        files.sort()

        expected_files = [
            "soundscape_90s-93s.wav",
            "soundscape_39s-42s.wav",
            "soundscape_9s-12s.wav",
            "soundscape_51s-54s.wav",
            "soundscape_42s-45s.wav",
            "soundscape_93s-96s.wav",
            "soundscape_84s-87s.wav",
            "soundscape_102s-105s.wav",
            "soundscape_72s-75s.wav",
            "soundscape_60s-63s.wav",
            "soundscape_96s-99s.wav",
            "soundscape_33s-36s.wav",
            "soundscape_69s-72s.wav",
            "soundscape_36s-39s.wav",
            "soundscape_54s-57s.wav",
            "soundscape_117s-120s.wav",
            "soundscape_78s-81s.wav",
        ]
        expected_files.sort()
        assert files == expected_files

        # Check that file format is wav, 48000, and correct size.
        audio = pydub.AudioSegment.from_wav(f"{export_dir}/{files[0]}")
        assert audio.frame_rate == 48000
        assert audio.duration_seconds == 3.0

    # mp3 test in temporary test directory (with custom min_conf extraction)
    with tempfile.TemporaryDirectory() as export_dir:

        recording.extract_detections_as_audio(
            directory=export_dir,
            format="mp3",
            bitrate="128k",
            min_conf=0.4,
            padding_secs=2,
        )

        # Check file list.
        files = os.listdir(export_dir)

        files.sort()
        expected_files = [
            "soundscape_94s-101s.mp3",
            "soundscape_88s-95s.mp3",
            "soundscape_70s-77s.mp3",
            "soundscape_52s-59s.mp3",
            "soundscape_58s-65s.mp3",
            "soundscape_40s-47s.mp3",
            "soundscape_7s-14s.mp3",
            "soundscape_100s-107s.mp3",
            "soundscape_31s-38s.mp3",
        ]
        expected_files.sort()

        assert files == expected_files

        # Check that file format is mp3, 48000, and 128k bitrate.
        audio = pydub.AudioSegment.from_mp3(f"{export_dir}/{files[0]}")
        assert audio.frame_rate == 48000
        assert audio.duration_seconds == 7.0

    # Test spectrogram extractions

    # spectrogram test in temporary test directory (with custom min_conf extraction)
    with tempfile.TemporaryDirectory() as export_dir:

        recording.extract_detections_as_spectrogram(
            directory=export_dir,
            format="jpg",
            min_conf=0.4,
            padding_secs=2,
        )

        # Check file list.
        files = os.listdir(export_dir)

        files.sort()
        expected_files = [
            "soundscape_31s-38s.jpg",
            "soundscape_58s-65s.jpg",
            "soundscape_52s-59s.jpg",
            "soundscape_88s-95s.jpg",
            "soundscape_94s-101s.jpg",
            "soundscape_40s-47s.jpg",
            "soundscape_7s-14s.jpg",
            "soundscape_100s-107s.jpg",
            "soundscape_70s-77s.jpg",
        ]
        expected_files.sort()

        assert files == expected_files

    # spectrogram test in temporary test directory (with custom min_conf extraction)
    with tempfile.TemporaryDirectory() as export_dir:

        recording.extract_detections_as_spectrogram(
            directory=export_dir,
            format="png",
            min_conf=0.4,
        )

        # Check file list.
        files = os.listdir(export_dir)

        files.sort()
        expected_files = [
            "soundscape_33s-36s.png",
            "soundscape_54s-57s.png",
            "soundscape_96s-99s.png",
            "soundscape_60s-63s.png",
            "soundscape_9s-12s.png",
            "soundscape_72s-75s.png",
            "soundscape_90s-93s.png",
            "soundscape_42s-45s.png",
            "soundscape_102s-105s.png",
        ]
        expected_files.sort()

        assert files == expected_files

    # Extract audio and spectrogram.

    with tempfile.TemporaryDirectory() as export_dir:

        recording.extract_detections_as_audio(
            directory=export_dir,
            format="mp3",
            bitrate="128k",
            padding_secs=2,
        )

        recording.extract_detections_as_spectrogram(
            directory=export_dir,
            format="png",
            padding_secs=2,
        )

        # Check file list.
        files = os.listdir(export_dir)

        files.sort()

        expected_files = [
            "soundscape_88s-95s.png",
            "soundscape_94s-101s.mp3",
            "soundscape_82s-89s.png",
            "soundscape_88s-95s.mp3",
            "soundscape_31s-38s.png",
            "soundscape_70s-77s.png",
            "soundscape_115s-120s.png",
            "soundscape_52s-59s.png",
            "soundscape_70s-77s.mp3",
            "soundscape_49s-56s.png",
            "soundscape_52s-59s.mp3",
            "soundscape_34s-41s.mp3",
            "soundscape_82s-89s.mp3",
            "soundscape_91s-98s.mp3",
            "soundscape_58s-65s.mp3",
            "soundscape_7s-14s.png",
            "soundscape_49s-56s.mp3",
            "soundscape_100s-107s.png",
            "soundscape_76s-83s.mp3",
            "soundscape_58s-65s.png",
            "soundscape_40s-47s.mp3",
            "soundscape_94s-101s.png",
            "soundscape_7s-14s.mp3",
            "soundscape_37s-44s.png",
            "soundscape_115s-120s.mp3",
            "soundscape_37s-44s.mp3",
            "soundscape_34s-41s.png",
            "soundscape_100s-107s.mp3",
            "soundscape_76s-83s.png",
            "soundscape_67s-74s.png",
            "soundscape_67s-74s.mp3",
            "soundscape_31s-38s.mp3",
            "soundscape_91s-98s.png",
            "soundscape_40s-47s.png",
        ]
        expected_files.sort()

        assert files == expected_files
        assert len(recording.detections) == 17

        detection = recording.detections[0]

        # Assert confidence (round for slight float variablity across platforms)
        assert round(detection["confidence"], 3) == 0.639

        del detection["confidence"]

        expected_detection = {
            "common_name": "House Finch",
            "end_time": 12.0,
            "extracted_audio_path": f"{export_dir}/soundscape_7s-14s.mp3",
            "extracted_spectrogram_path": f"{export_dir}/soundscape_7s-14s.png",
            "scientific_name": "Haemorhous mexicanus",
            "start_time": 9.0,
            "label": "Haemorhous mexicanus_House Finch",
        }

        assert detection == expected_detection
