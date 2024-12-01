import numpy as np
import cv2
import os
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from keras.utils import to_categorical

# Preprocessing Function
def load_data(path, label_dict):
    data = []
    labels = []
    for category, label_value in label_dict.items():
        category_path = os.path.join(path, category)
        for img_name in os.listdir(category_path):
            img_path = os.path.join(category_path, img_name)
            image = cv2.imread(img_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, (224, 224))
            data.append(image)
            labels.append(label_value)
    return np.array(data), np.array(labels)

# Training and Testing Function
def train_and_test_model():
    # Adjust label_dict keys to match subfolder names in your raw images directory
    label_dict = {
        'Myocardial_Infarction': 0,
        'History_of_MI': 1,
        'Abnormal_Heartbeat': 2,
        'Normal': 3
    }

    # Use the provided raw images directory
    data_dir = r'D:\Python project\Training\ecg_cnn_project\data\train'
    data, labels = load_data(data_dir, label_dict)

    # Normalize data and encode labels
    data = data.astype('float32') / 255.0
    labels = to_categorical(labels, len(label_dict))

    # Split into training and testing sets
    train_data, test_data, train_labels, test_labels = train_test_split(
        data, labels, test_size=0.2, random_state=42
    )

    # Create CNN model
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
        MaxPooling2D((2, 2)),
        Conv2D(32, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Flatten(),
        Dense(256, activation='relu'),
        Dropout(0.5),
        Dense(len(label_dict), activation='softmax')
    ])

    # Compile model
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    # Train model
    history = model.fit(train_data, train_labels, validation_split=0.2, epochs=20, batch_size=32)

    # Save model
    model_save_path = r'D:\Python project\ecg_cnn_project\models\ecg_cnn_model.h5'
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    model.save(model_save_path)
    print(f"Model training complete and saved at {model_save_path}")

    # Evaluate on test data
    test_loss, test_accuracy = model.evaluate(test_data, test_labels)
    print(f"Test Loss: {test_loss}")
    print(f"Test Accuracy: {test_accuracy}")

    # Visualize results
    plot_results(history, test_accuracy)

# Function to plot training history and test accuracy
def plot_results(history, test_accuracy):
    # Plot training & validation accuracy
    plt.figure(figsize=(12, 6))
    plt.plot(history.history['accuracy'], label='Train Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.title(f"Training and Validation Accuracy\nTest Accuracy: {test_accuracy:.2f}")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    train_and_test_model()
