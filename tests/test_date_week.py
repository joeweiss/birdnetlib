from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
import os
from datetime import datetime


def test_date_conversion_to_week_48():
    """
    BirdNET-Analyzer and BirdNET-Lite use a non-standard 48-weeks-to-a-year 'week' variable.
    For consistency and compatibility with existing usage, birdnetlib provides a 'week_48' variable,
    in addition to a more explicit 'date' variable. Behind the scenes, 'date' converts to 'week_48'
    for both analyzer model constructors.
    """

    # Test if no week or date is provided.
    input_path = os.path.join(os.path.dirname(__file__), "test_files/soundscape.wav")

    analyzer = Analyzer()

    recording = Recording(
        analyzer,
        input_path,
    )
    recording.analyze()

    assert recording.week_48 == -1  # Analyzers expect -1 if non-defined.

    # Test week 48 values are accepted.
    lon = -120.7463
    lat = 35.4244
    week_48 = 18  # This is the 2nd week of the 5th month, ie May 10th.
    # !!!! ???? For more info on the above determination,
    #           see Analyzer models ... they don't use 52 week/year format!
    min_conf = 0.7

    input_path = os.path.join(os.path.dirname(__file__), "test_files/soundscape.wav")

    analyzer = Analyzer()

    recording = Recording(
        analyzer,
        input_path,
        lon=lon,
        lat=lat,
        week_48=week_48,
        min_conf=min_conf,
    )
    recording.analyze()

    assert recording.week_48 == week_48

    # Test date values are accepted and week_48 is automatically applied.
    lon = -120.7463
    lat = 35.4244
    date = datetime(year=2022, month=5, day=10)
    print(date)
    min_conf = 0.7

    input_path = os.path.join(os.path.dirname(__file__), "test_files/soundscape.wav")

    analyzer = Analyzer()

    recording = Recording(
        analyzer,
        input_path,
        lon=lon,
        lat=lat,
        date=date,
        min_conf=min_conf,
    )
    recording.analyze()

    assert recording.week_48 == week_48
