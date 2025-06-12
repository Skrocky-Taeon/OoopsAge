import os
import firebase_admin
from firebase_admin import credentials, storage
import logging

logger = logging.getLogger(__name__)

class FirebaseService:
    """Service for Firebase Storage operations"""
    
    def __init__(self):
        self.firebase_initialized = False
        self.initialize_firebase()
        
    def initialize_firebase(self):
        """Initialize Firebase with credentials from environment variables"""
        try:
            # Check if Firebase credentials are available in environment variables
            firebase_api_key = os.environ.get('FIREBASE_API_KEY')
            firebase_auth_domain = os.environ.get('FIREBASE_AUTH_DOMAIN')
            firebase_project_id = os.environ.get('FIREBASE_PROJECT_ID')
            firebase_storage_bucket = os.environ.get('FIREBASE_STORAGE_BUCKET')
            firebase_messaging_sender_id = os.environ.get('FIREBASE_MESSAGING_SENDER_ID')
            firebase_app_id = os.environ.get('FIREBASE_APP_ID')
            
            if (not firebase_api_key or not firebase_auth_domain or not firebase_project_id or 
                not firebase_storage_bucket or not firebase_messaging_sender_id or not firebase_app_id):
                logger.warning("Firebase credentials not found in environment variables")
                return False
            
            # Initialize Firebase if not already initialized
            if not self.firebase_initialized and not firebase_admin._apps:
                cred = credentials.Certificate({
                    "type": "service_account",
                    "project_id": firebase_project_id,
                    "private_key_id": os.environ.get('FIREBASE_PRIVATE_KEY_ID', ''),
                    "private_key": os.environ.get('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                    "client_email": os.environ.get('FIREBASE_CLIENT_EMAIL', ''),
                    "client_id": os.environ.get('FIREBASE_CLIENT_ID', ''),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": os.environ.get('FIREBASE_CLIENT_CERT_URL', '')
                })
                
                firebase_admin.initialize_app(cred, {
                    'storageBucket': firebase_storage_bucket
                })
                
                self.firebase_initialized = True
                logger.info("Firebase initialized successfully")
                return True
            elif firebase_admin._apps:
                # Firebase is already initialized
                self.firebase_initialized = True
                logger.info("Firebase was already initialized")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error initializing Firebase: {e}")
            return False
    
    def upload_image(self, image_path, destination_path):
        """
        Upload an image to Firebase Storage
        
        Args:
            image_path (str): Local path to the image file
            destination_path (str): Path in Firebase Storage
            
        Returns:
            str: Public URL of the uploaded image or None if upload failed
        """
        if not self.firebase_initialized:
            if not self.initialize_firebase():
                logger.warning("Firebase not initialized, using local storage instead")
                return None
        
        try:
            bucket = storage.bucket()
            blob = bucket.blob(destination_path)
            
            # Upload the file
            with open(image_path, 'rb') as file:
                blob.upload_from_file(file)
            
            # Make the blob publicly accessible
            blob.make_public()
            
            # Return the public URL
            return blob.public_url
        except Exception as e:
            logger.error(f"Error uploading image to Firebase: {e}")
            return None
        
    def delete_image(self, image_path):
        """
        Delete an image from Firebase Storage
        
        Args:
            image_path (str): Path of the image in Firebase Storage
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        if not self.firebase_initialized:
            if not self.initialize_firebase():
                logger.warning("Firebase not initialized, cannot delete image")
                return False
        
        try:
            bucket = storage.bucket()
            blob = bucket.blob(image_path)
            
            # Delete the blob
            blob.delete()
            
            return True
        except Exception as e:
            logger.error(f"Error deleting image from Firebase: {e}")
            return False