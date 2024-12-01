import firebase_admin
from firebase_admin import credentials, storage

def initialize_firebase():
    """Initialize Firebase Admin SDK with serviceAccountKey.json."""
    try:
        # Update the path to your service account key file
        cred_path = r"D:\Python project\Medic project\Medic\config\medic-web-app-58ff7-firebase-adminsdk-lgubi-67a7315358.json"
        
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'medic-web-app-58ff7.appspot.com'  # Replace with your Firebase Storage bucket URL
        })
        print("Firebase initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize Firebase: {e}")

def list_files_in_storage():
    """List all files in the Firebase Storage bucket."""
    try:
        # Access the default bucket
        bucket = storage.bucket()
        
        # List all files in the bucket
        blobs = bucket.list_blobs()
        
        print("\nFiles in Firebase Storage:")
        if blobs:
            for blob in blobs:
                print(f" - {blob.name}")
        else:
            print("No files found in the storage bucket.")
    except Exception as e:
        print(f"Error accessing Firebase Storage: {e}")

if __name__ == "__main__":
    initialize_firebase()
    list_files_in_storage()
