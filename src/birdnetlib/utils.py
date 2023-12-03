import calendar
import math
import librosa


def return_week_48_from_datetime(dt):
    day_of_year = dt.timetuple().tm_yday
    days_in_year = 366 if calendar.isleap(dt.year) else 365
    week_48 = math.ceil((day_of_year / days_in_year) * 48)
    return week_48


def read_audio_segments(
    file_path, chunk_duration=60 * 10, segment_duration=3, sr=48000
):
    """
    Process an audio file, yielding 3-second segments from each 2-minute chunk along with start and end times.
    Includes the last chunk and segment even if they are shorter than the specified durations.

    :param file_path: Path to the audio file.
    :param chunk_duration: Duration of each chunk to read (in seconds).
    :param segment_duration: Duration of each segment to yield (in seconds).
    :param sr: Sampling rate for audio loading.
    :return: Yields dictionaries containing segments of audio and their start/end times.
    """

    chunk_samples = chunk_duration * sr
    segment_samples = segment_duration * sr

    start_sample = 0

    while True:
        audio_chunk, _ = librosa.load(
            file_path,
            sr=sr,
            mono=True,
            offset=start_sample / sr,
            duration=chunk_duration,
        )

        # Check if the chunk is empty, indicating the end of the file
        if not audio_chunk.any():
            break

        for start_idx in range(0, len(audio_chunk), segment_samples):
            end_idx = start_idx + segment_samples

            # Adjust the end index if it exceeds the length of the chunk
            end_idx = min(end_idx, len(audio_chunk))

            segment_start_time = (start_sample + start_idx) / sr
            segment_end_time = (start_sample + end_idx) / sr
            yield {
                "segment": audio_chunk[start_idx:end_idx],
                "start_sec": segment_start_time,
                "end_sec": segment_end_time,
            }

            # Break if this is the last segment in the current chunk
            if end_idx == len(audio_chunk):
                break

        start_sample += chunk_samples

        # Break if the last chunk was shorter than the expected chunk size
        if len(audio_chunk) < chunk_samples:
            break
