import librosa
import numpy as np
import pydub
from birdnetlib.exceptions import AudioFormatError, AnalyzerRuntimeWarning
import warnings
import audioread
from os import path
from birdnetlib.utils import return_week_48_from_datetime
from pathlib import Path
import matplotlib.pyplot as plt
from collections import namedtuple

SAMPLE_RATE = 48000


class RecordingBase:
    def __init__(
        self,
        analyzer,
        week_48=-1,
        date=None,
        sensitivity=1.0,
        lat=None,
        lon=None,
        min_conf=0.1,
        overlap=0.0,
    ):
        self.analyzer = analyzer
        self.detections_dict = {}  # Old format
        self.detection_list = []
        self.analyzed = False
        self.week_48 = week_48
        self.date = date
        self.sensitivity = max(0.5, min(1.0 - (sensitivity - 1.0), 1.5))
        self.lat = lat
        self.lon = lon
        self.overlap = overlap
        self.minimum_confidence = max(0.01, min(min_conf, 0.99))
        self.sample_secs = 3.0
        self.duration = None
        self.ndarray = None
        self.extracted_audio_paths = {}
        self.extracted_spectrogram_paths = {}

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
                detection = d.as_dict

                # Add extraction paths if available.
                extraction_key = f"{detection['start_time']}_{detection['end_time']}"
                audio_file_path = self.extracted_audio_paths.get(extraction_key, None)
                if audio_file_path:
                    detection["extracted_audio_path"] = audio_file_path
                spectrogram_file_path = self.extracted_spectrogram_paths.get(
                    extraction_key, None
                )
                if spectrogram_file_path:
                    detection["extracted_spectrogram_path"] = spectrogram_file_path
                qualified_detections.append(detection)

        return qualified_detections

    @property
    def as_dict(self):
        config = {
            "model_name": self.analyzer.model_name,
            "week_48": self.week_48,
            "date": self.date,
            "sensitivity": self.sensitivity,
            "lat": self.lat,
            "lon": self.lon,
            "minimum_confidence": self.minimum_confidence,
            "duration": self.duration,
        }
        return {"path": self.path, "config": config, "detections": self.detections}

    def process_audio_data(self, rate):
        # Split audio into 3-second chunks

        # Split signal with overlap
        seconds = self.sample_secs
        minlen = 1.5

        chunks = []
        for i in range(0, len(self.ndarray), int((seconds - self.overlap) * rate)):
            split = self.ndarray[i : i + int(seconds * rate)]

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

        print("read_audio_data: complete, read ", str(len(self.chunks)), "chunks.")

    def extract_detections_as_audio(
        self,
        directory,
        padding_secs=0,
        format="flac",
        bitrate="192k",
        min_conf=0.0,
    ):
        self.extracted_audio_paths = {}  # Clear paths before extraction.
        for detection in self.detections:
            # Skip if detection is under min_conf parameter.
            # Useful for reducing the number of extracted detections.
            if detection["confidence"] < min_conf:
                continue

            start_sec = int(
                detection["start_time"] - padding_secs
                if detection["start_time"] > padding_secs
                else 0
            )
            end_sec = int(
                detection["end_time"] + padding_secs
                if detection["end_time"] + padding_secs < self.duration
                else self.duration
            )

            extract_array = self.ndarray[
                start_sec * SAMPLE_RATE : end_sec * SAMPLE_RATE
            ]

            channels = 1
            data = np.int16(extract_array * 2**15)  # Normalized to -1, 1
            audio = pydub.AudioSegment(
                data.tobytes(),
                frame_rate=SAMPLE_RATE,
                sample_width=2,
                channels=channels,
            )
            if format == "mp3":
                path = f"{directory}/{self.filestem}_{start_sec}s-{end_sec}s.mp3"
                audio.export(path, format="mp3", bitrate=bitrate)
            elif format == "wav":
                path = f"{directory}/{self.filestem}_{start_sec}s-{end_sec}s.wav"
                audio.export(path, format="wav")
            else:
                # flac is default.
                path = f"{directory}/{self.filestem}_{start_sec}s-{end_sec}s.flac"
                audio.export(path, format="flac")

            # Save path for detections list.
            extraction_key = f"{detection['start_time']}_{detection['end_time']}"
            self.extracted_audio_paths[extraction_key] = path

    def extract_detections_as_spectrogram(
        self, directory, padding_secs=0, min_conf=0.0, top=14000, format="jpg", dpi=144
    ):
        self.extracted_spectrogram_paths = {}  # Clear paths before extraction.
        for detection in self.detections:
            # Skip if detection is under min_conf parameter.
            # Useful for reducing the number of extracted detections.
            if detection["confidence"] < min_conf:
                continue

            start_sec = int(
                detection["start_time"] - padding_secs
                if detection["start_time"] > padding_secs
                else 0
            )
            end_sec = int(
                detection["end_time"] + padding_secs
                if detection["end_time"] + padding_secs < self.duration
                else self.duration
            )

            extract_array = self.ndarray[
                start_sec * SAMPLE_RATE : end_sec * SAMPLE_RATE
            ]

            path = f"{directory}/{self.filestem}_{start_sec}s-{end_sec}s.{format}"
            plt.specgram(extract_array, Fs=SAMPLE_RATE)
            plt.ylim(top=top)
            plt.ylabel("frequency kHz")
            plt.title(f"{self.filename} ({start_sec}s - {end_sec}s)", fontsize=10)
            plt.savefig(path, dpi=dpi)
            plt.close()

            # Save path for detections list.
            extraction_spectrogram_key = (
                f"{detection['start_time']}_{detection['end_time']}"
            )
            self.extracted_spectrogram_paths[extraction_spectrogram_key] = path


