import os
import sys


os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

try:
    import tflite_runtime.interpreter as tflite
except:
    from tensorflow import lite as tflite

import numpy as np
import math
import time
import operator

from birdnetlib import Detection


MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "models/lite/BirdNET_6K_GLOBAL_MODEL.tflite"
)
LABEL_PATH = os.path.join(os.path.dirname(__file__), "models/lite/labels.txt")


class LiteAnalyzer:
    def __init__(self, custom_species_list_path=None):
        self.name = "LiteAnalyzer"
        self.model_name = "BirdNET-Lite"
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.input_layer_index = None
        self.mdata_input_index = None
        self.output_layer_index = None
        self.classes = []
        self.custom_species_list = []
        self.custom_species_list_path = custom_species_list_path

        self.load_lite_model()
        if self.custom_species_list_path:
            self.load_custom_list()

    def load_lite_model(self):
        self.interpreter = tflite.Interpreter(model_path=MODEL_PATH)
        self.interpreter.allocate_tensors()

        # Get input and output tensors.
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        self.input_layer_index = self.input_details[0]["index"]
        self.mdata_input_index = self.input_details[1]["index"]
        self.output_layer_index = self.output_details[0]["index"]

        # Load labels
        with open(LABEL_PATH, "r") as lfile:
            for line in lfile.readlines():
                self.classes.append(line.replace("\n", ""))

        print("Lite model loaded")

    def load_custom_list(self, custom_species_list_path=None):
        if custom_species_list_path:
            self.custom_species_list_path = custom_species_list_path
        slist = []
        if os.path.isfile(self.custom_species_list_path):
            with open(self.custom_species_list_path, "r") as csfile:
                for line in csfile.readlines():
                    print(line)
                    slist.append(line.replace("\r", "").replace("\n", ""))

        self.custom_species_list = slist

    def custom_sigmoid(self, x, sensitivity=1.0):
        return 1 / (1.0 + np.exp(-sensitivity * x))

    def convertMetadata(self, m):

        # Convert week_48 to cosine
        if m[2] >= 1 and m[2] <= 48:
            m[2] = math.cos(math.radians(m[2] * 7.5)) + 1
        else:
            m[2] = -1

        # Add binary mask
        mask = np.ones((3,))
        if m[0] == -1 or m[1] == -1:
            mask = np.zeros((3,))
        if m[2] == -1:
            mask[2] = 0.0

        return np.concatenate([m, mask])

    def predict(self, sample, interpreter, sensitivity):

        # Make a prediction
        interpreter.set_tensor(
            self.input_layer_index, np.array(sample[0], dtype="float32")
        )
        interpreter.set_tensor(
            self.mdata_input_index, np.array(sample[1], dtype="float32")
        )
        interpreter.invoke()
        prediction = interpreter.get_tensor(self.output_layer_index)[0]

        # Apply custom sigmoid
        p_sigmoid = self.custom_sigmoid(prediction, sensitivity)

        # Get label and scores for pooled predictions
        p_labels = dict(zip(self.classes, p_sigmoid))

        # Sort by score
        p_sorted = sorted(p_labels.items(), key=operator.itemgetter(1), reverse=True)

        # Remove species that are on blacklist
        for i in range(min(10, len(p_sorted))):
            if p_sorted[i][0] in ["Human_Human", "Non-bird_Non-bird", "Noise_Noise"]:
                p_sorted[i] = (p_sorted[i][0], 0.0)

        # Only return first the top ten results
        return p_sorted[:10]

    def analyze_recording(self, recording):
        print("analyze_recording", recording.path)

        detections = {}
        detection_list = []
        start = time.time()
        print("ANALYZING AUDIO...", end=" ", flush=True)

        # Convert and prepare metadata
        lat = recording.lat or -1  # lite uses -1 for none here.
        lon = recording.lon or -1  # lite uses -1 for none here.
        mdata = self.convertMetadata(np.array([lat, lon, recording.week_48]))
        mdata = np.expand_dims(mdata, 0)

        # Parse every chunk
        pred_start = 0.0
        for c in recording.chunks:

            # Prepare as input signal
            sig = np.expand_dims(c, 0)

            # Make prediction
            p = self.predict([sig, mdata], self.interpreter, recording.sensitivity)

            # Save result and timestamp
            pred_end = pred_start + 3.0
            detections[str(pred_start) + ";" + str(pred_end)] = p
            detection = Detection(pred_start, pred_end, p)
            detection_list.append(detection)
            pred_start = pred_end - recording.overlap

        print("DONE! Time", int((time.time() - start) * 10) / 10.0, "SECONDS")

        recording.detection_dict = detections
        recording.detection_list = detection_list
