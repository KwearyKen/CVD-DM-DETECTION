from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os
import joblib
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# Define the paths to the models and scaler
DIABETES_MODEL_PATH = r'D:\Python project\Medic project\Medic\model\diabetes_model.pkl'
SCALER_PATH = r'D:\Python project\Medic project\Medic\model\scaler.pkl'
ECG_CNN_MODEL_PATH = r'D:\Python project\Medic project\Medic\model\ecg_cnn_model.h5'

# Load the models and scaler
diabetes_model = joblib.load(DIABETES_MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
ecg_cnn_model = load_model(ECG_CNN_MODEL_PATH)

class ScanProcess:
    def __init__(self):
        self.results = {}
        self.ecg_data = None
        self.systolic = None
        self.diastolic = None
        self.blood_glucose_level = None

    def preprocess_ecg_image(self, image_path):
        img = load_img(image_path, target_size=(224, 224))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0
        return img_array

    def process_data(self, user):
        # Preprocess ECG data
        ecg_image_array = self.preprocess_ecg_image(self.ecg_data)

        # Make predictions
        ecg_prediction = ecg_cnn_model.predict(ecg_image_array)
        ecg_result = np.argmax(ecg_prediction, axis=1)[0]
        ecg_labels = {0: 'Myocardial_Infarction', 1: 'History_of_MI', 2: 'Abnormal_Heartbeat', 3: 'Normal'}
        ecg_result = ecg_labels[ecg_result]

        # Prepare diabetes prediction data
        bmi = user.get_bmi()
        hypertension = user.get_hypertension(int(self.systolic), int(self.diastolic))

        # Scale the features that were used during training
        features_to_scale = np.array([[
            user.user_data["age"],
            bmi,
            int(self.blood_glucose_level)
        ]])
        features_scaled = scaler.transform(features_to_scale)

        # Combine all inputs
        diabetes_data = np.array([[
            features_scaled[0][0],  # Scaled age
            user.user_data["gender"],
            hypertension,
            features_scaled[0][1],  # Scaled BMI
            features_scaled[0][2]   # Scaled blood glucose level
        ]])

        diabetes_prediction = diabetes_model.predict(diabetes_data)
        diabetes_result = "Diabetic" if diabetes_prediction[0] == 1 else "Non-Diabetic"

        # Determine hypertension status
        hypertension_status = "Hypertensive" if hypertension == 1 else "Non-Hypertensive"

        # Generate Results
        self.results = {
            "ecg_result": ecg_result,
            "diabetes_result": diabetes_result,
            "hypertension_status": hypertension_status
        }

        # Generate Health Advice
        health_advice = self.generate_health_advice()
        self.results["health_advice"] = health_advice

        return self.results

    
    def generate_health_advice(self):
        ecg_result = self.results.get("ecg_result")
        diabetes_result = self.results.get("diabetes_result")

        advice = ""

        if ecg_result == "Myocardial_Infarction":
            advice += "You have signs of Myocardial Infarction. Seek immediate medical attention.\n"
            if diabetes_result == "Diabetic":
                advice += "Being diabetic increases your risk. Monitor your blood sugar levels closely and follow a strict diet and medication plan.\n"
            else:
                advice += "Even though you are non-diabetic, maintaining a healthy lifestyle is crucial to prevent future complications.\n"
        elif ecg_result == "History_of_MI":
            advice += "You have a history of Myocardial Infarction. Regular check-ups are advised.\n"
            if diabetes_result == "Diabetic":
                advice += "Managing your diabetes is essential to prevent further cardiovascular issues. Follow your doctor's advice closely.\n"
            else:
                advice += "Continue with regular check-ups and maintain a healthy lifestyle to prevent future heart problems.\n"
        elif ecg_result == "Abnormal_Heartbeat":
            advice += "You have an abnormal heartbeat. Consult a cardiologist for further evaluation.\n"
            if diabetes_result == "Diabetic":
                advice += "Diabetes can exacerbate heart issues. Ensure you monitor your blood sugar levels and follow your treatment plan.\n"
            else:
                advice += "Regular monitoring and a healthy lifestyle can help manage your heart condition.\n"
        else:  # Normal
            advice += "Your ECG results are normal. Keep up with regular check-ups.\n"
            if diabetes_result == "Diabetic":
                advice += "Even with normal ECG results, managing your diabetes is important. Follow your diet and medication plan.\n"
            else:
                advice += "Maintain a healthy lifestyle to prevent future health issues.\n"

        return advice
    
    def generate_pdf(self, user, pdf_path):
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2.0, height - 50, "Patient Health Monitoring Report")

        # User Information
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 100, f"Name: {user.user_data['name']}")
        c.drawString(50, height - 120, f"Age: {user.user_data['age']}")
        c.drawString(50, height - 140, f"Gender: {'Male' if user.user_data['gender'] == 0 else 'Female'}")
        c.drawString(50, height - 160, f"Weight: {user.user_data['weight']} kg")
        c.drawString(50, height - 180, f"Height: {user.user_data['height']} cm")
        c.drawString(50, height - 200, f"Assigned Doctor: {user.user_data['doctor']}")

        # Scan Results
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 240, "Scan Results:")
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 260, f"ECG Result: {self.results['ecg_result']}")
        c.drawString(50, height - 280, f"Diabetes Result: {self.results['diabetes_result']}")
        c.drawString(50, height - 300, f"Hypertension Status: {self.results['hypertension_status']}")
        c.drawString(50, height - 320, f"Systolic BP: {self.systolic} mmHg")
        c.drawString(50, height - 340, f"Diastolic BP: {self.diastolic} mmHg")
        c.drawString(50, height - 360, f"Blood Glucose: {self.blood_glucose_level} mg/dL")

        # Health Advice
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 400, "Health Advice:")
        c.setFont("Helvetica", 12)
        advice_lines = self.results['health_advice'].split('\n')
        y_position = height - 420
        for line in advice_lines:
            c.drawString(50, y_position, line)
            y_position -= 20

        # ECG Image
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position - 40, "ECG Image:")
        ecg_image = ImageReader(self.ecg_data)
        c.drawImage(ecg_image, 50, y_position - 300, width=400, height=300)

        c.save()
