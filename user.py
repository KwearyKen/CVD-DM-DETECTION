import json
import os

class User:
    def __init__(self):
        self.user_data = {}
        self.file_path = 'user_data.json'
        self.load_user_data()

    def set_user_data(self, name, gender, age, weight, height, doctor):
        self.user_data = {
            "name": name,
            "gender": gender,
            "age": age,
            "weight": weight,
            "height": height,
            "doctor": doctor
        }
        self.save_user_data()

    def save_user_data(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.user_data, f)

    def load_user_data(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                self.user_data = json.load(f)

    def get_bmi(self):
        if 'weight' in self.user_data and 'height' in self.user_data:
            weight = self.user_data['weight']
            height = self.user_data['height'] / 100  # Convert height to meters
            return weight / (height ** 2)
        return None

    def get_hypertension(self, systolic, diastolic):
        return 1 if systolic > 139 and diastolic > 90 else 0
