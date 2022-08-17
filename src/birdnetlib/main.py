import librosa
import numpy as np
from birdnetlib.exceptions import AudioFormatError, AnalyzerRuntimeWarning
import warnings
import audioread
from os import path
from birdnetlib.utils import return_week_48_from_datetime

class Recording:
    def __init__(
        self,
        analyzer,
        path,
        week_48=-1,
        date=None,
        sensitivity=1.0,
        lat=None,
        lon=None,
        min_conf=0.1,
    ):
        self.path = path
        self.analyzer = analyzer
        self.detections_dict = {}  # Old format
        self.detection_list = []
        self.analyzed = False
        self.week_48 = week_48
        self.date = date
        self.sensitivity = max(0.5, min(1.0 - (sensitivity - 1.0), 1.5))
        self.lat = lat
        self.lon = lon
        self.overlap = 0.0
        self.minimum_confidence = max(0.01, min(min_conf, 0.99))
        self.sample_secs = 3.0

    def analyze(self):
        # Compute date to week_48 format as required by current BirdNET analyzers.
        # TODO: Add a warning if both a date and week_48 value is provided. Currently, date would override explicit week_48.
        if self.week_48 != -1:
            self.week_48 = max(1, min(self.week_48, 48))

        if self.date:
            # Convert date to week_48 format for the Analyzer models.
            self.week_48 = return_week_48_from_datetime(self.date)

        # Read and analyze.
        self.read_audio_data()
        self.analyzer.analyze_recording(self)
        self.analyzed = True

    @property
    def filename(self):
        return path.basename(self.path)

    @property
    def detections(self):
        if not self.analyzed:
            warnings.warn(
                "'analyze' method has not been called. Call .analyze() before accessing detections.",
                AnalyzerRuntimeWarning,
            )
        qualified_detections = []
        allow_list = self.analyzer.custom_species_list
        for d in self.detection_list:
            if d.confidence > self.minimum_confidence and (
                f"{d.scientific_name}_{d.common_name}" in allow_list
                or len(allow_list) == 0
            ):
                qualified_detections.append(d.as_dict)
        return qualified_detections

    def read_audio_data(self, sample_rate=48000):

        # Might be shared between systems, or might not.

        print("READING AUDIO DATA...", end=" ", flush=True)

        # Open file with librosa (uses ffmpeg or libav)
        try:
            sig, rate = librosa.load(
                self.path, sr=sample_rate, mono=True, res_type="kaiser_fast"
            )
        except audioread.exceptions.NoBackendError as e:
            print(e)
            raise AudioFormatError("Audio format could not be opened.")

        # Split audio into 3-second chunks

        # Split signal with overlap
        seconds = self.sample_secs
        minlen = 1.5

        chunks = []
        for i in range(0, len(sig), int((seconds - self.overlap) * rate)):
            split = sig[i : i + int(seconds * rate)]

            # End of signal?
            if len(split) < int(minlen * rate):
                break

            # Signal chunk too short? Fill with zeros.
            if len(split) < int(rate * seconds):
                temp = np.zeros((int(rate * seconds)))
                temp[: len(split)] = split
                split = temp

            chunks.append(split)

        self.chunks = chunks

        print("DONE! READ", str(len(self.chunks)), "CHUNKS.")


class Detection:
    def __init__(self, start_time, end_time, data):
        self.data = data or []
        self.start_time = start_time
        self.end_time = end_time

    @property
    def result(self):
        return self.data[0][0]

    @property
    def confidence(self):
        return self.data[0][1]

    @property
    def scientific_name(self):
        return self.result.split("_")[0]

    @property
    def common_name(self):
        return self.result.split("_")[1]

    @property
    def as_dict(self):
        return {
            "common_name": self.common_name,
            "scientific_name": self.scientific_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "confidence": self.confidence,
        }


if __name__ == "__main__":
    pass