class Recording(RecordingBase):
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
        overlap=0.0,
    ):
        self.path = path
        p = Path(self.path)
        self.filestem = p.stem
        super().__init__(
            analyzer, week_48, date, sensitivity, lat, lon, min_conf, overlap
        )

    @property
    def filename(self):
        return path.basename(self.path)

    def read_audio_data(self):
        print("read_audio_data")
        # Open file with librosa (uses ffmpeg or libav)
        try:
            self.ndarray, rate = librosa.load(
                self.path, sr=SAMPLE_RATE, mono=True, res_type="kaiser_fast"
            )
            self.duration = librosa.get_duration(y=self.ndarray, sr=SAMPLE_RATE)
        except audioread.exceptions.NoBackendError as e:
            print(e)
            raise AudioFormatError("Audio format could not be opened.")
        except FileNotFoundError as e:
            print(e)
            raise e
        except BaseException as e:
            print(e)
            raise AudioFormatError("Generic audio read error occurred from librosa.")

        self.process_audio_data(rate)


class RecordingBuffer(RecordingBase):
    def __init__(
        self,
        analyzer,
        buffer,
        rate,
        week_48=-1,
        date=None,
        sensitivity=1.0,
        lat=None,
        lon=None,
        min_conf=0.1,
        overlap=0.0,
    ):
        self.buffer = buffer
        self.rate = rate
        super().__init__(
            analyzer, week_48, date, sensitivity, lat, lon, min_conf, overlap
        )

    @property
    def filename(self):
        return "buffer"

    def read_audio_data(self):
        self.ndarray = self.buffer
        self.duration = len(self.ndarray) / self.rate
        self.process_audio_data(self.rate)


