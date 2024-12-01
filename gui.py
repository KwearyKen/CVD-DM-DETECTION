import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from user import User
from scan import ScanProcess
from datetime import datetime
import os
import subprocess
from arduino import fetch_ecg_from_arduino
from PIL import ImageTk, Image
from firebase_auth import sign_in, upload_pdf
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class SignIn:
    def __init__(self, root):
        self.root = root
        self.logged_in = False
        self.user_id = None
        self.load_credentials()

    def load_credentials(self):
        try:
            with open(r"D:\Python project\Medic project\Medic\credentials.json", "r") as file:
                credentials = json.load(file)
                self.email = credentials.get("email")
                self.password = credentials.get("password")
                self.user_id = credentials.get("user_id")
                print(f"Loaded credentials: email={self.email}, user_id={self.user_id}")
        except FileNotFoundError:
            self.email = None
            self.password = None
            self.user_id = None
            print("Credentials file not found.")
            messagebox.showinfo("Sign In Required", "Credentials file not found. Please sign in.")
            self.login()

    def save_credentials(self):
        with open(r"D:\Python project\Medic project\Medic\credentials.json", "w") as file:
            json.dump({"email": self.email, "password": self.password, "user_id": self.user_id}, file)
            print(f"Saved credentials: email={self.email}, user_id={self.user_id}")

    def login(self):
        if self.email and self.password:
            self.user_id = sign_in(self.email, self.password)
            if self.user_id:
                messagebox.showinfo("Sign In", "User signed in successfully!")
                self.logged_in = True
                self.save_credentials()
            else:
                messagebox.showerror("Sign In", "Invalid email or password.")
                self.email, self.password = self.ask_credentials()
                self.user_id = sign_in(self.email, self.password)
                if self.user_id:
                    messagebox.showinfo("Sign In", "User signed in successfully!")
                    self.logged_in = True
                    self.save_credentials()
                else:
                    messagebox.showerror("Sign In", "Invalid email or password.")
        else:
            self.email, self.password = self.ask_credentials()
            self.user_id = sign_in(self.email, self.password)
            if self.user_id:
                messagebox.showinfo("Sign In", "User signed in successfully!")
                self.logged_in = True
                self.save_credentials()
            else:
                messagebox.showerror("Sign In", "Invalid email or password.")

    def ask_credentials(self):
        while True:
            email = self.ask_email()
            if email:
                password = self.ask_password()
                if password:
                    return email, password
            messagebox.showerror("Error", "Email and password cannot be empty.")

    def ask_email(self):
        email_window = tk.Toplevel(self.root)
        email_window.title("Enter Email")
        email_window.geometry("300x150+{}+{}".format(self.root.winfo_x() + 50, self.root.winfo_y() + 50))
        email_window.transient(self.root)
        email_window.grab_set()

        email_label = tk.Label(email_window, text="Enter your email:")
        email_label.pack(pady=10)

        email_entry = tk.Entry(email_window)
        email_entry.pack(pady=10)

        email = []

        def submit_email():
            email.append(email_entry.get())
            email_window.destroy()

        submit_button = tk.Button(email_window, text="Submit", command=submit_email)
        submit_button.pack(pady=10)

        email_window.wait_window(email_window)
        return email[0] if email else None

    def ask_password(self):
        password_window = tk.Toplevel(self.root)
        password_window.title("Enter Password")
        password_window.geometry("300x150+{}+{}".format(self.root.winfo_x() + 50, self.root.winfo_y() + 50))
        password_window.transient(self.root)
        password_window.grab_set()

        password_label = tk.Label(password_window, text="Enter your password:")
        password_label.pack(pady=10)

        password_entry = tk.Entry(password_window, show='*')
        password_entry.pack(pady=10)

        password = []

        def submit_password():
            password.append(password_entry.get())
            password_window.destroy()

        submit_button = tk.Button(password_window, text="Submit", command=submit_password)
        submit_button.pack(pady=10)

        password_window.wait_window(password_window)
        return password[0] if password else None

    def update_credentials(self):
        new_email, new_password = self.ask_credentials()
        if new_email and new_password:
            self.user_id = sign_in(new_email, new_password)
            if self.user_id:
                self.email = new_email
                self.password = new_password
                messagebox.showinfo("Update Credentials", "Credentials updated successfully!")
                self.save_credentials()
            else:
                messagebox.showerror("Update Credentials", "Invalid email or password.")
        else:
            messagebox.showerror("Update Credentials", "Email and password cannot be empty.")

class HealthMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Patient Health Monitoring System")
        self.root.geometry("800x480")

        self.sign_in = SignIn(root)
        self.user = User()
        self.scan_process = ScanProcess()
        self.load_emails()

        self.create_widgets()

    def load_emails(self):
        try:
            with open(r"D:\Python project\Medic project\Medic\emails.json", "r") as file:
                emails = json.load(file)
                self.doctor_email = emails.get("doctor_email")
                self.emergency_email = emails.get("emergency_email")
                print(f"Loaded emails: doctor_email={self.doctor_email}, emergency_email={self.emergency_email}")
        except FileNotFoundError:
            self.doctor_email = None
            self.emergency_email = None
            print("Emails file not found.")

    def save_emails(self):
        with open(r"D:\Python project\Medic project\Medic\emails.json", "w") as file:
            json.dump({"doctor_email": self.doctor_email, "emergency_email": self.emergency_email}, file)
            print(f"Saved emails: doctor_email={self.doctor_email}, emergency_email={self.emergency_email}")

    def create_widgets(self):
        font_size = 14
        self.title_label = tk.Label(self.root, text="Patient Health Monitoring System", font=("Arial", 20))
        self.title_label.pack(pady=20)

        self.sign_in_button = tk.Button(self.root, text="Sign In", command=self.sign_in.login, width=10, height=2, font=("Arial", font_size))
        self.sign_in_button.place(x=20, y=20)

        self.update_credentials_button = tk.Button(self.root, text="Update Acc", command=self.sign_in.update_credentials, width=12, height=2, font=("Arial", font_size))
        self.update_credentials_button.place(x=20, y=420)

        self.body_data_button = tk.Button(self.root, text="User Data", command=self.show_data_input, width=12, height=2, font=("Arial", font_size))
        self.body_data_button.place(x=640, y=20)

        self.scan_button = tk.Button(self.root, text="Start Scan", command=lambda: self.start_scan(self.root), width=20, height=3, font=("Arial", font_size))
        self.scan_button.pack(pady=50)

        self.history_button = tk.Button(self.root, text="Check History", command=self.check_history, width=20, height=3, font=("Arial", font_size))
        self.history_button.pack(pady=20)

        self.email_button = tk.Button(self.root, text="Update Emails", command=self.update_emails, width=12, height=2, font=("Arial", font_size))
        self.email_button.place(x=640, y=420)

    def show_data_input(self):
        input_window = tk.Toplevel(self.root)
        input_window.title("Input User Data")
        input_window.geometry("400x400")

        # Create a frame to hold the input fields
        input_frame = tk.Frame(input_window)
        input_frame.pack(pady=20)

        tk.Label(input_frame, text="Name").grid(row=0, column=0, pady=5)
        name_entry = tk.Entry(input_frame)
        name_entry.grid(row=0, column=1, pady=5)

        tk.Label(input_frame, text="Gender (0 for Male, 1 for Female)").grid(row=1, column=0, pady=5)
        gender_entry = tk.Entry(input_frame)
        gender_entry.grid(row=1, column=1, pady=5)

        tk.Label(input_frame, text="Age").grid(row=2, column=0, pady=5)
        age_entry = tk.Entry(input_frame)
        age_entry.grid(row=2, column=1, pady=5)

        tk.Label(input_frame, text="Weight (kg)").grid(row=3, column=0, pady=5)
        weight_entry = tk.Entry(input_frame)
        weight_entry.grid(row=3, column=1, pady=5)

        tk.Label(input_frame, text="Height (cm)").grid(row=4, column=0, pady=5)
        height_entry = tk.Entry(input_frame)
        height_entry.grid(row=4, column=1, pady=5)

        tk.Label(input_frame, text="Assigned Doctor").grid(row=5, column=0, pady=5)
        doctor_entry = tk.Entry(input_frame)
        doctor_entry.grid(row=5, column=1, pady=5)

        def submit_data():
            name = name_entry.get()
            gender = int(gender_entry.get())
            age = int(age_entry.get())
            weight = float(weight_entry.get())
            height = float(height_entry.get())
            doctor = doctor_entry.get()

            self.user.set_user_data(name, gender, age, weight, height, doctor)
            messagebox.showinfo("Data Input", "User data saved successfully!")
            input_window.destroy()

        # Submit Button
        submit_button = tk.Button(input_window, text="Submit", command=submit_data)
        submit_button.pack(pady=20)

    def check_history(self):
        pdf_dir = r"D:\Python project\Medic project\Medic\PDF"
        if os.path.exists(pdf_dir):
            if os.name == 'nt':  # For Windows
                os.startfile(pdf_dir)
            elif os.name == 'posix':  # For macOS and Linux
                subprocess.call(["open", pdf_dir])
            else:
                messagebox.showerror("Error", "Unsupported operating system.")
        else:
            messagebox.showerror("Error", "PDF directory does not exist.")

    def start_scan(self, root):
        scan_process_gui = ScanProcessGUI(root, self.scan_process, self.user, self.sign_in, self.doctor_email, self.emergency_email)
        scan_process_gui.start_scan(root)

    def update_emails(self):
        email_window = tk.Toplevel(self.root)
        email_window.title("Update Emails")

        # Calculate the screen dimensions and position the window at the center
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 400
        window_height = 200
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        email_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        email_window.transient(self.root)
        email_window.grab_set()

        # Create a frame to hold the input fields
        email_frame = tk.Frame(email_window)
        email_frame.pack(pady=20)

        # Configure the grid to center the widgets
        email_frame.columnconfigure(0, weight=1)
        email_frame.columnconfigure(1, weight=1)
        email_frame.rowconfigure(0, weight=1)
        email_frame.rowconfigure(1, weight=1)
        email_frame.rowconfigure(2, weight=1)

        tk.Label(email_frame, text="Doctor's Email:").grid(row=0, column=0, pady=5, sticky="e")
        doctor_email_entry = tk.Entry(email_frame)
        doctor_email_entry.grid(row=0, column=1, pady=5, sticky="w")

        tk.Label(email_frame, text="Emergency Email:").grid(row=1, column=0, pady=5, sticky="e")
        emergency_email_entry = tk.Entry(email_frame)
        emergency_email_entry.grid(row=1, column=1, pady=5, sticky="w")

        def submit_emails():
            self.doctor_email = doctor_email_entry.get()
            self.emergency_email = emergency_email_entry.get()
            self.save_emails()
            messagebox.showinfo("Update Emails", "Emails updated successfully!")
            email_window.destroy()

        submit_button = tk.Button(email_frame, text="Submit", command=submit_emails)
        submit_button.grid(row=2, column=0, columnspan=2, pady=20)

