import sqlite3
from datetime import datetime


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
