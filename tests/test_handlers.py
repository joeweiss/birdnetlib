from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from birdnetlib.handlers import SqliteHandler
import tempfile
import os
import sqlite3


def test_sqlite_handler():

    tf = tempfile.NamedTemporaryFile(suffix=".db")
    db_path = tf.name

    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(
        """
CREATE TABLE IF NOT EXISTS detections (
    sci_name VARCHAR(100) NOT NULL,
    com_name VARCHAR(100) NOT NULL,
    confidence FLOAT,
    latitude FLOAT,
    longitude FLOAT,
    cutoff FLOAT,
    week INT,
    sens FLOAT,
    overlap FLOAT,
    file_name VARCHAR(100) NOT NULL,
    created_at DATETIME NULL, 
    updated_at DATETIME NULL);
"""
    )

    db_handler = SqliteHandler(db_path)

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
    # pprint(recording.detections)

    success = db_handler.log(recording)

    assert success

    items = []
    for row in cur.execute("SELECT * FROM detections"):
        items.append(row)

    assert items[0] == (
        "Haemorhous mexicanus",
        "House Finch",
        0.5066996216773987,
        35.4244,
        -120.7463,
        0.25,
        18,
        1.0,
        0.0,
        "soundscape.wav",
        items[0][-2],
        items[0][-1],
    )

    # Pass an empty file to handler.
    tf = tempfile.NamedTemporaryFile(suffix=".db")
    db_path = tf.name
    db_handler = SqliteHandler(db_path)

    success = db_handler.log(recording)

    assert success

    con = sqlite3.connect(db_path)
    cur = con.cursor()
    count = cur.execute("SELECT count() FROM detections").fetchone()[0]
    assert count == len(recording.detections)
