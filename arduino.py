import serial
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import io

def fetch_ecg_from_arduino():
    # Open the serial port (adjust the port as needed for Windows)
    ser = serial.Serial('COM11', 9600)  # Change 'COM11' to the correct port

    # Read ECG data from the Arduino
    ecg_data = []
    for _ in range(500):  # Adjust the range as needed
        line = ser.readline().decode('utf-8').strip()
        ecg_data.append(float(line))

    # Close the serial port
    ser.close()

    # Create a 12-lead-like image
    ecg_image = create_12_lead_image(ecg_data)

    return ecg_image

def create_12_lead_image(ecg_data):
    # Create a figure with 4 subplots
    fig, axs = plt.subplots(4, 1, figsize=(10, 8), sharex=True)

    # Plot the ECG data on each subplot
    for i in range(4):
        axs[i].plot(ecg_data)
        axs[i].set_ylabel(f'Lead {i+1}')

    # Add labels and title
    axs[3].set_xlabel('Time')
    fig.suptitle('ECG Report')

    # Save the figure to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image = Image.open(buf)
    plt.close(fig)

    return image