import warnings
warnings.filterwarnings('ignore')

# Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import joblib  # For saving the model and scaler

# Load dataset
file_path = r"D:\Python project\diabetes_training\diabetes_prediction_dataset.csv"
df = pd.read_csv(file_path)

# Select relevant features
df = df[['age', 'gender', 'hypertension', 'bmi', 'blood_glucose_level', 'diabetes']]

# Encode gender (Male=0, Female=1)
df['gender'] = df['gender'].map({'Male': 0, 'Female': 1})

# Check for missing values
print("Missing values before:", df.isnull().sum())
df.dropna(inplace=True)  # Drop rows with missing values
print("Missing values after:", df.isnull().sum())

# Split features and target
X = df[['age', 'gender', 'hypertension', 'bmi', 'blood_glucose_level']]
y = df['diabetes']

# Scale numerical features
scaler = StandardScaler()
X[['age', 'bmi', 'blood_glucose_level']] = scaler.fit_transform(X[['age', 'bmi', 'blood_glucose_level']])

# Save the scaler
joblib.dump(scaler, "scaler.pkl")

# Split into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Random Forest Accuracy: {accuracy:.2f}")
print("Classification Report:\n", classification_report(y_test, y_pred))

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Non-diabetic', 'Diabetic'], yticklabels=['Non-diabetic', 'Diabetic'])
plt.title("Random Forest Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("True")
plt.show()

# Save the trained model
joblib.dump(model, "diabetes_model.pkl")
