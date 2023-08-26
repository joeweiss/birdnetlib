import requests
import io

from datetime import datetime
from pprint import pprint
from birdnetlib import RecordingFileObject
from birdnetlib.analyzer import Analyzer

# Mississippi Kite from Xeno-Canto.
r = requests.get("https://xeno-canto.org/669899/download")
analyzer = Analyzer()

with io.BytesIO(r.content) as fileObj:
    recording = RecordingFileObject(
        analyzer,
        fileObj,
        lat=35.6,
        lon=-77.3,
        date=datetime(year=2023, month=6, day=27),  # use date or week_48
        min_conf=0.25,
    )
    recording.analyze()
    pprint(recording.detections)
