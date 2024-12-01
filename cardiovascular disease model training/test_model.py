import numpy as np
import cv2
from keras.models import load_model
import os
from keras.preprocessing import image

# Load the model
model_path = r'D:\Python project\Training\ecg_cnn_project\models\ecg_cnn_model.h5'
model = load_model(model_path)

# Define label dictionary
label_dict = {
    0: 'Myocardial_Infarction',
    1: 'History_of_MI',
    2: 'Abnormal_Heartbeat',
    3: 'Normal'
}

# Preprocessing function to prepare the image for prediction
def preprocess_image(img_path):
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (224, 224))  # Resize to match the model input size
    img = img.astype('float32') / 255.0  # Normalize image
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    return img

# Function to predict class of an ECG image
def predict_ecg_image(img_path):
    img = preprocess_image(img_path)
    prediction = model.predict(img)
    predicted_class = np.argmax(prediction, axis=1)[0]  # Get the class with highest probability
    return label_dict[predicted_class]

# Test the model on a new ECG image from the directory
test_image_path = r'D:\Python project\Training\ecg_cnn_project\Normal.jpg'  # Update this path to your test image

prediction = predict_ecg_image(test_image_path)
print(f"Predicted class for the ECG image: {prediction}")
