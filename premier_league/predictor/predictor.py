import numpy as np
import pandas as pd


class Predictor:
    def __init__(self, dataset_dir: str):
        self.dataset = dataset_dir
        self.data = pd.read_csv(self.dataset)

    def forward_propagation(self):
        """
        Forward propagation function to compute the predictions.
        """