class RecordingFileObject(RecordingBase):
    def __init__(
        self,
        analyzer,
        file_obj,
        week_48=-1,
        date=None,
        sensitivity=1.0,
        lat=None,
        lon=None,
        min_conf=0.1,
        overlap=0.0,
    ):
        self.file_obj = file_obj
        super().__init__(
            analyzer, week_48, date, sensitivity, lat, lon, min_conf, overlap
        )

    @property
    def filename(self):
        return "File Object"

    def read_audio_data(self):
        print("read_audio_data")
        # Open file with librosa
        try:
            self.ndarray, rate = librosa.load(
                self.file_obj, sr=SAMPLE_RATE, mono=True, res_type="kaiser_fast"
            )
            self.duration = librosa.get_duration(y=self.ndarray, sr=SAMPLE_RATE)
        except audioread.exceptions.NoBackendError as e:
            print(e)
            raise AudioFormatError("Audio format could not be opened.")
        except FileNotFoundError as e:
            print(e)
            raise e
        except BaseException as e:
            print(e)
            raise AudioFormatError("Generic audio read error occurred from librosa.")

        self.process_audio_data(rate)


class MultiProcessRecording(RecordingBase):
    def __init__(
        self,
        results,
    ):
        self.path = results.get("path")
        p = Path(self.path)
        self.filestem = p.stem
        self.config = results.get("config", {})

        week_48 = results.get("config", {}).get("week_48", -1)
        date = results.get("config", {}).get("date", None)
        sensitivity = results.get("config", {}).get("sensitivity", 1.0)
        lat = results.get("config", {}).get("lat", None)
        lon = results.get("config", {}).get("lon", None)
        min_conf = results.get("config", {}).get("minimum_confidence", 0.1)
        overlap = results.get("config", {}).get("overlap", 0.1)

        Analyzer = namedtuple("Analyzer", ["model_name", "custom_species_list"])

        analyzer = Analyzer(
            model_name=results.get("config", {}).get("model_name"),
            custom_species_list=[],
        )

        super().__init__(
            analyzer, week_48, date, sensitivity, lat, lon, min_conf, overlap
        )

        # After super init.
        self.analyzed = True
        self.error = results.get("error")
        self.error_message = results.get("error_message")
        self.duration = results.get("duration")

        passed_detections = results.get("detections", [])
        self.detection_list = [
            Detection(
                start_time=i["start_time"],
                end_time=i["end_time"],
                data=[[i["label"], i["confidence"]]],
            )
            for i in passed_detections
        ]

    @property
    def filename(self):
        return path.basename(self.path)

    def read_audio_data(self):
        print("read_audio_data")
        # Open file with librosa (uses ffmpeg or libav)
        try:
            self.ndarray, rate = librosa.load(
                self.path, sr=SAMPLE_RATE, mono=True, res_type="kaiser_fast"
            )
            self.duration = librosa.get_duration(y=self.ndarray, sr=SAMPLE_RATE)
        except audioread.exceptions.NoBackendError as e:
            print(e)
            raise AudioFormatError("Audio format could not be opened.")
        except FileNotFoundError as e:
            print(e)
            raise e
        except BaseException as e:
            print(e)
            raise AudioFormatError("Generic audio read error occurred from librosa.")

        # Process audio data is not needed in multiprocess post-extract.
        # self.process_audio_data(rate)

    def extract_detections_as_audio(
        self, directory, padding_secs=0, format="flac", bitrate="192k", min_conf=0
    ):
        if self.ndarray is None:
            self.read_audio_data()
        return super().extract_detections_as_audio(
            directory, padding_secs, format, bitrate, min_conf
        )

    def extract_detections_as_spectrogram(
        self, directory, padding_secs=0, min_conf=0, top=14000, format="jpg", dpi=144
    ):
        if self.ndarray is None:
            self.read_audio_data()
        return super().extract_detections_as_spectrogram(
            directory, padding_secs, min_conf, top, format, dpi
        )

    def process_audio_data(self, rate):
        raise NotImplementedError(
            "MultiProcessRecording objects can not be re-processed from this interface."
        )

    def analyze(self):
        raise NotImplementedError(
            "MultiProcessRecording objects can not be re-analyzed from this interface."
        )



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
        confidence = self.data[0][1]
        if type(confidence) is np.float32:
            return confidence.item()
        return confidence

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
            "label": self.result,
        }


if __name__ == "__main__":
    pass
