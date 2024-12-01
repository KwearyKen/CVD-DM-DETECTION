# firebase_auth.py
import firebase_admin
from firebase_admin import credentials, storage, auth, firestore
import json
from datetime import datetime

# Initialize the Firebase Admin SDK
cred_path = r"D:\Python project\Medic project\Medic\config\medic-web-app-58ff7-firebase-adminsdk-lgubi-67a7315358.json"
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {
    'storageBucket': 'medic-web-app-58ff7.firebasestorage.app'  # Ensure this is the correct bucket name
})

db = firestore.client()
bucket = storage.bucket()

def sign_in(email, password):
    try:
        user = auth.get_user_by_email(email)
        return user.uid
    except auth.UserNotFoundError:
        return None

def upload_pdf(user_id, pdf_path, pdf_filename):
    if user_id is None:
        raise ValueError("User ID is None. Please ensure the user is signed in.")

    folder_path = f"pdfs/{user_id}"
    blob_path = f"{folder_path}/{pdf_filename}"

    # Check if the folder exists by attempting to list blobs with the folder prefix
    blobs = bucket.list_blobs(prefix=folder_path)
    if not list(blobs):
        # Create the folder by uploading a placeholder file
        placeholder_blob = bucket.blob(f"{folder_path}/.placeholder")
        placeholder_blob.upload_from_string("")

    # Upload the PDF to the folder
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(pdf_path)

    # Make the file publicly accessible
    blob.make_public()

    # Generate a public URL for the file
    pdf_url = blob.public_url

    # Save the PDF record to Firestore with local datetime
    pdf_record = {
        'patient_id': user_id,
        'pdf_file': blob_path,
        'pdf_url': pdf_url,
        'upload_date': datetime.now()  # Use local datetime
    }
    db.collection('pdfs').document(pdf_filename).set(pdf_record)
    print(f"Firestore updated with PDF metadata: {pdf_record}")
