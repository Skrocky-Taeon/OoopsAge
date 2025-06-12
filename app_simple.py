import os
import logging
import uuid
import json
from datetime import datetime
import imagehash
from PIL import Image
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, g, make_response, abort
from werkzeug.utils import secure_filename
from sqlalchemy import func
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from config import Config
from models import db, SkinAnalysis
from services.ai_service import analyze_skin_age
from services.storage_service import upload_image, get_image_url
from utils.common import allowed_file, generate_feedback, generate_image_hash
from utils.pdf_generator import create_skin_analysis_pdf
from utils.product_recommendations import get_product_recommendations
# Dashboard import will be added after app initialization

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = os.environ.get("SESSION_SECRET", "myskinageappsecret")

# Configure session for better HTTPS compatibility and stability
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=86400,  # 24 hours
    SEND_FILE_MAX_AGE_DEFAULT=300      # 5 minutes cache
)

# Initialize database
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "pool_timeout": 30,
    "max_overflow": 15
}
db.init_app(app)

# Create all tables
with app.app_context():
    try:
        db.create_all()
        logger.debug("Database tables created")
        print("🇺🇸 영어 버전 (Ooops Age) 실행 중...")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

# Health check endpoint
@app.route('/health')
def health_check():
    try:
        # Simple health check without database query to reduce load
        return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}, 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {'status': 'unhealthy', 'error': str(e)}, 500

# PWA Service Worker route
@app.route('/service-worker.js')
def service_worker():
    return app.send_static_file('service-worker.js')

# Digital Asset Links for TWA
@app.route('/.well-known/assetlinks.json')
def assetlinks():
    return app.send_static_file('.well-known/assetlinks.json')

# Privacy Policy route (required for Google Play)
@app.route('/privacy-policy')
def privacy_policy():
    from datetime import datetime
    return render_template('privacy_policy.html', current_date=datetime.now().strftime('%B %d, %Y'))

# Set default language
config = Config()

@app.before_request
def before_request():
    # Always use English for simplified app
    g.lang = 'en'
    
    # Generate session ID for tracking
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        logger.debug(f"Created new session ID: {session['session_id']}")
    
    # Handle multiple domains for backward compatibility
    host = request.host
    if 'spock.replit.dev' in host or 'spock.prod.repl.run' in host:
        # Valid domains, proceed normally
        pass

# Add template context processors
@app.context_processor
def utility_processor():
    """Add utility functions to template context."""
    return {
        'lang': 'en',
        'app_name': config.APP_NAME,
        'app_description': config.APP_DESCRIPTION
    }

def nl2br_filter(s):
    """Convert newlines to HTML line breaks."""
    if s is None:
        return ''
    return s.replace('\n', '<br>')

app.jinja_env.filters['nl2br'] = nl2br_filter

@app.route('/')
def index():
    """Render the home page with image upload form."""
    # Generate a session ID if none exists
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        logger.debug(f"Created new session ID: {session['user_id']}")
    
    return render_template('index_simple.html')

@app.route('/serve_image/<filename>')
def serve_image(filename):
    """Serve the uploaded images."""
    try:
        return send_file(f"/tmp/uploads/{filename}")
    except FileNotFoundError:
        abort(404)

