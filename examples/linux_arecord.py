from subprocess import Popen


def main():
    print("main")
    recording_dir = "/home/pi/birdnetlib/examples/recordings"
    duration_secs = 15

    arecord_command_list = [
        "arecord",
        "-f",
        "S16_LE",
        "-c2",
        "-r48000",
        "-t",
        "wav",
        "--max-file-time",
        f"{duration_secs}",
        "--use-strftime",
        f"{recording_dir}/%F-birdnet-%H:%M:%S.wav",
    ]
    print(arecord_command_list)
    record_process = Popen(arecord_command_list)

    record_process.wait()


if __name__ == "__main__":
    main()
