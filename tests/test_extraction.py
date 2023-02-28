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
            "soundscape_9s-12s.flac",
            "soundscape_33s-36s.flac",
            "soundscape_69s-72s.flac",
            "soundscape_51s-54s.flac",
            "soundscape_42s-45s.flac",
            "soundscape_60s-63s.flac",
            "soundscape_84s-87s.flac",
            "soundscape_93s-96s.flac",
            "soundscape_66s-69s.flac",
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
            "soundscape_9s-12s.wav",
            "soundscape_51s-54s.wav",
            "soundscape_42s-45s.wav",
            "soundscape_93s-96s.wav",
            "soundscape_84s-87s.wav",
            "soundscape_60s-63s.wav",
            "soundscape_66s-69s.wav",
            "soundscape_33s-36s.wav",
            "soundscape_69s-72s.wav",
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
            "soundscape_7s-14s.mp3",
            "soundscape_82s-89s.mp3",
            "soundscape_40s-47s.mp3",
            "soundscape_64s-71s.mp3",
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
            "soundscape_40s-47s.jpg",
            "soundscape_64s-71s.jpg",
            "soundscape_7s-14s.jpg",
            "soundscape_82s-89s.jpg",
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
            "soundscape_42s-45s.png",
            "soundscape_66s-69s.png",
            "soundscape_84s-87s.png",
            "soundscape_9s-12s.png",
        ]
        expected_files.sort()

        assert files == expected_files

    # Extract audio and spectrogram.

    with tempfile.TemporaryDirectory() as export_dir:

        recording.extract_detections_as_audio(
            directory=export_dir,
            format="mp3",
            bitrate="128k",
            min_conf=0.4,
            padding_secs=2,
        )

        recording.extract_detections_as_spectrogram(
            directory=export_dir,
            format="png",
            min_conf=0.4,
            padding_secs=2,
        )

        # Check file list.
        files = os.listdir(export_dir)
        files.sort()

        expected_files = [
            "soundscape_40s-47s.mp3",
            "soundscape_40s-47s.png",
            "soundscape_64s-71s.mp3",
            "soundscape_64s-71s.png",
            "soundscape_7s-14s.mp3",
            "soundscape_7s-14s.png",
            "soundscape_82s-89s.mp3",
            "soundscape_82s-89s.png",
        ]
        expected_files.sort()

        assert files == expected_files
