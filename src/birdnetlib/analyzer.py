from multiprocessing.sharedctypes import Value
import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

try:
    import tflite_runtime.interpreter as tflite
except:
    from tensorflow import lite as tflite

import numpy as np
import operator

from birdnetlib.species import SpeciesList

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models/analyzer/BirdNET_GLOBAL_3K_V2.2_Model_FP32.tflite",
)

LABEL_PATH = os.path.join(
    os.path.dirname(__file__), "models/analyzer/BirdNET_GLOBAL_3K_V2.2_Labels.txt"
)


LOCATION_FILTER_THRESHOLD = 0.03


class Detection:
    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
        self.common_name = ""
        self.scientific_name = ""
        self.confidence = 0

    @property
    def as_dict(self):
        return {
            "common_name": self.common_name,
            "scientific_name": self.scientific_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "confidence": self.confidence,
        }


class Analyzer:
    def __init__(self, custom_species_list_path=None):
        self.name = "Analyzer"
        self.model_name = "BirdNET-Analyzer"
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.input_layer_index = None
        self.output_layer_index = None
        self.labels = []
        self.results = []
        self.custom_species_list = []
        self.load_model()
        self.load_labels()

        self.cached_species_lists = {}
        self.custom_species_list_path = None

        self.species_class = SpeciesList()

        if custom_species_list_path:
            self.custom_species_list_path = custom_species_list_path
            self.load_custom_list()

    @property
    def detections(self):
        detections = []
        for key, value in self.results.items():
            # print(f"{key} -----")
            start_time = float(key.split("-")[0])
            end_time = float(key.split("-")[1])
            for c in value:
                confidence = float(c[1])
                scientific_name = c[0].split("_")[0]
                common_name = c[0].split("_")[1]
                # print(c[0], f"{c[1]:1.4f}")
                d = Detection(start_time, end_time)
                d.common_name = common_name
                d.scientific_name = scientific_name
                d.confidence = confidence
                # print(d.as_dict)
                detections.append(d)

        return detections

    def predict(self, sample):
        # Prepare sample and pass through model
        data = np.array([sample], dtype="float32")

        self.interpreter.resize_tensor_input(
            self.input_layer_index, [len(data), *data[0].shape]
        )
        self.interpreter.allocate_tensors()

        # Make a prediction (Audio only for now)
        self.interpreter.set_tensor(
            self.input_layer_index, np.array(data, dtype="float32")
        )
        self.interpreter.invoke()
        prediction = self.interpreter.get_tensor(self.output_layer_index)

        # Logits or sigmoid activations?
        APPLY_SIGMOID = True
        if APPLY_SIGMOID:
            SIGMOID_SENSITIVITY = 1.0
            prediction = self.flat_sigmoid(
                np.array(prediction), sensitivity=-SIGMOID_SENSITIVITY
            )

        return prediction

    def flat_sigmoid(self, x, sensitivity=-1):
        return 1 / (1.0 + np.exp(sensitivity * np.clip(x, -15, 15)))

    def return_predicted_species_list(
        self,
        lon=None,
        lat=None,
        week_48=None,
        filter_threshold=LOCATION_FILTER_THRESHOLD,
    ):

        print("return_predicted_species_list")

        return self.species_class.return_list_for_analyzer(
            lat=lat, lon=lon, week_48=week_48, threshold=filter_threshold
        )


    def set_predicted_species_list_from_position(self, recording):
        print("set_predicted_species_list_from_position")

        # Check to see if this species list has been previously cached.
        list_key = f"list-{recording.lon}-{recording.lat}-{recording.week_48}"

        if list_key in self.cached_species_lists:
            self.custom_species_list = self.cached_species_lists[list_key]
            return

        species_list = self.return_predicted_species_list(
            lon=recording.lon,
            lat=recording.lat,
            week_48=recording.week_48,
        )
        self.custom_species_list = species_list

        # Save to analyzer's cache.
        self.cached_species_lists[list_key] = species_list

    def analyze_recording(self, recording):
        print("analyze_recording", recording.path)

        if self.custom_species_list_path and recording.lon and recording.lat:
            raise ValueError(
                "Recording lon/lat should not be used in conjunction with a custom species list."
            )

        # If recording has lon/lat, load cached list or predict a new species list.
        if recording.lon and recording.lat:
            print("recording has lon/lat")
            self.set_predicted_species_list_from_position(recording)

        start = 0
        end = recording.sample_secs
        results = {}
        for c in recording.chunks:

            pred = self.predict(c)[0]

            # Assign scores to labels
            p_labels = dict(zip(self.labels, pred))

            # Sort by score
            p_sorted = sorted(
                p_labels.items(), key=operator.itemgetter(1), reverse=True
            )

            # Store top 5 results and advance indicies
            results[str(start) + "-" + str(end)] = p_sorted[:5]

            # Increment start and end
            start += recording.sample_secs - recording.overlap
            end = start + recording.sample_secs

        self.results = results
        recording.detection_list = self.detections

    def load_model(self):
        print("load model")
        # Load TFLite model and allocate tensors.
        model_path = MODEL_PATH
        num_threads = 1  # Default from BN-A config
        self.interpreter = tflite.Interpreter(
            model_path=model_path, num_threads=num_threads
        )
        self.interpreter.allocate_tensors()

        # Get input and output tensors.
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        # Get input tensor index
        self.input_layer_index = self.input_details[0]["index"]
        self.output_layer_index = self.output_details[0]["index"]

        print("Model loaded.")


    def load_labels(self):
        labels_file_path = LABEL_PATH
        labels = []
        with open(labels_file_path, "r") as lfile:
            for line in lfile.readlines():
                labels.append(line.replace("\n", ""))
        self.labels = labels
        print("Labels loaded.")

    def load_custom_list(self):
        species_list = []
        if os.path.isfile(self.custom_species_list_path):
            with open(self.custom_species_list_path, "r") as csfile:
                for line in csfile.readlines():
                    print(line)
                    species_list.append(line.replace("\r", "").replace("\n", ""))

        self.custom_species_list = species_list
        print(len(species_list), "species loaded.")