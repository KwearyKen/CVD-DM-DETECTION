import joblib
import numpy as np

# Load the model and scaler
model = joblib.load("diabetes_model.pkl")
scaler = joblib.load("scaler.pkl")

# Prompt user for input
print("Enter the following details for diabetes prediction:")

try:
    age = float(input("Age: "))
    gender = input("Gender (Male/Female): ").strip().capitalize()
    hypertension = int(input("Hypertension (0 for No, 1 for Yes): "))
    bmi = float(input("BMI: "))
    blood_glucose_level = float(input("Blood Glucose Level: "))

    # Validate gender input
    if gender not in ['Male', 'Female']:
        raise ValueError("Gender must be 'Male' or 'Female'.")

    # Encode gender
    gender_encoded = 0 if gender == "Male" else 1

    # Scale features (assuming the model was trained with scaled features)
    features = np.array([[age, bmi, blood_glucose_level]])  # Input features for scaling
    features_scaled = scaler.transform(features)  # Use transform instead of fit_transform during prediction

    # Combine all inputs
    input_data = np.array([features_scaled[0][0], gender_encoded, hypertension, features_scaled[0][1], features_scaled[0][2]]).reshape(1, -1)

    # Predict
    prediction = model.predict(input_data)
    print("\nPrediction: ", "Diabetic" if prediction[0] == 1 else "Non-diabetic")

except Exception as e:
    print(f"Error: {e}")

