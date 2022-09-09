from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
import tempfile
import os
import sqlite3
from datetime import datetime

# Make a handler for saving recordings to SQLite database.
class SQLiteHandler:
    def __init__(self, db_path):
        self.db_path = db_path
        # Confirm the db_path exists and can be opened.
        self.connection = sqlite3.connect(self.db_path)
        cur = self.connection.cursor()
        result = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='detections';"
        )
        table_exists = len(result.fetchall()) == 1
        if not table_exists:
            # Create table.
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

    def log(self, recording):
        # Log recording to database.
        data = []
        for d in recording.detections:
            sci_name = d["scientific_name"]
            com_name = d["common_name"]
            confidence = d["confidence"]
            latitude = recording.lat
            longitude = recording.lon
            cutoff = recording.minimum_confidence
            week = recording.week_48
            sens = recording.sensitivity
            overlap = recording.overlap
            file_name = recording.filename
            created_at = recording.date or datetime.now()
            updated_at = datetime.now()
            data.append(
                [
                    sci_name,
                    com_name,
                    confidence,
                    latitude,
                    longitude,
                    cutoff,
                    week,
                    sens,
                    overlap,
                    file_name,
                    created_at,
                    updated_at,
                ]
            )
        cur = self.connection.cursor()
        cur.executemany(
            "INSERT INTO detections VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data
        )
        self.connection.commit()  # Remember to commit the transaction after executing INSERT.
        return True


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

    db_handler = SQLiteHandler(db_path)

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
        recording.detections[0]["confidence"],
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
    db_handler = SQLiteHandler(db_path)

    success = db_handler.log(recording)

    assert success

    con = sqlite3.connect(db_path)
    cur = con.cursor()
    count = cur.execute("SELECT count() FROM detections").fetchone()[0]
    assert count == len(recording.detections)

    # Pass a specific recording date
    # New database and handler for testing.
    tf = tempfile.NamedTemporaryFile(suffix=".db")
    db_path = tf.name
    db_handler = SQLiteHandler(db_path)

    recording.date = datetime.now()
    success = db_handler.log(recording)

    assert success

    con = sqlite3.connect(db_path)
    cur = con.cursor()
    items = []
    for row in cur.execute("SELECT * FROM detections"):
        items.append(row)

    assert items[0] == (
        "Haemorhous mexicanus",
        "House Finch",
        recording.detections[0]["confidence"],
        35.4244,
        -120.7463,
        0.25,
        18,
        1.0,
        0.0,
        "soundscape.wav",
        str(recording.date),
        items[0][-1],
    )
