from birdnetlib.analyzer_lite import LiteAnalyzer, MODEL_PATH, LABEL_PATH
import os
import hashlib


def test_downloading_models():

    # Initialize analyzer in repo, will not download.
    analyzer = LiteAnalyzer()
    assert analyzer.model_download_was_required == False

    original_hash = hashlib.md5(open(MODEL_PATH, "rb").read()).hexdigest()

    # Temporarily rename the Lite model and labels file.
    os.rename(MODEL_PATH, f"{MODEL_PATH}_temp")
    os.rename(LABEL_PATH, f"{LABEL_PATH}_temp")

    # Initialize analyzer without MODEL_PATH or LABEL_PATH existing.
    analyzer = LiteAnalyzer()
    assert (
        analyzer.model_download_was_required
    )  # Files will have downloaded from Github.

    downloaded_file_hash = hashlib.md5(open(MODEL_PATH, "rb").read()).hexdigest()

    assert (
        original_hash == downloaded_file_hash
    )  # Ensure files are a match. BirdNET-Lite is deprecated, so this will likely never change.

    os.unlink(MODEL_PATH)
    os.unlink(LABEL_PATH)

    os.rename(f"{MODEL_PATH}_temp", MODEL_PATH)
    os.rename(f"{LABEL_PATH}_temp", LABEL_PATH)