@app.route('/upload', methods=['POST'])
def upload():
    """Handle image upload and analysis. Available for all users."""
    if 'file' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('index'))
    
    file = request.files['file']
    actual_age = request.form.get('actual_age', type=int)
    
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        try:
            # Read and validate image
            image_data = file.read()
            file.seek(0)  # Reset file pointer
            
            # Validate file size
            if len(image_data) < Config.MIN_FILE_SIZE:
                flash(f'File too small. Minimum size is {Config.MIN_FILE_SIZE // 1024}KB', 'danger')
                return redirect(url_for('index'))
            
            # Validate image format and dimensions
            try:
                img = Image.open(BytesIO(image_data))
                width, height = img.size
                
                if width < Config.MIN_IMAGE_WIDTH or height < Config.MIN_IMAGE_HEIGHT:
                    flash(f'Image too small. Minimum dimensions: {Config.MIN_IMAGE_WIDTH}x{Config.MIN_IMAGE_HEIGHT}px', 'danger')
                    return redirect(url_for('index'))
                
                if width > Config.MAX_IMAGE_WIDTH or height > Config.MAX_IMAGE_HEIGHT:
                    flash(f'Image too large. Maximum dimensions: {Config.MAX_IMAGE_WIDTH}x{Config.MAX_IMAGE_HEIGHT}px', 'danger')
                    return redirect(url_for('index'))
                
            except Exception as e:
                logger.error(f"Error validating image: {str(e)}")
                flash('Invalid image file', 'danger')
                return redirect(url_for('index'))
            
            # Generate image hash for duplicate detection
            try:
                # Convert BytesIO to PIL Image for hash generation
                image_for_hash = Image.open(BytesIO(image_data))
                img_hash = str(generate_image_hash(image_for_hash))
                
                # Check for duplicate analysis (within same session for guest users)
                user_id = session.get('user_id')
                existing_analysis = SkinAnalysis.query.filter_by(
                    user_id=user_id,
                    image_hash=img_hash
                ).first()
                
                if existing_analysis:
                    flash('⚠️ Same images provide identical results. For different results, please upload a new photo of the same person.', 'info')
                    return redirect(url_for('results', analysis_id=existing_analysis.id))
                    
            except Exception as e:
                logger.error(f"Error generating image hash: {str(e)}")
                img_hash = "unknown"
            
            # Upload image to storage
            try:
                image_path, image_url = upload_image(file, session.get('user_id'))
                logger.debug(f"Image uploaded: {image_path}")
            except Exception as e:
                logger.error(f"Error uploading image: {str(e)}")
                flash('Error uploading image. Please try again.', 'danger')
                return redirect(url_for('index'))
            
            # Analyze skin age
            try:
                logger.debug("Starting skin age analysis...")
                # Load image from path for analysis
                image_for_analysis = Image.open(image_path)
                result = analyze_skin_age(image_for_analysis, actual_age)
                if len(result) == 2:
                    skin_age, features = result
                else:
                    skin_age, features, _ = result
                logger.debug(f"Analysis complete: skin_age={skin_age}, features={features}")
            except Exception as e:
                logger.error(f"Error analyzing skin age: {str(e)}")
                flash('Error analyzing image. Please try again with a different photo.', 'danger')
                return redirect(url_for('index'))
            
            # Generate feedback
            try:
                feedback = generate_feedback(skin_age, features, 'en')
            except Exception as e:
                logger.error(f"Error generating feedback: {str(e)}")
                feedback = "Analysis completed successfully."
            
            # Save analysis to database
            try:
                analysis = SkinAnalysis()
                analysis.user_id = session.get('user_id')
                analysis.user_account_id = None  # No user accounts in simplified version
                analysis.image_path = image_path
                analysis.image_url = image_url
                analysis.image_hash = img_hash
                analysis.skin_age = skin_age
                analysis.actual_age = actual_age
                analysis.features = features
                analysis.feedback = feedback
                db.session.add(analysis)
                db.session.commit()
                
                flash('Analysis completed successfully!', 'success')
                return redirect(url_for('results', analysis_id=analysis.id))
                
            except Exception as e:
                logger.error(f"Error saving analysis: {str(e)}")
                db.session.rollback()
                flash('Analysis completed but could not be saved.', 'warning')
                # Still show results even if save failed
                return render_template('results.html', 
                                     skin_age=skin_age, 
                                     features=features,
                                     feedback=feedback,
                                     image_url=image_url,
                                     actual_age=actual_age)
        
        except Exception as e:
            logger.error(f"Unexpected error during upload: {str(e)}")
            flash('An unexpected error occurred. Please try again.', 'danger')
            return redirect(url_for('index'))
    else:
        flash('Invalid file type. Please upload a JPG or PNG image.', 'danger')
        return redirect(url_for('index'))

@app.route('/results/<int:analysis_id>')
def results(analysis_id):
    """Display the results of skin analysis."""
    try:
        analysis = SkinAnalysis.query.get_or_404(analysis_id)
        
        # Only show results to the same session user
        if analysis.user_id != session.get('user_id'):
            flash('Analysis not found.', 'danger')
            return redirect(url_for('index'))
        
        # Ensure image_url is properly set for display
        if not analysis.image_url or not analysis.image_url.startswith('http'):
            # Regenerate URL from path if needed
            from services.storage_service import get_image_url
            analysis.image_url = get_image_url(analysis.image_path)
            # Update in database
            try:
                db.session.commit()
            except Exception as e:
                logger.warning(f"Could not update image URL: {str(e)}")
        
        # Generate product recommendations based on analysis
        recommended_products = get_product_recommendations(
            analysis.features, 
            analysis.skin_age, 
            analysis.actual_age
        )
        
        # Add recommendations to analysis object for template
        analysis.recommended_products = recommended_products
        
        return render_template('results_simple.html', analysis=analysis)
    
    except Exception as e:
        logger.error(f"Error loading results: {str(e)}")
        flash('Error loading analysis results.', 'danger')
        return redirect(url_for('index'))

@app.route('/download_pdf/<int:analysis_id>')
def download_pdf(analysis_id):
    """Generate and download a PDF report for a skin analysis."""
    try:
        analysis = SkinAnalysis.query.get_or_404(analysis_id)
        
        # Only allow download for the same session user
        if analysis.user_id != session.get('user_id'):
            flash('Analysis not found.', 'danger')
            return redirect(url_for('index'))
        
        # Generate PDF
        pdf_buffer = create_skin_analysis_pdf(analysis, 'en')
        
        # Create response
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=skin_analysis_{analysis_id}.pdf'
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        flash('Error generating PDF report.', 'danger')
        return redirect(url_for('results', analysis_id=analysis_id))

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    logger.error(f"Server error: {str(e)}")
    return render_template('404.html'), 500

# Dashboard removed - using Google Play Console analytics instead

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)