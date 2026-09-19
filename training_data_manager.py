#!/usr/bin/env python3
import json
from pathlib import Path

class TrainingDataManager:
    def __init__(self):
        self.test_data_dir = Path('test_data')
    
    def load_training_data(self):
        try:
            with open(self.test_data_dir / 'training_dataset_sample.json') as f:
                return json.load(f)
        except:
            return []