class ScanProcessGUI:
    def __init__(self, root, scan_process, user, sign_in, doctor_email, emergency_email):
        self.root = root
        self.scan_process = scan_process
        self.user = user
        self.sign_in = sign_in
        self.doctor_email = doctor_email
        self.emergency_email = emergency_email

    def start_scan(self, root):
        # Get the size of the main window
        main_window_width = root.winfo_width()
        main_window_height = root.winfo_height()

        scan_window = tk.Toplevel(root)
        scan_window.title("Scan Process")
        scan_window.geometry(f"{main_window_width}x{main_window_height}")

        # Make the scan window stay on top of the main window
        scan_window.transient(root)
        scan_window.grab_set()

        # Increase font size and padding for better visibility
        font_size = 14
        padding = 10

        # Create frames to organize the widgets
        main_frame = tk.Frame(scan_window)
        main_frame.pack(padx=padding, pady=padding, fill='both', expand=True)

        # Configure the grid to center the widgets
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(3, weight=1)
        main_frame.rowconfigure(4, weight=1)
        main_frame.rowconfigure(5, weight=1)
        main_frame.rowconfigure(6, weight=1)
        main_frame.rowconfigure(7, weight=1)

        # ECG Data Options
        tk.Label(main_frame, text="Step 1: Select ECG Data Source", font=("Arial", font_size)).grid(row=0, column=0, columnspan=2, pady=padding, sticky="nsew")
        tk.Button(main_frame, text="Get ECG from Arduino", command=self.fetch_ecg_from_arduino, font=("Arial", font_size)).grid(row=1, column=0, pady=padding, padx=padding, sticky="nsew")
        tk.Button(main_frame, text="Upload ECG Image", command=self.upload_ecg_image, font=("Arial", font_size)).grid(row=1, column=1, pady=padding, padx=padding, sticky="nsew")

        # Blood Pressure Input
        tk.Label(main_frame, text="Step 2: Enter Blood Pressure", font=("Arial", font_size)).grid(row=2, column=0, columnspan=2, pady=padding, sticky="nsew")

        tk.Label(main_frame, text="Systolic Blood Pressure", font=("Arial", font_size)).grid(row=3, column=0, pady=padding, padx=padding, sticky="e")
        systolic_entry = tk.Entry(main_frame, font=("Arial", font_size))
        systolic_entry.grid(row=3, column=1, pady=padding, padx=padding, sticky="nsew")

        tk.Label(main_frame, text="Diastolic Blood Pressure", font=("Arial", font_size)).grid(row=4, column=0, pady=padding, padx=padding, sticky="e")
        diastolic_entry = tk.Entry(main_frame, font=("Arial", font_size))
        diastolic_entry.grid(row=4, column=1, pady=padding, padx=padding, sticky="nsew")

        # Blood Glucose Level Input
        tk.Label(main_frame, text="Step 3: Enter Blood Glucose Level", font=("Arial", font_size)).grid(row=5, column=0, columnspan=2, pady=padding, sticky="nsew")
        bg_entry = tk.Entry(main_frame, font=("Arial", font_size))
        bg_entry.grid(row=6, column=0, columnspan=2, pady=padding, padx=padding, sticky="nsew")

        def submit_data():
            self.scan_process.systolic = systolic_entry.get()
            self.scan_process.diastolic = diastolic_entry.get()
            self.scan_process.blood_glucose_level = bg_entry.get()

            # Validate Inputs
            if not self.scan_process.ecg_data:
                messagebox.showerror("Error", "Please provide ECG data.")
                return
            if not self.scan_process.systolic.isdigit():
                messagebox.showerror("Error", "Invalid systolic blood pressure value.")
                return
            if not self.scan_process.diastolic.isdigit():
                messagebox.showerror("Error", "Invalid diastolic blood pressure value.")
                return
            if not self.scan_process.blood_glucose_level.isdigit():
                messagebox.showerror("Error", "Invalid blood glucose level value.")
                return

            # Process Data
            results = self.scan_process.process_data(self.user)

            # Show results in a message box
            messagebox.showinfo(
                "Results",
                f"Scan Complete:\n"
                f"ECG Result: {results['ecg_result']}\n"
                f"Diabetes Result: {results['diabetes_result']}\n"
                f"Hypertension Status: {results['hypertension_status']}\n"
                f"Systolic BP: {self.scan_process.systolic} mmHg\n"
                f"Diastolic BP: {self.scan_process.diastolic} mmHg\n"
                f"Blood Glucose: {self.scan_process.blood_glucose_level} mg/dL\n"
                f"Health Advice: {results['health_advice']}"
            )

            # Ensure the PDF directory exists
            pdf_dir = r"D:\Python project\Medic project\Medic\PDF"
            if not os.path.exists(pdf_dir):
                os.makedirs(pdf_dir)

            # Get the current date and time
            current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            # Format the filename
            user_name = self.user.user_data['name'].replace(" ", "_")  # Replace spaces with underscores
            pdf_filename = f"{user_name}_{current_datetime}_health_report.pdf"
            pdf_path = os.path.join(pdf_dir, pdf_filename)

            # Generate and save PDF
            self.scan_process.generate_pdf(self.user, pdf_path)
            messagebox.showinfo("PDF Generation", f"PDF report generated and saved at: {pdf_path}")

            # Upload the PDF to Firebase Storage
            user_id = self.sign_in.user_id
            print(f"Uploading PDF with user_id: {user_id}")
            upload_pdf(user_id, pdf_path, pdf_filename)
            messagebox.showinfo("Upload", f"PDF report uploaded to Firebase Storage.")

            # Send email with the PDF
            self.send_email(pdf_path, pdf_filename)

            # Release the grab
            scan_window.grab_release()
            scan_window.destroy()


        # Submit Button
        tk.Button(main_frame, text="Submit and View Results", command=submit_data, font=("Arial", font_size)).grid(row=7, column=0, columnspan=2, pady=padding, sticky="nsew")

    def fetch_ecg_from_arduino(self):
        try:
            # Fetch ECG data from Arduino and create the image
            ecg_image = fetch_ecg_from_arduino()

            # Save the image to a temporary file
            temp_image_path = "temp_ecg_image.png"
            ecg_image.save(temp_image_path)

            # Set the ECG data path
            self.scan_process.ecg_data = temp_image_path

            messagebox.showinfo("ECG Scan", f"ECG data retrieved from Arduino and image generated.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch ECG data from Arduino: {e}")

    def upload_ecg_image(self):
        file_path = filedialog.askopenfilename(
            title="Select ECG Image",
            filetypes=(("Image Files", "*.png;*.jpg;*.jpeg"), ("All Files", "*.*"))
        )
        if file_path:
            self.scan_process.ecg_data = file_path
            messagebox.showinfo("ECG Scan", f"ECG image uploaded: {file_path}")

    def send_email(self, pdf_path, pdf_filename):
        sender_email = "appmedic138@gmail.com"
        sender_password = "atxx mugt tpss nvfe"  # Replace with your app password
        recipient_emails = [self.doctor_email, self.emergency_email]
        subject = "Health Report"
        body = (f"Please find the attached health report for {self.user.user_data['name']}."
                f"with Patient ID: {self.sign_in.user_id}.")

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ", ".join(recipient_emails)
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        # Attach the PDF file
        with open(pdf_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {pdf_filename}',
            )
            msg.attach(part)

        # Send the email
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, recipient_emails, text)
            server.quit()
            messagebox.showinfo("Email Sent", f"Email sent to {', '.join(recipient_emails)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HealthMonitorApp(root)
    root.mainloop()
