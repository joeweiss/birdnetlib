from birdnetlib import RecordingBuffer
from birdnetlib.analyzer import Analyzer
import birdnetlib.wavutils as wavutils
from datetime import datetime
from pprint import pprint
import socketserver

"""
Simple example of running birdnetlib in a TCP Server. To test the example:

Start the server in one terminal:

python simple_tcp_server.py

In a second terminal, send a Wav file to the server using netcat:

cat 2022-08-15-21-05-51.wav | nc -q 0 127.0.0.1 9988

If you have a sound card and microphone you can send a continuos stream of 10 second wavs using arecord:

arecord -r 48000 -f FLOAT_LE --max-file-time 10 | nc 127.0.0.1 9988

If you want to stream from somewhere other than the localhost,
change the TCPServer address from 127.0.0.1 to 0.0.0.0 
"""


class MyTCPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        analyzer = Analyzer()
        # Read WAV data from the socket
        for rate, data in wavutils.bufferwavs(self.rfile):
            # Make a RecordingBuffer with buffer and rate
            recording = RecordingBuffer(
                analyzer,
                data,
                rate,
                lat=35.4244,
                lon=-120.7463,
                date=datetime(year=2022, month=5, day=10),  # use date or week_48
                min_conf=0.25,
            )
            recording.analyze()
            pprint(recording.detections)


if __name__ == "__main__":
    try:
        with socketserver.TCPServer(("127.0.0.1", 9988), MyTCPHandler) as server:
            print("Birdnetlib forever!")
            server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
