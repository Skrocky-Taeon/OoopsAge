import os
import logging
import base64
import json
import requests
from datetime import datetime, timedelta
import uuid
from io import BytesIO
import firebase_admin
from firebase_admin import credentials, storage, initialize_app

logger = logging.getLogger(__name__)

# Flag to track if Firebase has been initialized
firebase_initialized = False

def initialize_firebase():
    """Initialize Firebase if it hasn't been already."""
    global firebase_initialized
    
    if firebase_initialized:
        return True
    
    try:
        # Check for Firebase credentials
        firebase_api_key = os.environ.get('FIREBASE_API_KEY')
        firebase_auth_domain = os.environ.get('FIREBASE_AUTH_DOMAIN')
        firebase_project_id = os.environ.get('FIREBASE_PROJECT_ID')
        firebase_storage_bucket = os.environ.get('FIREBASE_STORAGE_BUCKET')
        
        # If we have a service account JSON, use it
        if os.environ.get('FIREBASE_SERVICE_ACCOUNT'):
            # Parse the JSON string into a dictionary
            service_account_info = json.loads(os.environ.get('FIREBASE_SERVICE_ACCOUNT'))
            cred = credentials.Certificate(service_account_info)
            firebase_admin.initialize_app(cred, {
                'storageBucket': firebase_storage_bucket
            })
            firebase_initialized = True
            logger.debug("Firebase initialized with service account")
            return True
            
        # If we have individual environment variables, try to use them
        elif firebase_api_key and firebase_storage_bucket:
            # Create a default app with storage bucket
            firebase_admin.initialize_app(options={
                'apiKey': firebase_api_key,
                'authDomain': firebase_auth_domain,
                'projectId': firebase_project_id,
                'storageBucket': firebase_storage_bucket
            })
            firebase_initialized = True
            logger.debug("Firebase initialized with environment variables")
            return True
        
        else:
            logger.warning("Firebase credentials not found in environment variables")
            return False
            
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {str(e)}")
        return False

def upload_image(file, user_id):
    """
    Upload an image to cloud storage.
    
    Args:
        file: FileStorage object from Flask request
        user_id: User ID for organizing files
        
    Returns:
        tuple: (path, url) - The path and URL to the stored image
    """
    # Generate unique filename
    filename = f"{user_id}_{uuid.uuid4().hex}.jpg"
    
    # Read image data
    image_data = BytesIO(file.read())
    file.seek(0)  # Reset file pointer
    # Try to use Firebase if credentials are available
    if initialize_firebase():
        try:
            bucket = storage.bucket()
            # Create a unique path for the image
            path = f"images/{datetime.now().strftime('%Y%m%d')}/{filename}"
            blob = bucket.blob(path)
            
            # Upload the image
            image_data.seek(0)
            blob.upload_from_file(image_data, content_type='image/jpeg')
            
            # Make the image publicly accessible
            blob.make_public()
            
            logger.debug(f"Image uploaded to Firebase: {path}")
            url = blob.public_url
            return path, url
            
        except Exception as e:
            logger.error(f"Firebase upload failed: {str(e)}")
            # Fall back to local storage
            path = upload_to_local(image_data, filename)
            url = get_image_url(path)
            return path, url
    
    # If Firebase isn't available, use an alternative method
    else:
        logger.debug("Firebase not initialized, using local storage")
        path = upload_to_local(image_data, filename)
        url = get_image_url(path)
        return path, url

def upload_to_local(image_data, filename):
    """
    Upload an image to local storage.
    
    Args:
        image_data: BytesIO object containing the image
        filename: Name to save the file as
        
    Returns:
        str: The path to the stored image
    """
    # Create directory if it doesn't exist
    os.makedirs('/tmp/uploads', exist_ok=True)
    
    # Generate a path for the file
    path = f"/tmp/uploads/{filename}"
    
    # Save the file
    image_data.seek(0)
    with open(path, 'wb') as f:
        f.write(image_data.read())
    
    logger.debug(f"Image saved locally at {path}")
    return path

def get_image_url(path):
    """
    Get the URL for an image.
    
    Args:
        path: The path where the image is stored
        
    Returns:
        str: URL to access the image
    """
    # If it's a Firebase path and Firebase is initialized
    if firebase_initialized and path.startswith('images/'):
        try:
            bucket = storage.bucket()
            blob = bucket.blob(path)
            return blob.public_url
        except Exception as e:
            logger.error(f"Error getting Firebase URL: {str(e)}")
            # Fall back to local URL
            return f"/serve_image/{path.split('/')[-1]}"
    
    # If it's a local path
    elif path.startswith('/tmp/uploads/'):
        return f"/serve_image/{path.split('/')[-1]}"
    
    # Default case
    else:
        return f"/serve_image/{path.split('/')[-1]}"
