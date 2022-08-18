import os

try:
    import tflite_runtime.interpreter as tflite
except:
    from tensorflow import lite as tflite

import numpy as np
from birdnetlib.utils import return_week_48_from_datetime


SPECIES_MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models/analyzer/BirdNET_GLOBAL_3K_V2.2_MData_Model_FP16.tflite",
)
LABEL_PATH = os.path.join(
    os.path.dirname(__file__), "models/analyzer/BirdNET_GLOBAL_3K_V2.2_Labels.txt"
)


class SpeciesList:
    def __init__(self):
        self.lon = None
        self.lat = None
        self.date = None
        self.week_48 = None
        self.threshold = None

        # Labels init
        self.labels = []
        self.load_labels()

        # Model init
        self.meta_interpreter = None
        self.meta_input_details = None
        self.meta_output_details = None
        self.meta_input_layer_index = None
        self.meta_output_layer_index = None

        self.load_species_list_model()

    def return_list(self, lon=None, lat=None, date=None, week_48=-1, threshold=0.3):
        # Returns the list in the format preferred by BirdNET Analyzers.
        # ['Haemorhous mexicanus_House Finch', 'Aphelocoma californica_California Scrub-Jay']

        self.lon = lon
        self.lat = lat
        self.date = date
        self.week_48 = week_48
        self.threshold = threshold

        # Compute date to week_48 format as required by current BirdNET analyzers.
        # TODO: Add a warning if both a date and week_48 value is provided. Currently, date would override explicit week_48.
        if self.week_48 != -1:
            self.week_48 = max(1, min(self.week_48, 48))

        if self.date:
            # Convert date to week_48 format for the Analyzer models.
            self.week_48 = return_week_48_from_datetime(self.date)

        print(self.week_48)

        sample = np.expand_dims(
            np.array(
                [self.lat, self.lon, self.week_48],
                dtype="float32",
            ),
            0,
        )
        self.meta_interpreter.set_tensor(self.meta_input_layer_index, sample)
        self.meta_interpreter.invoke()

        l_filter = self.meta_interpreter.get_tensor(self.meta_output_layer_index)[0]

        # Apply thresho ld
        l_filter = np.where(l_filter >= self.threshold, l_filter, 0)

        # Zip with labels
        l_filter = list(zip(l_filter, self.labels))

        # Sort by filter value
        l_filter = sorted(l_filter, key=lambda x: x[0], reverse=True)

        species_list = []

        for s in l_filter:
            if s[0] >= self.threshold:
                split_name = s[1].split("_")
                item = {
                    "scientific_name": split_name[0],
                    "common_name": split_name[1],
                    "threshold": s[0],
                }
                species_list.append(item)

        print(len(species_list), "species loaded.")
        return species_list

    def load_species_list_model(self):
        print("load_species_list_model")

        model_path = SPECIES_MODEL_PATH
        num_threads = 1  # Default from BN-A config
        self.meta_interpreter = tflite.Interpreter(
            model_path=model_path, num_threads=num_threads
        )
        self.meta_interpreter.allocate_tensors()

        # Get input and output tensors.
        self.meta_input_details = self.meta_interpreter.get_input_details()
        self.meta_output_details = self.meta_interpreter.get_output_details()

        # Get input tensor index
        self.meta_input_layer_index = self.meta_input_details[0]["index"]
        self.meta_output_layer_index = self.meta_output_details[0]["index"]

        print("Meta model loaded.")

    def load_labels(self):
        labels_file_path = LABEL_PATH
        labels = []
        with open(labels_file_path, "r") as lfile:
            for line in lfile.readlines():
                labels.append(line.replace("\n", ""))
        self.labels = labels
        print("Labels loaded.")

    def return_list_for_analyzer(
        self, lon=None, lat=None, date=None, week_48=-1, threshold=0.3
    ):
        species = self.return_list(
            lon=lon, lat=lat, date=date, week_48=week_48, threshold=threshold
        )
        species_split = [f'{i["scientific_name"]}_{i["common_name"]}' for i in species]
        return species_split