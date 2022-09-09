from birdnetlib.watcher import DirectoryWatcher
from birdnetlib.analyzer import Analyzer
from datetime import datetime
from pprint import pprint
import sqlite3


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


def on_analyze_complete(recording):
    print("on_analyze_complete")
    # Each analyzation as it is completed.
    print(recording.path, recording.analyzer.name)
    pprint(recording.detections)


def on_analyze_file_complete(recording_list):
    print("---------------------------")
    print("on_analyze_file_complete")
    print("---------------------------")
    # All analyzations are completed. Results passed as a list of Recording objects.
    for recording in recording_list:
        print(recording.filename, recording.date, recording.analyzer.name)
        pprint(recording.detections)
        handler.log(recording)  # Log the recording to the SQLiteHandler
        print("---------------------------")


def on_error(recording, error):
    print("An exception occurred: {}".format(error))
    print(recording.path)


def preanalyze(recording):
    # Used to modify the recording object before analyzing.
    filename = recording.filename
    # 2022-08-15-birdnet-21:05:51.wav, as an example, use BirdNET-Pi's preferred format for testing.
    dt = datetime.strptime(filename, "%Y-%m-%d-birdnet-%H:%M:%S.wav")
    # Modify the recording object here as needed.
    # For testing, we're changing the date. We could also modify lat/long here.
    recording.date = dt


if __name__ == "__main__":

    # Initialize SQLiteHandler
    db_path = "birds.db"
    handler = SQLiteHandler(db_path)

    print("Starting Analyzers")
    analyzer = Analyzer()


    print("Starting Watcher")
    directory = "."
    watcher = DirectoryWatcher(
        directory,
        analyzers=[analyzer],
        lon=-120.7463,
        lat=35.4244,
        min_conf=0.3,
        use_polling=True,
    )
    watcher.recording_preanalyze = preanalyze
    watcher.on_analyze_complete = on_analyze_complete
    watcher.on_analyze_file_complete = on_analyze_file_complete
    watcher.on_error = on_error
    watcher.watch()
