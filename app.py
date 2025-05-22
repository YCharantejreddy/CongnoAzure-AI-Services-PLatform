# # # # """
# # # # Main Flask Application

# # # # This is the main application file for the Azure AI Mega Toolkit.
# # # # It integrates all components and provides the web interface.
# # # # """

# # # # import os
# # # # import sys
# # # # import logging
# # # # import uuid
# # # # import json
# # # # import io  # Required for BytesIO
# # # # import re  # Required for regular expressions
# # # # from datetime import datetime
# # # # from werkzeug.utils import secure_filename
# # # # from werkzeug.security import generate_password_hash, check_password_hash
# # # # import eventlet
# # # # # Apply eventlet monkey patch at the very beginning
# # # # eventlet.monkey_patch()

# # # # # Flask and extensions
# # # # from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, abort
# # # # from flask_sqlalchemy import SQLAlchemy
# # # # from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

# # # # # Configure logging
# # # # logging.basicConfig(
# # # #     level=logging.INFO,
# # # #     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# # # # )
# # # # logger = logging.getLogger(__name__)

# # # # # Initialize Flask app
# # # # app = Flask(__name__)

# # # # # --- Application Configuration ---
# # # # # Base directory of the application
# # # # base_dir = os.path.abspath(os.path.dirname(__file__))

# # # # # Load configuration from environment variables
# # # # from dotenv import load_dotenv
# # # # dotenv_path = os.path.join(base_dir, '.env')  # Use base_dir for .env path

# # # # if os.path.exists(dotenv_path):
# # # #     logger.info(f"Attempting to load .env file from: {dotenv_path}")
# # # #     load_dotenv(dotenv_path=dotenv_path)
# # # #     logger.info(".env file loaded successfully.")
# # # # else:
# # # #     logger.warning(f".env file not found at: {dotenv_path}. Using default configurations or expecting environment variables to be set externally.")

# # # # # Secret Key
# # # # app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'a-very-strong-default-secret-key-for-dev-only')
# # # # if app.config['SECRET_KEY'] == 'a-very-strong-default-secret-key-for-dev-only':
# # # #     logger.warning("Using default FLASK_SECRET_KEY. This is insecure for production. Please set it in your .env file or environment.")

# # # # # Instance Folder (for database, etc.)
# # # # instance_folder_path = os.path.join(base_dir, 'instance')
# # # # os.makedirs(instance_folder_path, exist_ok=True)
# # # # logger.info(f"Ensured instance folder exists at: {instance_folder_path}")
# # # # try:
# # # #     os.chmod(instance_folder_path, 0o777)  # For development ease; review for production
# # # #     logger.info(f"Attempted to set permissions on instance directory: {instance_folder_path}")
# # # # except Exception as e:
# # # #     logger.warning(f"Could not set permissions on instance directory: {str(e)} (This is often fine on Windows)")

# # # # # Database Configuration
# # # # database_url_from_env = os.environ.get('DATABASE_URL', 'sqlite:///instance/default_toolkit.db')  # Default if not in .env
# # # # logger.info(f"DATABASE_URL from environment (or default): {database_url_from_env}")

# # # # if database_url_from_env.startswith('sqlite:///'):
# # # #     # Handle relative paths for SQLite to be relative to the instance folder
# # # #     db_file_part = database_url_from_env[len('sqlite:///'):]  # e.g., "instance/toolkit.db" or "toolkit.db"
    
# # # #     if db_file_part.startswith('instance/'):
# # # #         # Path is like "instance/toolkit.db", make it relative to base_dir/instance
# # # #         db_filename_in_instance = db_file_part[len('instance/'):]
# # # #         absolute_db_path = os.path.join(instance_folder_path, db_filename_in_instance)
# # # #     elif os.path.isabs(db_file_part):
# # # #         # It's already an absolute path like "sqlite:///C:/path/to/db.sqlite"
# # # #         absolute_db_path = db_file_part
# # # #     else:
# # # #         # Path is like "toolkit.db", assume it's meant for the instance folder
# # # #         absolute_db_path = os.path.join(instance_folder_path, db_file_part)
        
# # # #     app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{absolute_db_path}'
# # # # else:
# # # #     # For other database types (e.g., PostgreSQL), use the URL as is
# # # #     app.config['SQLALCHEMY_DATABASE_URI'] = database_url_from_env

# # # # logger.info(f"Final SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
# # # # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# # # # # Upload Folder
# # # # upload_folder_name = os.environ.get('UPLOAD_FOLDER_NAME', 'uploads')
# # # # upload_folder_path = os.path.join(base_dir, upload_folder_name)
# # # # app.config['UPLOAD_FOLDER'] = upload_folder_path

# # # # # Parse MAX_CONTENT_LENGTH, stripping any comments
# # # # max_content_length_str = os.environ.get('MAX_CONTENT_LENGTH', '16777216')  # 16MB default
# # # # if '#' in max_content_length_str:
# # # #     max_content_length_str = max_content_length_str.split('#')[0].strip()
# # # # app.config['MAX_CONTENT_LENGTH'] = int(max_content_length_str)

# # # # os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# # # # logger.info(f"Ensured uploads folder exists at: {app.config['UPLOAD_FOLDER']}")
# # # # try:
# # # #     os.chmod(app.config['UPLOAD_FOLDER'], 0o777)  # For development ease; review for production
# # # #     logger.info(f"Attempted to set permissions on uploads directory: {app.config['UPLOAD_FOLDER']}")
# # # # except Exception as e:
# # # #     logger.warning(f"Could not set permissions on uploads directory: {str(e)} (This is often fine on Windows)")

# # # # # Log Azure Keys (first 5 chars for verification, rest masked)
# # # # logger.info(f"TRANSLATOR_SUBSCRIPTION_KEY: {os.environ.get('TRANSLATOR_SUBSCRIPTION_KEY', 'Not set')[:5]}...")
# # # # logger.info(f"LANGUAGE_SUBSCRIPTION_KEY: {os.environ.get('LANGUAGE_SUBSCRIPTION_KEY', 'Not set')[:5]}...")
# # # # logger.info(f"SPEECH_SUBSCRIPTION_KEY: {os.environ.get('SPEECH_SUBSCRIPTION_KEY', 'Not set')[:5]}...")
# # # # logger.info(f"VISION_SUBSCRIPTION_KEY: {os.environ.get('VISION_SUBSCRIPTION_KEY', 'Not set')[:5]}...")
# # # # # --- End of Application Configuration ---

# # # # # Initialize SQLAlchemy
# # # # db = SQLAlchemy(app)

# # # # # Initialize Flask-Login
# # # # login_manager = LoginManager(app)
# # # # login_manager.login_view = 'login'
# # # # login_manager.login_message_category = 'info'  # For better flash message styling

# # # # # Initialize Azure services
# # # # from azure_services import azure_services

# # # # # Initialize Document QA
# # # # import document_qa
# # # # # Pass the absolute path to the uploads folder for document_qa initialization
# # # # document_qa_upload_dir = app.config['UPLOAD_FOLDER']
# # # # document_qa.init_document_qa(document_qa_upload_dir)

# # # # # Initialize NLTK
# # # # try:
# # # #     import nltk
# # # #     nltk.data.find('tokenizers/punkt')
# # # # except LookupError:
# # # #     logger.info("NLTK 'punkt' resource not found. Downloading...")
# # # #     nltk.download('punkt')
# # # #     logger.info("'punkt' resource downloaded.")

# # # # # Database Models
# # # # class User(UserMixin, db.Model):
# # # #     __tablename__ = 'user'
# # # #     id = db.Column(db.Integer, primary_key=True)
# # # #     username = db.Column(db.String(64), unique=True, nullable=False)
# # # #     password_hash = db.Column(db.String(128), nullable=False)
# # # #     summaries = db.relationship('Summary', backref='user', lazy='dynamic')
    
# # # #     def set_password(self, password):
# # # #         self.password_hash = generate_password_hash(password)
        
# # # #     def check_password(self, password):
# # # #         return check_password_hash(self.password_hash, password)

# # # # class Summary(db.Model):
# # # #     __tablename__ = 'summary'
# # # #     id = db.Column(db.Integer, primary_key=True)
# # # #     input_type = db.Column(db.String(20), nullable=False)
# # # #     action_type = db.Column(db.String(30), nullable=False)
# # # #     original_content_preview = db.Column(db.Text, nullable=True)
# # # #     processed_content = db.Column(db.JSON, nullable=True)
# # # #     details_json = db.Column(db.JSON, nullable=True)
# # # #     timestamp = db.Column(db.DateTime, default=datetime.utcnow)
# # # #     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
# # # #     def __repr__(self):
# # # #         return f'<Summary {self.id}>'
        
# # # #     def to_dict(self):  # For JSON serialization, especially in my_summaries.html script
# # # #         return {
# # # #             'id': self.id,
# # # #             'input_type': self.input_type,
# # # #             'action_type': self.action_type,
# # # #             'original_content_preview': self.original_content_preview,
# # # #             'processed_content': self.processed_content,
# # # #             'details_json': self.details_json,
# # # #             'timestamp': self.timestamp.isoformat() if self.timestamp else None,
# # # #             'user_id': self.user_id
# # # #         }

# # # # # Create database tables
# # # # try:
# # # #     with app.app_context():
# # # #         db.create_all()
# # # #         logger.info("Database tables created successfully (or already exist).")
        
# # # #         # Create a test user for validation if it doesn't exist
# # # #         if not User.query.filter_by(username="testuser").first():
# # # #             test_user = User(username="testuser")
# # # #             test_user.set_password("password")  # Ensure this matches how you test login
# # # #             db.session.add(test_user)
# # # #             db.session.commit()
# # # #             logger.info("Test user 'testuser' created for validation.")
# # # #         else:
# # # #             logger.info("Test user 'testuser' already exists.")
# # # # except Exception as e:
# # # #     logger.error(f"Error during database initialization or test user creation: {str(e)}")
# # # #     logger.error("The application might not function correctly with database-dependent features.")

# # # # @login_manager.user_loader
# # # # def load_user(user_id):
# # # #     return User.query.get(int(user_id))

# # # # @app.context_processor
# # # # def inject_current_year():
# # # #     return {'current_year': datetime.now().year}

# # # # # Utility Functions
# # # # def extract_pdf_text_pypdf2(pdf_file_storage_or_bytesio):
# # # #     """Extract text from PDF file using PyPDF2. Accepts FileStorage or BytesIO."""
# # # #     import PyPDF2
    
# # # #     pdf_stream = None
# # # #     if hasattr(pdf_file_storage_or_bytesio, 'read'):  # Check if it's a stream-like object
# # # #         if hasattr(pdf_file_storage_or_bytesio, 'seek'):
# # # #              pdf_file_storage_or_bytesio.seek(0)  # Reset stream if possible (like for FileStorage)
# # # #         pdf_stream = io.BytesIO(pdf_file_storage_or_bytesio.read())
# # # #         if hasattr(pdf_file_storage_or_bytesio, 'seek'):  # Reset original stream again if it was a FileStorage
# # # #             pdf_file_storage_or_bytesio.seek(0)
# # # #     else:
# # # #         logger.error("extract_pdf_text_pypdf2 received an object it cannot read.")
# # # #         raise ValueError("Invalid input type for PDF extraction. Expected FileStorage or BytesIO.")

# # # #     try:
# # # #         pdf_reader = PyPDF2.PdfReader(pdf_stream)
# # # #         text = ""
# # # #         for page_num in range(len(pdf_reader.pages)):
# # # #             page = pdf_reader.pages[page_num]
# # # #             extracted_page_text = page.extract_text()
# # # #             if extracted_page_text:  # Ensure text was actually extracted
# # # #                  text += extracted_page_text + "\n\n"
# # # #         if not text:
# # # #             logger.warning("PyPDF2 extracted no text from the PDF. It might be an image-based PDF or encrypted.")
# # # #         return text
# # # #     except Exception as e:
# # # #         logger.error(f"Error extracting PDF text with PyPDF2: {str(e)}")
# # # #         raise

# # # # def get_youtube_transcript(video_url: str):
# # # #     """Get transcript from YouTube video URL."""
# # # #     # Assuming background_tasks.py is in the same directory or Python path
# # # #     from background_tasks import youtube_transcript 
    
# # # #     try:
# # # #         # For development, Celery might run tasks eagerly if not configured with a broker.
# # # #         # If using a proper Celery setup, you might use .delay() and handle AsyncResult.
# # # #         # .apply().get() will block until the task completes (or run it synchronously if eager).
# # # #         result = youtube_transcript.apply(args=[video_url]).get()
# # # #         return result
# # # #     except Exception as e:
# # # #         logger.error(f"Error getting YouTube transcript for URL {video_url}: {str(e)}")
# # # #         return {"error": f"Could not retrieve transcript: {str(e)}", "status": "error"}

# # # # # Routes - Page Rendering
# # # # @app.route('/')
# # # # def index():
# # # #     return render_template('index.html')

# # # # @app.route('/about')
# # # # def about():
# # # #     return render_template('about.html')

# # # # @app.route('/image-analyzer-page')
# # # # @login_required
# # # # def image_analyzer_page():
# # # #     return render_template('image_analyzer.html')

# # # # @app.route('/live-chat-page')
# # # # @login_required
# # # # def live_chat_page():
# # # #     return render_template('live_chat.html')

# # # # @app.route('/doc-qa-page')
# # # # @login_required
# # # # def doc_qa_page():
# # # #     return render_template('doc_qa.html')

# # # # @app.route('/my-summaries')
# # # # @login_required
# # # # def my_summaries():
# # # #     page = request.args.get('page', 1, type=int)
# # # #     per_page = 10  # Or from config
    
# # # #     summaries_pagination = Summary.query.filter_by(user_id=current_user.id)\
# # # #         .order_by(Summary.timestamp.desc())\
# # # #         .paginate(page=page, per_page=per_page, error_out=False)
        
# # # #     return render_template('my_summaries.html', summaries=summaries_pagination)

# # # # # Authentication Routes
# # # # @app.route('/login', methods=['GET', 'POST'])
# # # # def login():
# # # #     if current_user.is_authenticated:
# # # #         return redirect(url_for('index'))
        
# # # #     if request.method == 'POST':
# # # #         username = request.form.get('username')
# # # #         password = request.form.get('password')
        
# # # #         user = User.query.filter_by(username=username).first()
        
# # # #         if user is None or not user.check_password(password):
# # # #             flash('Invalid username or password.', 'danger')
# # # #             return redirect(url_for('login'))
            
# # # #         login_user(user, remember=request.form.get('remember') == 'on')  # Handle remember me
        
# # # #         next_page = request.args.get('next')
# # # #         # Basic protection against open redirect vulnerability
# # # #         if not next_page or not next_page.startswith('/'):
# # # #             next_page = url_for('index')
        
# # # #         flash('Logged in successfully!', 'success')
# # # #         return redirect(next_page)
        
# # # #     return render_template('login.html')

# # # # @app.route('/register', methods=['GET', 'POST'])
# # # # def register():
# # # #     if current_user.is_authenticated:
# # # #         return redirect(url_for('index'))
        
# # # #     if request.method == 'POST':
# # # #         username = request.form.get('username')
# # # #         password = request.form.get('password')
        
# # # #         if not username or not password:  # Basic validation
# # # #             flash('Username and password are required.', 'warning')
# # # #             return redirect(url_for('register'))

# # # #         if User.query.filter_by(username=username).first():
# # # #             flash('Username already exists. Please choose a different one.', 'warning')
# # # #             return redirect(url_for('register'))
            
# # # #         user = User(username=username)
# # # #         user.set_password(password)
        
# # # #         try:
# # # #             db.session.add(user)
# # # #             db.session.commit()
# # # #             flash('Registration successful! Please log in.', 'success')
# # # #             return redirect(url_for('login'))
# # # #         except Exception as e:
# # # #             db.session.rollback()
# # # #             logger.error(f"Error during registration for user {username}: {str(e)}")
# # # #             flash('An error occurred during registration. Please try again.', 'danger')
# # # #             return redirect(url_for('register'))
            
# # # #     return render_template('register.html')

# # # # @app.route('/logout')
# # # # @login_required
# # # # def logout():
# # # #     logout_user()
# # # #     flash('You have been logged out.', 'info')
# # # #     return redirect(url_for('index'))

# # # # # API Routes - Azure Services
# # # # @app.route('/api/translate', methods=['POST'])
# # # # @login_required
# # # # def translate_text():
# # # #     data = request.get_json()
# # # #     if not data or 'text' not in data or 'target_languages' not in data:
# # # #         return jsonify({'error': 'Invalid request. Required fields: text, target_languages'}), 400
        
# # # #     text = data['text']
# # # #     target_languages = data['target_languages']
# # # #     source_language = data.get('source_language')  # Optional
    
# # # #     if not text or not target_languages:
# # # #         return jsonify({'error': 'Text and target languages cannot be empty'}), 400
        
# # # #     result = azure_services.translate_text(text, target_languages, source_language)
    
# # # #     if 'error' in result:
# # # #         return jsonify(result), 400
        
# # # #     return jsonify(result)

# # # # @app.route('/api/analyze-sentiment', methods=['POST'])
# # # # @login_required
# # # # def analyze_sentiment():
# # # #     data = request.get_json()
# # # #     if not data or 'text' not in data:
# # # #         return jsonify({'error': 'Invalid request. Required field: text'}), 400
        
# # # #     text = data['text']
    
# # # #     if not text:
# # # #         return jsonify({'error': 'Text cannot be empty'}), 400
        
# # # #     result = azure_services.analyze_sentiment(text)
    
# # # #     if 'error' in result:
# # # #         return jsonify(result), 400
        
# # # #     return jsonify(result)

# # # # @app.route('/api/summarize', methods=['POST'])
# # # # @login_required
# # # # def summarize_text():
# # # #     data = request.get_json()
# # # #     if not data or 'text' not in data:
# # # #         return jsonify({'error': 'Invalid request. Required field: text'}), 400
        
# # # #     text = data['text']
# # # #     summary_type = data.get('type', 'extractive')  # Default to extractive
# # # #     sentence_count = data.get('sentence_count', 3)  # Default to 3 sentences
    
# # # #     if not text:
# # # #         return jsonify({'error': 'Text cannot be empty'}), 400
        
# # # #     if summary_type == 'extractive':
# # # #         result = azure_services.extractive_summarize(text, sentence_count)
# # # #     elif summary_type == 'abstractive':
# # # #         result = azure_services.abstractive_summarize(text, sentence_count)
# # # #     else:
# # # #         return jsonify({'error': 'Invalid summary type. Use "extractive" or "abstractive"'}), 400
        
# # # #     if 'error' in result:
# # # #         return jsonify(result), 400
        
# # # #     # Save summary to database
# # # #     try:
# # # #         summary = Summary(
# # # #             input_type='text',
# # # #             action_type=f'{summary_type}_summary',
# # # #             original_content_preview=text[:500] + ('...' if len(text) > 500 else ''),
# # # #             processed_content=result,
# # # #             user_id=current_user.id
# # # #         )
# # # #         db.session.add(summary)
# # # #         db.session.commit()
# # # #         result['summary_id'] = summary.id
# # # #     except Exception as e:
# # # #         logger.error(f"Error saving summary to database: {str(e)}")
# # # #         # Continue even if saving fails
        
# # # #     return jsonify(result)

# # # # @app.route('/api/analyze-image', methods=['POST'])
# # # # @login_required
# # # # def analyze_image():
# # # #     if 'image' not in request.files:
# # # #         return jsonify({'error': 'No image file provided'}), 400
        
# # # #     image_file = request.files['image']
    
# # # #     if image_file.filename == '':
# # # #         return jsonify({'error': 'Empty image file name'}), 400
        
# # # #     if not image_file or not allowed_file(image_file.filename, {'png', 'jpg', 'jpeg', 'gif', 'bmp'}):
# # # #         return jsonify({'error': 'Invalid image file format'}), 400
        
# # # #     # Save the image temporarily
# # # #     filename = secure_filename(image_file.filename)
# # # #     temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
# # # #     image_file.save(temp_path)
    
# # # #     # Analyze the image
# # # #     result = azure_services.analyze_image(temp_path)
    
# # # #     if 'error' in result:
# # # #         return jsonify(result), 400
        
# # # #     # Save analysis to database
# # # #     try:
# # # #         summary = Summary(
# # # #             input_type='image',
# # # #             action_type='vision_analysis',
# # # #             original_content_preview=filename,
# # # #             processed_content=result,
# # # #             user_id=current_user.id
# # # #         )
# # # #         db.session.add(summary)
# # # #         db.session.commit()
# # # #         result['summary_id'] = summary.id
# # # #     except Exception as e:
# # # #         logger.error(f"Error saving image analysis to database: {str(e)}")
# # # #         # Continue even if saving fails
        
# # # #     return jsonify(result)

# # # # @app.route('/api/youtube-transcript', methods=['POST'])
# # # # @login_required
# # # # def youtube_transcript_api():
# # # #     data = request.get_json()
# # # #     if not data or 'url' not in data:
# # # #         return jsonify({'error': 'Invalid request. Required field: url'}), 400
        
# # # #     video_url = data['url']
    
# # # #     if not video_url:
# # # #         return jsonify({'error': 'YouTube URL cannot be empty'}), 400
        
# # # #     result = get_youtube_transcript(video_url)
    
# # # #     if result.get('status') == 'error':
# # # #         return jsonify(result), 400
        
# # # #     # Save transcript to database
# # # #     try:
# # # #         summary = Summary(
# # # #             input_type='youtube',
# # # #             action_type='transcript',
# # # #             original_content_preview=video_url,
# # # #             processed_content={'text': result.get('text', ''), 'language': result.get('language', 'unknown')},
# # # #             user_id=current_user.id
# # # #         )
# # # #         db.session.add(summary)
# # # #         db.session.commit()
# # # #         result['summary_id'] = summary.id
# # # #     except Exception as e:
# # # #         logger.error(f"Error saving YouTube transcript to database: {str(e)}")
# # # #         # Continue even if saving fails
        
# # # #     return jsonify(result)

# # # # @app.route('/api/document-qa', methods=['POST'])
# # # # @login_required
# # # # def document_qa_api():
# # # #     if 'document' not in request.files:
# # # #         return jsonify({'error': 'No document file provided'}), 400
        
# # # #     document_file = request.files['document']
# # # #     question = request.form.get('question', '')
    
# # # #     if document_file.filename == '':
# # # #         return jsonify({'error': 'Empty document file name'}), 400
        
# # # #     if not document_file or not allowed_file(document_file.filename, {'pdf', 'txt', 'docx'}):
# # # #         return jsonify({'error': 'Invalid document file format'}), 400
        
# # # #     if not question:
# # # #         return jsonify({'error': 'Question cannot be empty'}), 400
        
# # # #     # Save the document
# # # #     filename = secure_filename(document_file.filename)
# # # #     file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
# # # #     document_file.save(file_path)
    
# # # #     # Get file size
# # # #     file_size = os.path.getsize(file_path)
    
# # # #     # Add document to QA system
# # # #     doc_id = document_qa.add_document(
# # # #         file_path=file_path,
# # # #         user_id=current_user.id,
# # # #         file_size=file_size
# # # #     )
    
# # # #     if not doc_id:
# # # #         return jsonify({'error': 'Failed to process document'}), 500
        
# # # #     # Query the document
# # # #     answer = document_qa.query_document(doc_id, question)
    
# # # #     if not answer or 'error' in answer:
# # # #         return jsonify(answer or {'error': 'Failed to get answer'}), 400
        
# # # #     # Save QA to database
# # # #     try:
# # # #         summary = Summary(
# # # #             input_type='document',
# # # #             action_type='qa',
# # # #             original_content_preview=filename,
# # # #             processed_content={'question': question, 'answer': answer},
# # # #             user_id=current_user.id
# # # #         )
# # # #         db.session.add(summary)
# # # #         db.session.commit()
# # # #         answer['summary_id'] = summary.id
# # # #     except Exception as e:
# # # #         logger.error(f"Error saving document QA to database: {str(e)}")
# # # #         # Continue even if saving fails
        
# # # #     return jsonify(answer)

# # # # @app.route('/api/get-user-documents', methods=['GET'])
# # # # @login_required
# # # # def get_user_documents():
# # # #     documents = document_qa.get_user_documents(current_user.id)
# # # #     return jsonify(documents)

# # # # @app.route('/api/transcribe-audio', methods=['POST'])
# # # # @login_required
# # # # def transcribe_audio_api():
# # # #     if 'audio' not in request.files:
# # # #         return jsonify({'error': 'No audio file provided'}), 400
        
# # # #     audio_file = request.files['audio']
# # # #     language = request.form.get('language')  # Optional
    
# # # #     if audio_file.filename == '':
# # # #         return jsonify({'error': 'Empty audio file name'}), 400
        
# # # #     if not audio_file or not allowed_file(audio_file.filename, {'wav', 'mp3', 'ogg', 'flac'}):
# # # #         return jsonify({'error': 'Invalid audio file format'}), 400
        
# # # #     # Save the audio file
# # # #     filename = secure_filename(audio_file.filename)
# # # #     file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
# # # #     audio_file.save(file_path)
    
# # # #     # Import the transcribe_audio task
# # # #     try:
# # # #         from background_tasks import transcribe_audio
        
# # # #         # Call the task
# # # #         result = transcribe_audio.apply(args=[file_path, language]).get()
        
# # # #         if 'error' in result:
# # # #             return jsonify(result), 400
            
# # # #         # Save transcription to database
# # # #         try:
# # # #             summary = Summary(
# # # #                 input_type='audio',
# # # #                 action_type='transcription',
# # # #                 original_content_preview=filename,
# # # #                 processed_content={'text': result.get('text', '')},
# # # #                 user_id=current_user.id
# # # #             )
# # # #             db.session.add(summary)
# # # #             db.session.commit()
# # # #             result['summary_id'] = summary.id
# # # #         except Exception as e:
# # # #             logger.error(f"Error saving audio transcription to database: {str(e)}")
# # # #             # Continue even if saving fails
            
# # # #         return jsonify(result)
# # # #     except ImportError as e:
# # # #         logger.error(f"Error importing transcribe_audio task: {str(e)}")
# # # #         return jsonify({'error': 'Audio transcription service is not available'}), 500
# # # #     except Exception as e:
# # # #         logger.error(f"Error transcribing audio: {str(e)}")
# # # #         return jsonify({'error': f'Failed to transcribe audio: {str(e)}'}), 500

# # # # # Helper Functions
# # # # def allowed_file(filename, allowed_extensions):
# # # #     return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# # # # # Error Handlers
# # # # @app.errorhandler(404)
# # # # def page_not_found(e):
# # # #     return render_template('404.html'), 404

# # # # @app.errorhandler(500)
# # # # def internal_server_error(e):
# # # #     return render_template('500.html'), 500

# # # # # Main entry point
# # # # if __name__ == '__main__':
# # # #     app.run(debug=True, host='0.0.0.0')




# # # """
# # # Main Flask Application

# # # This is the main application file for the Azure AI Mega Toolkit.
# # # It integrates all components and provides the web interface.
# # # """

# # # import os
# # # import sys
# # # import logging
# # # import uuid
# # # import json
# # # import io 
# # # from datetime import datetime, timezone 
# # # from werkzeug.utils import secure_filename
# # # from werkzeug.security import generate_password_hash, check_password_hash
# # # import eventlet
# # # eventlet.monkey_patch()

# # # # Typing imports
# # # from typing import Optional, Dict, List, Any # <<<<<<<<<<<< CORRECTED: Added Optional and others

# # # from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, abort
# # # from flask_sqlalchemy import SQLAlchemy
# # # from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
# # # from flask_socketio import SocketIO, emit, join_room, leave_room

# # # # Configure logging
# # # logging.basicConfig(
# # #     level=logging.INFO,
# # #     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# # # )
# # # logger = logging.getLogger(__name__)

# # # app = Flask(__name__)

# # # # --- Application Configuration ---
# # # base_dir = os.path.abspath(os.path.dirname(__file__))
# # # from dotenv import load_dotenv
# # # dotenv_path = os.path.join(base_dir, '.env')
# # # if os.path.exists(dotenv_path):
# # #     logger.info(f"Attempting to load .env file from: {dotenv_path}")
# # #     load_dotenv(dotenv_path=dotenv_path)
# # #     logger.info(".env file loaded successfully.")
# # # else:
# # #     logger.warning(f".env file not found at: {dotenv_path}. Using defaults or externally set env vars.")

# # # app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-prod')
# # # if app.config['SECRET_KEY'] == 'dev-secret-key-change-in-prod' and not app.debug:
# # #     logger.warning("CRITICAL: Using default FLASK_SECRET_KEY in a non-debug environment. THIS IS HIGHLY INSECURE.")

# # # instance_folder_path = os.path.join(base_dir, 'instance')
# # # os.makedirs(instance_folder_path, exist_ok=True)
# # # logger.info(f"Ensured instance folder exists at: {instance_folder_path}")

# # # # Corrected Database Path Handling
# # # default_db_filename = "toolkit.db"
# # # db_path_from_env = os.environ.get('DATABASE_URL', f'sqlite:///{default_db_filename}')
# # # logger.info(f"DATABASE_URL from environment (or default): {db_path_from_env}")

# # # if db_path_from_env.startswith('sqlite:///'):
# # #     db_file_part = db_path_from_env[len('sqlite:///'):]
# # #     if os.path.isabs(db_file_part): # Absolute path like /path/to/db or C:\path\to\db
# # #         absolute_db_path = db_file_part
# # #     elif db_file_part.startswith('instance/'): # Relative to base_dir, like 'instance/toolkit.db'
# # #         absolute_db_path = os.path.join(base_dir, db_file_part)
# # #     else: # Filename only, assume it's in the instance folder
# # #         absolute_db_path = os.path.join(instance_folder_path, db_file_part)
    
# # #     # Ensure directory for the SQLite file exists if it's not in the main instance_folder_path directly
# # #     db_dir = os.path.dirname(absolute_db_path)
# # #     if not os.path.exists(db_dir):
# # #         os.makedirs(db_dir, exist_ok=True)
# # #         logger.info(f"Created directory for SQLite DB: {db_dir}")

# # #     app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{absolute_db_path.replace(os.sep, "/")}'
# # # else:
# # #     app.config['SQLALCHEMY_DATABASE_URI'] = db_path_from_env
# # # logger.info(f"Final SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
# # # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# # # upload_folder_name = os.environ.get('UPLOAD_FOLDER_NAME', 'uploads')
# # # upload_folder_path = os.path.join(base_dir, upload_folder_name)
# # # app.config['UPLOAD_FOLDER'] = upload_folder_path
# # # max_content_length_str = os.environ.get('MAX_CONTENT_LENGTH', '16777216') # 16MB default
# # # if '#' in max_content_length_str: max_content_length_str = max_content_length_str.split('#')[0].strip()
# # # app.config['MAX_CONTENT_LENGTH'] = int(max_content_length_str)
# # # os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# # # logger.info(f"Ensured uploads folder exists at: {app.config['UPLOAD_FOLDER']}")

# # # logger.info(f"TRANSLATOR_SUBSCRIPTION_KEY: {os.environ.get('TRANSLATOR_SUBSCRIPTION_KEY', 'Not set')[:5]}...")
# # # logger.info(f"LANGUAGE_SUBSCRIPTION_KEY: {os.environ.get('LANGUAGE_SUBSCRIPTION_KEY', 'Not set')[:5]}...")
# # # logger.info(f"SPEECH_SUBSCRIPTION_KEY: {os.environ.get('SPEECH_SUBSCRIPTION_KEY', 'Not set')[:5]}...")
# # # logger.info(f"VISION_SUBSCRIPTION_KEY: {os.environ.get('VISION_SUBSCRIPTION_KEY', 'Not set')[:5]}...")

# # # db = SQLAlchemy(app)
# # # login_manager = LoginManager(app)
# # # login_manager.login_view = 'login'
# # # login_manager.login_message_category = 'info'

# # # from azure_services import azure_services, VisualFeatureTypes 
# # # import document_qa
# # # document_qa.init_document_qa(app.config['UPLOAD_FOLDER'])

# # # try:
# # #     import nltk
# # #     nltk.data.find('tokenizers/punkt')
# # #     nltk.data.find('corpora/stopwords')
# # # except LookupError as e:
# # #     resource_name = str(e).split("'")[1] if "'" in str(e) else "unknown NLTK resource"
# # #     logger.warning(f"NLTK resource '{resource_name}' missing. Attempting download...")
# # #     try: nltk.download(resource_name, quiet=True); logger.info(f"NLTK resource '{resource_name}' downloaded.")
# # #     except Exception as de: logger.error(f"Failed to download NLTK resource '{resource_name}': {de}")


# # # class User(UserMixin, db.Model):
# # #     __tablename__ = 'user'
# # #     id = db.Column(db.Integer, primary_key=True)
# # #     username = db.Column(db.String(80), unique=True, nullable=False)
# # #     password_hash = db.Column(db.String(256), nullable=False)
# # #     summaries = db.relationship('Summary', backref='user', lazy='dynamic', cascade="all, delete-orphan")
# # #     def set_password(self, password): self.password_hash = generate_password_hash(password)
# # #     def check_password(self, password): return check_password_hash(self.password_hash, password)

# # # class Summary(db.Model):
# # #     __tablename__ = 'summary'
# # #     id = db.Column(db.Integer, primary_key=True)
# # #     input_type = db.Column(db.String(50), nullable=False)
# # #     action_type = db.Column(db.String(50), nullable=False)
# # #     original_content_preview = db.Column(db.Text, nullable=True)
# # #     processed_content = db.Column(db.JSON, nullable=True)
# # #     details_json = db.Column(db.JSON, nullable=True)
# # #     timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
# # #     user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
# # #     def __repr__(self): return f'<Summary {self.id} by User {self.user_id}>'
# # #     def to_dict(self):
# # #         return {'id': self.id, 'input_type': self.input_type, 'action_type': self.action_type,
# # #                 'original_content_preview': self.original_content_preview,
# # #                 'processed_content': self.processed_content, 'details_json': self.details_json,
# # #                 'timestamp': self.timestamp.isoformat() if self.timestamp else None, 'user_id': self.user_id}

# # # try:
# # #     with app.app_context():
# # #         db.create_all()
# # #         logger.info("Database tables created successfully (or already exist).")
# # #         if not User.query.filter_by(username="testuser").first():
# # #             test_user = User(username="testuser"); test_user.set_password("password")
# # #             db.session.add(test_user); db.session.commit()
# # #             logger.info("Test user 'testuser' created.")
# # #         else: logger.info("Test user 'testuser' already exists.")
# # # except Exception as e: logger.error(f"Error during database initialization: {str(e)}")

# # # @login_manager.user_loader
# # # def load_user(user_id: str) -> Optional[User]: # Corrected: Added Type Hinting import
# # #     try:
# # #         return db.session.get(User, int(user_id)) 
# # #     except Exception as e: 
# # #         logger.error(f"Error loading user {user_id}: {e}", exc_info=True)
# # #         return None

# # # @app.context_processor
# # # def inject_current_year(): return {'current_year': datetime.now(timezone.utc).year}

# # # # Page Routes
# # # @app.route('/')
# # # def index(): return render_template('index.html')

# # # @app.route('/about')
# # # def about(): return render_template('about.html')

# # # @app.route('/image-analyzer-page')
# # # @login_required
# # # def image_analyzer_page(): return render_template('image_analyzer.html')

# # # @app.route('/live-chat-page')
# # # @login_required
# # # def live_chat_page(): return render_template('live_chat.html')

# # # @app.route('/doc-qa-page')
# # # @login_required
# # # def doc_qa_page(): return render_template('doc_qa.html')

# # # @app.route('/my-summaries')
# # # @login_required
# # # def my_summaries():
# # #     page = request.args.get('page', 1, type=int)
# # #     per_page = 10 
# # #     summaries_pagination_obj = db.session.query(Summary).filter_by(user_id=current_user.id)\
# # #         .order_by(Summary.timestamp.desc())\
# # #         .paginate(page=page, per_page=per_page, error_out=False)
# # #     summaries_list = [s.to_dict() for s in summaries_pagination_obj.items]
# # #     try: summaries_json_str = json.dumps(summaries_list)
# # #     except TypeError as e: logger.error(f"Error serializing summaries: {e}"); summaries_json_str = "[]"
# # #     return render_template('my_summaries.html', summaries=summaries_pagination_obj, summaries_json=summaries_json_str)

# # # # Auth Routes
# # # @app.route('/login', methods=['GET', 'POST'])
# # # def login():
# # #     if current_user.is_authenticated: return redirect(url_for('index'))
# # #     if request.method == 'POST':
# # #         username = request.form.get('username'); password = request.form.get('password')
# # #         user = User.query.filter_by(username=username).first()
# # #         if user and user.check_password(password):
# # #             login_user(user, remember=request.form.get('remember') == 'on')
# # #             next_page = request.args.get('next')
# # #             if not next_page or not next_page.startswith('/'): next_page = url_for('index')
# # #             flash('Logged in successfully!', 'success'); return redirect(next_page)
# # #         else: flash('Invalid username or password. Please try again.', 'danger')
# # #     return render_template('login.html')

# # # @app.route('/register', methods=['GET', 'POST'])
# # # def register():
# # #     if current_user.is_authenticated: return redirect(url_for('index'))
# # #     if request.method == 'POST':
# # #         username = request.form.get('username'); password = request.form.get('password')
# # #         if not username or not password: flash('Username and password are required.', 'warning'); return redirect(url_for('register'))
# # #         if User.query.filter_by(username=username).first(): flash('Username already exists.', 'warning'); return redirect(url_for('register'))
# # #         new_user = User(username=username); new_user.set_password(password)
# # #         try: db.session.add(new_user); db.session.commit(); flash('Registration successful! Please log in.', 'success'); return redirect(url_for('login'))
# # #         except Exception as e: db.session.rollback(); logger.error(f"Reg error {username}: {e}"); flash('Registration error.', 'danger')
# # #     return render_template('register.html')

# # # @app.route('/logout')
# # # @login_required
# # # def logout(): logout_user(); flash('You have been logged out.', 'info'); return redirect(url_for('index'))

# # # # Helper to save processing results
# # # def save_processing_result(input_type, action_type, original_preview, processed_data, request_details=None):
# # #     if current_user.is_authenticated:
# # #         try:
# # #             entry = Summary(user_id=current_user.id, input_type=input_type, action_type=action_type,
# # #                             original_content_preview=original_preview, processed_content=processed_data,
# # #                             details_json=request_details, timestamp=datetime.now(timezone.utc))
# # #             db.session.add(entry); db.session.commit(); return entry.id
# # #         except Exception as e: db.session.rollback(); logger.error(f"DB save error for {current_user.id}: {e}")
# # #     return None

# # # # API Routes
# # # @app.route('/api/translate', methods=['POST'])
# # # @login_required
# # # def translate_text_api(): 
# # #     if not request.is_json: return jsonify({"status": "error", "error": "Request must be JSON"}), 415
# # #     data = request.get_json()
# # #     text = data.get('text'); targets = data.get('target_languages'); source = data.get('source_language')
# # #     if not text or not targets: return jsonify({"status": "error", "error": "Missing 'text' or 'target_languages'"}), 400
# # #     results = azure_services.translate_text(text, targets, source)
# # #     if 'error' in results: return jsonify({"status": "error", "error": results['error']}), 500
# # #     save_processing_result('text', 'translate', text[:500], results, {"target_languages": targets, "source_language": source})
# # #     return jsonify({"status": "success", "translations": results})

# # # @app.route('/api/analyze-sentiment', methods=['POST'])
# # # @login_required
# # # def analyze_sentiment_api():
# # #     if not request.is_json: return jsonify({"status": "error", "error": "Request must be JSON"}), 415
# # #     data = request.get_json(); text = data.get('text')
# # #     if not text: return jsonify({"status": "error", "error": "Missing 'text'"}), 400
# # #     result = azure_services.analyze_sentiment(text)
# # #     if 'error' in result: return jsonify({"status": "error", "error": result['error']}), 500
# # #     save_processing_result('text', 'sentiment', text[:500], result)
# # #     return jsonify({"status": "success", "sentiment_analysis": result})

# # # @app.route('/api/summarize', methods=['POST'])
# # # @login_required
# # # def summarize_text_api():
# # #     if not request.is_json: return jsonify({"status": "error", "error": "Request must be JSON"}), 415
# # #     data = request.get_json(); text = data.get('text'); s_type = data.get('type', 'extractive'); s_count = data.get('sentence_count', 3)
# # #     if not text: return jsonify({"status": "error", "error": "Missing 'text'"}), 400
# # #     if s_type not in ['extractive', 'abstractive']: return jsonify({"status": "error", "error": "Invalid summary 'type'"}), 400
# # #     result = azure_services.extractive_summarize(text, s_count) if s_type == 'extractive' else azure_services.abstractive_summarize(text, s_count)
# # #     if 'error' in result: return jsonify({"status": "error", "error": result['error']}), 500
# # #     save_processing_result('text_summary', f'{s_type}_summary', text[:500], result, {"type": s_type, "sentence_count": s_count})
# # #     return jsonify({"status": "success", "summary_data": result})

# # # @app.route('/api/analyze-image', methods=['POST'])
# # # @login_required
# # # def analyze_image_api(): 
# # #     if 'imageFile' not in request.files: return jsonify({"status": "error", "error": "No 'imageFile' part"}), 400
# # #     image_file = request.files['imageFile']
# # #     if image_file.filename == '': return jsonify({"status": "error", "error": "No image selected"}), 400
    
# # #     feature_map_client_to_sdk = {
# # #         "description": VisualFeatureTypes.description, "tags": VisualFeatureTypes.tags,
# # #         "objects": VisualFeatureTypes.objects, "faces": VisualFeatureTypes.faces,
# # #         "adult": VisualFeatureTypes.adult, "brands": VisualFeatureTypes.brands,
# # #         "categories": VisualFeatureTypes.categories, "color": VisualFeatureTypes.color
# # #     }
# # #     selected_sdk_features = []
# # #     form_features_names = [] 
# # #     for feature_key_form, sdk_feature_enum in feature_map_client_to_sdk.items():
# # #         if request.form.get(feature_key_form) == 'true':
# # #             selected_sdk_features.append(sdk_feature_enum)
# # #             form_features_names.append(feature_key_form)
            
# # #     if not selected_sdk_features:
# # #          return jsonify({"status": "error", "error": "No analysis features selected"}), 400
        
# # #     if image_file and allowed_file(image_file.filename, {'png', 'jpg', 'jpeg', 'gif', 'bmp'}):
# # #         filename = secure_filename(image_file.filename)
# # #         temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_images')
# # #         os.makedirs(temp_dir, exist_ok=True)
# # #         temp_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{filename}")
# # #         try:
# # #             image_file.save(temp_path)
# # #             analysis_result = azure_services.analyze_image(temp_path, visual_features_enums=selected_sdk_features) # Corrected param name
# # #         finally:
# # #             if os.path.exists(temp_path): os.remove(temp_path)
# # #         if 'error' in analysis_result: return jsonify({"status": "error", "error": analysis_result['error']}), 500
# # #         save_processing_result('image', 'vision_analysis', filename, analysis_result, {"features_requested": form_features_names})
# # #         return jsonify({"status": "success", "analysis": analysis_result, "filename": filename})
# # #     else: return jsonify({"status": "error", "error": "Invalid image file type"}), 400

# # # @app.route('/api/youtube-transcript', methods=['POST'])
# # # @login_required
# # # def youtube_transcript_api_route():
# # #     if not request.is_json: return jsonify({"status": "error", "error": "Request must be JSON"}), 415
# # #     data = request.get_json(); url = data.get('url')
# # #     if not url: return jsonify({"status": "error", "error": "Missing 'url'"}), 400
# # #     from background_tasks import youtube_transcript
# # #     task = youtube_transcript.apply_async(args=[url])
# # #     try: result = task.get(timeout=120)
# # #     except Exception as e: logger.error(f"YT task error: {e}"); return jsonify({"status":"error", "error": str(e)}), 500
# # #     if result.get('status') == 'error': return jsonify(result), result.get('http_status_code', 400)
# # #     save_processing_result('youtube', 'transcript', url, result, {"url": url})
# # #     return jsonify({"status": "success", "transcript": result})

# # # @app.route('/api/transcribe-audio', methods=['POST'])
# # # @login_required
# # # def transcribe_audio_route():
# # #     if 'audio' not in request.files: return jsonify({"status": "error", "error": "No audio file part"}), 400
# # #     audio_f = request.files['audio']; lang = request.form.get('language')
# # #     if audio_f.filename == '': return jsonify({"status": "error", "error": "No audio selected"}), 400
# # #     if audio_f and allowed_file(audio_f.filename, {'wav', 'mp3', 'ogg', 'flac', 'm4a'}):
# # #         fname = secure_filename(audio_f.filename)
# # #         tmp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_audio'); os.makedirs(tmp_dir, exist_ok=True)
# # #         fpath = os.path.join(tmp_dir, f"{uuid.uuid4()}_{fname}")
# # #         try:
# # #             audio_f.save(fpath); from background_tasks import transcribe_audio
# # #             task = transcribe_audio.apply_async(args=[fpath, lang])
# # #             result = task.get(timeout=600) 
# # #         finally:
# # #             if os.path.exists(fpath): os.remove(fpath)
# # #         if 'error' in result: return jsonify(result), result.get('http_status_code', 400)
# # #         save_processing_result('audio', 'transcribe_audio', fname, result, {"language": lang})
# # #         return jsonify({"status": "success", "transcription": result})
# # #     else: return jsonify({"status": "error", "error": "Invalid audio file type"}), 400

# # # @app.route('/api/get-user-documents', methods=['GET'])
# # # @login_required
# # # def get_user_documents():
# # #     try:
# # #         docs = document_qa.get_user_documents(current_user.id)
# # #         s_docs = []
# # #         for d in docs:
# # #             if 'upload_date' in d and isinstance(d['upload_date'], datetime): d['upload_date'] = d['upload_date'].isoformat()
# # #             elif 'timestamp' in d and isinstance(d['timestamp'], datetime): d['timestamp'] = d['timestamp'].isoformat()
# # #             s_docs.append(d)
# # #         return jsonify({"status": "success", "documents": s_docs})
# # #     except Exception as e: logger.error(f"Doc fetch error {current_user.id}: {e}", exc_info=True); return jsonify({"status": "error", "error": "Could not get docs."}), 500

# # # @app.route('/api/document-qa', methods=['POST'])
# # # @login_required
# # # def document_qa_api():
# # #     if 'document' not in request.files: return jsonify({"status": "error", "error": "No 'document' part"}), 400
# # #     doc_file = request.files['document']
# # #     if doc_file.filename == '': return jsonify({"status": "error", "error": "No document selected"}), 400
# # #     if not allowed_file(doc_file.filename, {'pdf', 'txt', 'docx'}): return jsonify({"status": "error", "error": "Invalid doc format"}), 400
# # #     filename = secure_filename(doc_file.filename)
# # #     tmp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_docqa_{uuid.uuid4()}_{filename}")
# # #     try:
# # #         doc_file.save(tmp_path); file_size = os.path.getsize(tmp_path)
# # #         doc_id = document_qa.add_document(tmp_path, current_user.id, file_size)
# # #     except Exception as e: logger.error(f"Doc upload error: {e}", exc_info=True); return jsonify({"status": "error", "error": "Server doc processing error."}), 500
# # #     finally:
# # #         if os.path.exists(tmp_path): os.remove(tmp_path)
# # #     if not doc_id: return jsonify({"status": "error", "error": "Failed to add doc to QA."}), 500
# # #     save_processing_result('document_upload', 'doc_upload', filename, {"doc_id": doc_id, "filename": filename, "size": file_size})
# # #     return jsonify({"status": "success", "message": "Doc uploaded.", "doc_id": doc_id, "filename": filename, "size": file_size}), 201

# # # @app.route('/api/document/<string:document_id>/ask', methods=['POST'])
# # # @login_required
# # # def api_document_ask(document_id):
# # #     if not request.is_json: return jsonify({"status": "error", "error": "Request must be JSON"}), 415
# # #     data = request.get_json(); question = data.get('question')
# # #     if not question: return jsonify({"status": "error", "error": "Question missing"}), 400
# # #     meta = document_qa.get_document_metadata(document_id)
# # #     if not meta or str(meta.get("user_id")) != str(current_user.id): return jsonify({"status": "error", "error": "Doc not found/access denied"}), 404
# # #     ans_data = document_qa.query_document(document_id, question)
# # #     if 'error' in ans_data: return jsonify({"status": "error", "error": ans_data['error']}), 500
# # #     proc_ans = {"answer_text": ans_data.get("answer", "N/A"), "results": [ans_data.get("context")] if ans_data.get("context") else []}
# # #     save_processing_result('document_qa', 'Youtube', f"DocID:{document_id}, Q:{question[:100]}", # Corrected action_type
# # #                            {"question": question, "answer": proc_ans}, {"document_id": document_id, "question": question})
# # #     return jsonify({"status": "success", **proc_ans})

# # # @app.route('/api/document/<string:document_id>', methods=['DELETE'])
# # # @login_required
# # # def api_document_delete(document_id):
# # #     if document_qa.delete_document(document_id, current_user.id): return jsonify({"status": "success", "message": "Doc deleted."})
# # #     else: return jsonify({"status": "error", "error": "Delete failed or doc not found/access denied"}), 404

# # # socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*", logger=True, engineio_logger=True)

# # # @socketio.on('connect')
# # # def handle_connect_socket(): logger.info(f"Socket.IO Client connected: SID {request.sid}")

# # # @socketio.on('join_room')
# # # def on_join_room(data):
# # #     username = data.get('user', 'Anon'); room = data.get('room', 'general')
# # #     join_room(room); logger.info(f"User {username} (SID:{request.sid}) joined room: {room}")
# # #     emit('user_joined', {'user': username, 'room': room}, to=room)

# # # @socketio.on('leave_room')
# # # def on_leave_room(data):
# # #     username = data.get('user', 'Anon'); room = data.get('room', 'general')
# # #     leave_room(room); logger.info(f"User {username} (SID:{request.sid}) left room: {room}")
# # #     emit('user_left', {'user': username, 'room': room}, to=room, include_self=False)

# # # @socketio.on('text_message')
# # # def handle_chat_text_message(data):
# # #     room = data.get('room','general'); user = data.get('user','Anon'); text = data.get('text',''); lang_code = data.get('translate_to')
# # #     logger.info(f"Message from {user} in {room}: '{text}', ToLang: {lang_code}")
# # #     orig_txt = text; orig_lang_name = "Original"; trans_txt = text; trans_lang_name = None # Corrected: original_lang_name
# # #     if lang_code:
# # #         trans_res = azure_services.translate_text(text, [lang_code])
# # #         if not trans_res.get('error') and trans_res.get(lang_code):
# # #             trans_txt = trans_res[lang_code]; trans_lang_name = lang_code 
# # #             logger.info(f"Translated '{text}' to '{trans_txt}' ({lang_code}) for {user}")
# # #         else: logger.warning(f"Translate fail for {user}: {trans_res.get('error')}")
# # #     payload = {'user':user, 'text':trans_txt, 
# # #                'original_text': orig_txt if trans_txt.lower()!=orig_txt.lower() else None,
# # #                'original_lang_name': orig_lang_name if trans_txt.lower()!=orig_txt.lower() else None, # Corrected
# # #                'translated_to_lang_name': trans_lang_name, 'timestamp':datetime.now(timezone.utc).isoformat(), 'room':room}
# # #     emit('chat_message', payload, to=room)

# # # @socketio.on('typing')
# # # def on_typing_socket(data): emit('typing', data, to=data.get('room','general'), include_self=False)

# # # @socketio.on('stop_typing')
# # # def on_stop_typing_socket(data): emit('stop_typing', data, to=data.get('room','general'), include_self=False)

# # # @socketio.on('disconnect')
# # # def handle_socket_disconnect_event(): logger.info(f"Socket.IO Client disconnected: SID {request.sid}")

# # # @app.route('/api/get-speech-token', methods=['GET'])
# # # @login_required
# # # def get_speech_token_route():
# # #     creds = azure_services.get_speech_token()
# # #     if 'error' in creds: return jsonify(creds), 503
# # #     return jsonify(creds)

# # # def allowed_file(filename, exts): return '.' in filename and filename.rsplit('.',1)[1].lower() in exts

# # # @app.errorhandler(400)
# # # def bad_request_error_handler(e): 
# # #     msg = str(e.description if hasattr(e, 'description') else e)
# # #     logger.warning(f"400: {msg} for {request.url}")
# # #     if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html: return jsonify(status="error",error="Bad Request",message=msg),400
# # #     return render_template('400.html', error=e),400 

# # # @app.errorhandler(404)
# # # def page_not_found_error_handler(e): 
# # #     msg = str(e.description if hasattr(e, 'description') else e)
# # #     logger.warning(f"404: {request.path} - {msg}")
# # #     if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html: return jsonify(status="error",error="Not Found",message=msg),404
# # #     return render_template('404.html', error=e),404

# # # @app.errorhandler(415)
# # # def unsupported_media_type_error_handler(e):
# # #     msg = str(e.description if hasattr(e, 'description') else e)
# # #     logger.warning(f"415: {msg} for {request.url}")
# # #     if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html: return jsonify(status="error",error="Unsupported Media Type",message=msg),415
# # #     return render_template('500.html',error_code=415,error_message="Unsupported Media Type",error_detail=msg),415

# # # @app.errorhandler(500)
# # # def internal_server_error_handler_page(e): 
# # #     logger.error(f"500: {e} for {request.url}", exc_info=sys.exc_info()); db.session.rollback()
# # #     if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html: return jsonify(status="error",error="Internal Server Error",message="Unexpected server error."),500
# # #     return render_template('500.html', error=e),500

# # # if __name__ == '__main__':
# # #     logger.info("Starting Flask-SocketIO development server with eventlet...")
# # #     try:
# # #         use_reloader_val = True if os.environ.get("WERKZEUG_RUN_MAIN") != "true" else False
# # #         socketio.run(app, debug=True, host='0.0.0.0', port=5000, use_reloader=use_reloader_val)
# # #     except KeyboardInterrupt: logger.info("Application shutting down...")
# # #     except Exception as e: logger.critical(f"Failed to start application: {e}", exc_info=True)






# # # """
# # # Main Flask Application
# # # """
# # import os
# # import sys
# # import logging
# # import uuid
# # import json
# # import io 
# # from datetime import datetime, timezone 
# # from werkzeug.utils import secure_filename
# # from werkzeug.security import generate_password_hash, check_password_hash
# # import eventlet
# # eventlet.monkey_patch()

# # from typing import Optional, Dict, List, Any, Tuple

# # from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, abort
# # from flask_sqlalchemy import SQLAlchemy
# # from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
# # from flask_socketio import SocketIO, emit, join_room, leave_room

# # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(pathname)s:%(lineno)d]') # Added pathname and lineno
# # logger = logging.getLogger(__name__)

# # app = Flask(__name__)

# # # --- Application Configuration ---
# # base_dir = os.path.abspath(os.path.dirname(__file__))
# # from dotenv import load_dotenv
# # dotenv_path = os.path.join(base_dir, '.env')
# # if os.path.exists(dotenv_path):
# #     logger.info(f"Attempting to load .env file from: {dotenv_path}")
# #     load_dotenv(dotenv_path=dotenv_path)
# #     logger.info(".env file loaded successfully.")
# # else:
# #     logger.warning(f".env file not found at: {dotenv_path}.")

# # app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-please-change-ASAP')
# # if app.config['SECRET_KEY'] == 'dev-secret-key-please-change-ASAP' and not app.debug:
# #     logger.critical("CRITICAL: Using default FLASK_SECRET_KEY in a non-debug environment. THIS IS HIGHLY INSECURE. SET A STRONG, UNIQUE KEY IN YOUR .env FILE.")

# # instance_folder_path = os.path.join(base_dir, 'instance')
# # os.makedirs(instance_folder_path, exist_ok=True)

# # default_db_filename = "toolkit_v4_1.db" # Incremented DB version
# # db_path_from_env = os.environ.get('DATABASE_URL', f'sqlite:///{default_db_filename}')
# # logger.info(f"DATABASE_URL from environment (or default): {db_path_from_env}")
# # if db_path_from_env.startswith('sqlite:///'):
# #     db_file_part = db_path_from_env[len('sqlite:///'):]
# #     if os.path.isabs(db_file_part): absolute_db_path = db_file_part
# #     elif db_file_part.startswith('instance/'): absolute_db_path = os.path.join(base_dir, db_file_part)
# #     else: absolute_db_path = os.path.join(instance_folder_path, db_file_part)
# #     db_dir = os.path.dirname(absolute_db_path)
# #     if not os.path.exists(db_dir): os.makedirs(db_dir, exist_ok=True)
# #     app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{absolute_db_path.replace(os.sep, "/")}'
# # else:
# #     app.config['SQLALCHEMY_DATABASE_URI'] = db_path_from_env
# # logger.info(f"Final SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
# # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# # upload_folder_name = os.environ.get('UPLOAD_FOLDER_NAME', 'uploads')
# # upload_folder_path = os.path.join(base_dir, upload_folder_name)
# # app.config['UPLOAD_FOLDER'] = upload_folder_path
# # max_content_length_str = os.environ.get('MAX_CONTENT_LENGTH', '16777216')
# # if '#' in max_content_length_str: max_content_length_str = max_content_length_str.split('#')[0].strip()
# # app.config['MAX_CONTENT_LENGTH'] = int(max_content_length_str)
# # os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# # logger.info(f"Ensured uploads folder exists at: {app.config['UPLOAD_FOLDER']}")

# # logger.info(f"TRANSLATOR_SUBSCRIPTION_KEY: {os.environ.get('TRANSLATOR_SUBSCRIPTION_KEY', 'Not set')[:5]}...")
# # logger.info(f"LANGUAGE_SUBSCRIPTION_KEY: {os.environ.get('LANGUAGE_SUBSCRIPTION_KEY', 'Not set')[:5]}...")
# # logger.info(f"SPEECH_SUBSCRIPTION_KEY: {os.environ.get('SPEECH_SUBSCRIPTION_KEY', 'Not set')[:5]}...")
# # logger.info(f"VISION_SUBSCRIPTION_KEY: {os.environ.get('VISION_SUBSCRIPTION_KEY', 'Not set')[:5]}...")

# # db = SQLAlchemy(app)
# # login_manager = LoginManager(app)
# # login_manager.login_view = 'login'
# # login_manager.login_message_category = 'info'

# # # It's crucial these imports happen AFTER app is defined if they depend on app context or config
# # try:
# #     from azure_services import azure_services, VisualFeatureTypes 
# #     import document_qa
# #     document_qa.init_document_qa(app.config['UPLOAD_FOLDER']) # Initialize with app config
# # except ImportError as e:
# #     logger.critical(f"Failed to import core modules (azure_services, document_qa): {e}", exc_info=True)
# #     sys.exit("Application cannot start due to missing core modules.")


# # try:
# #     import nltk
# #     nltk.data.find('tokenizers/punkt'); nltk.data.find('corpora/stopwords')
# # except LookupError as e:
# #     resource_name = str(e).split("'")[1] if "'" in str(e) else "nltk_resource"
# #     logger.warning(f"NLTK resource '{resource_name}' missing. Downloading...")
# #     try: nltk.download(resource_name, quiet=True); logger.info(f"NLTK resource '{resource_name}' downloaded.")
# #     except Exception as de: logger.error(f"Failed to download NLTK '{resource_name}': {de}")

# # class User(UserMixin, db.Model):
# #     __tablename__ = 'user'
# #     id = db.Column(db.Integer, primary_key=True)
# #     username = db.Column(db.String(80), unique=True, nullable=False)
# #     password_hash = db.Column(db.String(256), nullable=False)
# #     summaries = db.relationship('Summary', backref='user', lazy='dynamic', cascade="all, delete-orphan")
# #     def set_password(self, password): self.password_hash = generate_password_hash(password)
# #     def check_password(self, password): return check_password_hash(self.password_hash, password)

# # class Summary(db.Model):
# #     __tablename__ = 'summary'
# #     id = db.Column(db.Integer, primary_key=True)
# #     input_type = db.Column(db.String(50), nullable=False)
# #     action_type = db.Column(db.String(50), nullable=False)
# #     original_content_preview = db.Column(db.Text, nullable=True)
# #     processed_content = db.Column(db.JSON, nullable=True)
# #     details_json = db.Column(db.JSON, nullable=True)
# #     timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
# #     user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
# #     def to_dict(self):
# #         return {'id': self.id, 'input_type': self.input_type, 'action_type': self.action_type,
# #                 'original_content_preview': self.original_content_preview,
# #                 'processed_content': self.processed_content, 'details_json': self.details_json,
# #                 'timestamp': self.timestamp.isoformat() if self.timestamp else None, 'user_id': self.user_id}
# # try:
# #     with app.app_context(): 
# #         db.create_all()
# #         if not User.query.filter_by(username="testuser").first():
# #             test_user = User(username="testuser"); test_user.set_password("password")
# #             db.session.add(test_user); db.session.commit()
# #             logger.info("Test user 'testuser' created.")
# # except Exception as e: logger.error(f"DB init error: {e}")

# # @login_manager.user_loader
# # def load_user(user_id: str) -> Optional[User]:
# #     try: return db.session.get(User, int(user_id)) 
# #     except: logger.error(f"Failed to load user by ID: {user_id}", exc_info=True); return None

# # @app.context_processor
# # def inject_current_year(): return {'current_year': datetime.now(timezone.utc).year}

# # def save_processing_result(input_type, action_type, original_preview, processed_data, request_details=None):
# #     if current_user.is_authenticated:
# #         try:
# #             entry = Summary(user_id=current_user.id, input_type=input_type, action_type=action_type,
# #                             original_content_preview=original_preview, processed_content=processed_data,
# #                             details_json=request_details, timestamp=datetime.now(timezone.utc))
# #             db.session.add(entry); db.session.commit(); return entry.id
# #         except Exception as e: db.session.rollback(); logger.error(f"DB save error for {current_user.id}: {e}", exc_info=True)
# #     return None

# # def allowed_file(filename, exts): return '.' in filename and filename.rsplit('.',1)[1].lower() in exts

# # # --- Helper function to get text from various inputs (REFINED V4.1) ---
# # def get_text_from_request_data(request_form_data: Dict[str, Any], request_files_data) -> Tuple[Optional[str], Optional[str], Optional[str]]:
# #     text_content = request_form_data.get('text') 
# #     original_filename = None
# #     error_message = None

# #     if text_content:
# #         logger.debug("Helper: Using direct text from request form data.")
# #         return text_content, None, None

# #     file_key_for_pdf_extraction = 'pdf_file' # Key used by index.html JS
    
# #     if file_key_for_pdf_extraction in request_files_data:
# #         pdf_file_storage = request_files_data[file_key_for_pdf_extraction]
# #         if pdf_file_storage and pdf_file_storage.filename:
# #             original_filename = secure_filename(pdf_file_storage.filename)
# #             logger.info(f"Helper: Processing PDF '{original_filename}' via key '{file_key_for_pdf_extraction}'.")
# #             if not allowed_file(original_filename, {'pdf'}):
# #                 return None, "Invalid PDF file type for text extraction. Only .pdf is allowed.", original_filename
            
# #             # Ensure UPLOAD_FOLDER is an absolute path and exists
# #             upload_folder_abs = app.config.get('UPLOAD_FOLDER')
# #             if not upload_folder_abs or not os.path.isabs(upload_folder_abs):
# #                 logger.error(f"UPLOAD_FOLDER '{upload_folder_abs}' is not absolute or not configured. Cannot save temp PDF.")
# #                 return None, "Server configuration error for file uploads.", original_filename

# #             temp_dir = os.path.join(upload_folder_abs, 'temp_pdf_extraction_api_v4_1') # Specific subdir
# #             try:
# #                 os.makedirs(temp_dir, exist_ok=True)
# #             except OSError as e:
# #                 logger.error(f"Helper: Could not create temp directory {temp_dir}: {e}", exc_info=True)
# #                 return None, f"Server error creating temp directory for PDF: {str(e)}", original_filename

# #             temp_pdf_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{original_filename}")
            
# #             try:
# #                 pdf_file_storage.save(temp_pdf_path)
# #                 logger.info(f"Helper: Temporarily saved PDF for extraction: {temp_pdf_path}")
# #                 text_content = document_qa.extract_text_from_document(temp_pdf_path) 
# #                 if not text_content or not text_content.strip(): # Check if empty or just whitespace
# #                     error_message = "Could not extract meaningful text from the PDF. It might be image-based, empty, or protected."
# #                     logger.warning(f"Helper: No meaningful text extracted from PDF: {original_filename}")
# #                 else:
# #                     logger.info(f"Helper: Successfully extracted {len(text_content)} chars from PDF: {original_filename}")
# #             except Exception as e:
# #                 logger.error(f"Helper: Error during PDF text extraction for '{original_filename}': {e}", exc_info=True)
# #                 error_message = f"Server error during PDF text extraction: {str(e)}"
# #             finally:
# #                 if os.path.exists(temp_pdf_path):
# #                     try: os.remove(temp_pdf_path); logger.debug(f"Helper: Removed temp PDF: {temp_pdf_path}")
# #                     except Exception as e_rem: logger.error(f"Helper: Error removing temp PDF {temp_pdf_path}: {e_rem}")
# #             return text_content, error_message, original_filename
# #         else:
# #             logger.warning(f"Helper: '{file_key_for_pdf_extraction}' in request.files but it's invalid or has no filename.")
# #             return None, f"A PDF file via '{file_key_for_pdf_extraction}' was expected but not properly provided.", None
            
# #     logger.debug("Helper: No direct text or 'pdf_file' found in request for text extraction.")
# #     return None, "No text or PDF file ('pdf_file') found in the request for text extraction.", None


# # # --- API Routes (Refined for PDF handling V4.1) ---
# # @app.route('/api/translate', methods=['POST'])
# # @login_required 
# # def translate_text_api(): 
# #     text_to_process = None; original_filename = None; error_msg = None
# #     data_source_params = {} 
# #     logger.debug(f"Translate API: Received request. Content-Type: {request.content_type}")

# #     if request.content_type and request.content_type.startswith('application/json'):
# #         data_source_params = request.get_json()
# #         if not data_source_params: return jsonify({"status": "error", "error": "Invalid JSON request."}), 400
# #         text_to_process = data_source_params.get('text')
# #         logger.debug("Translate API: Parsed JSON request.")
# #     elif request.content_type and request.content_type.startswith('multipart/form-data'):
# #         logger.debug(f"Translate API: Parsed FormData. Form: {request.form.to_dict()}, Files: {list(request.files.keys())}")
# #         text_to_process, error_msg, original_filename = get_text_from_request_data(request.form, request.files)
# #         data_source_params = request.form 
# #     else:
# #         logger.warning(f"Translate API: Unsupported content type: {request.content_type}")
# #         return jsonify({"status": "error", "error": "Unsupported content type. Must be JSON or FormData."}), 415

# #     if error_msg: return jsonify({"status": "error", "error": error_msg}), 400
# #     if not text_to_process: return jsonify({"status": "error", "error": "Missing text to translate after attempting extraction."}), 400

# #     targets_str = data_source_params.get('target_languages')
# #     targets = []
# #     if isinstance(targets_str, str):
# #         try: targets = json.loads(targets_str)
# #         except json.JSONDecodeError: logger.warning(f"Could not parse target_languages string from form data: {targets_str}")
# #     elif isinstance(targets_str, list): targets = targets_str
    
# #     if not targets and 'targetLanguages[]' in request.form: 
# #         targets = request.form.getlist('targetLanguages[]')

# #     if not targets: return jsonify({"status": "error", "error": "Missing 'target_languages'"}), 400
    
# #     source = data_source_params.get('source_language')
    
# #     logger.info(f"Translate API: Translating text (len: {len(text_to_process)}) to {targets}, source: {source or 'auto'}")
# #     results = azure_services.translate_text(text_to_process, targets, source)
# #     if 'error' in results: 
# #         logger.error(f"Translation service error from azure_services: {results['error']}")
# #         return jsonify({"status": "error", "error": results['error']}), 500
    
# #     preview = original_filename if original_filename else text_to_process[:500]
# #     save_processing_result('pdf' if original_filename else 'text', 'translate', preview, results, {"target_languages": targets, "source_language": source})
# #     return jsonify({"status": "success", "translations": results, 
# #                     "original_text_processed": text_to_process if not original_filename else None, 
# #                     "processed_filename": original_filename})

# # @app.route('/api/analyze-sentiment', methods=['POST'])
# # @login_required
# # def analyze_sentiment_api():
# #     text_to_process = None; original_filename = None; error_msg = None
# #     logger.debug(f"Sentiment API: Received request. Content-Type: {request.content_type}")

# #     if request.content_type and request.content_type.startswith('application/json'):
# #         data = request.get_json()
# #         if not data: return jsonify({"status": "error", "error": "Invalid JSON request."}), 400
# #         text_to_process = data.get('text')
# #         logger.debug("Sentiment API: Parsed JSON request.")
# #     elif request.content_type and request.content_type.startswith('multipart/form-data'):
# #         logger.debug(f"Sentiment API: Parsed FormData. Form: {request.form.to_dict()}, Files: {list(request.files.keys())}")
# #         text_to_process, error_msg, original_filename = get_text_from_request_data(request.form, request.files)
# #     else: 
# #         logger.warning(f"Sentiment API: Unsupported content type: {request.content_type}")
# #         return jsonify({"status": "error", "error": "Unsupported content type."}), 415

# #     if error_msg: return jsonify({"status": "error", "error": error_msg}), 400
# #     if not text_to_process: return jsonify({"status": "error", "error": "Missing text for sentiment analysis after attempting extraction."}), 400
        
# #     logger.info(f"Sentiment API: Analyzing text (len: {len(text_to_process)})")
# #     result = azure_services.analyze_sentiment(text_to_process)
# #     if 'error' in result: return jsonify({"status": "error", "error": result['error']}), 500
    
# #     preview = original_filename if original_filename else text_to_process[:500]
# #     save_processing_result('pdf' if original_filename else 'text', 'sentiment', preview, result)
# #     return jsonify({"status": "success", "sentiment_analysis": result, "original_text_processed": text_to_process if not original_filename else None, "processed_filename": original_filename})

# # @app.route('/api/summarize', methods=['POST'])
# # @login_required
# # def summarize_api():
# #     text_to_process = None; original_filename = None; error_msg = None
# #     data_source_params = {} 
# #     logger.debug(f"Summarize API: Received request. Content-Type: {request.content_type}")

# #     if request.content_type and request.content_type.startswith('application/json'):
# #         data_source_params = request.get_json()
# #         if not data_source_params: return jsonify({"status": "error", "error": "Invalid JSON request."}), 400
# #         text_to_process = data_source_params.get('text')
# #         logger.debug("Summarize API: Parsed JSON request.")
# #     elif request.content_type and request.content_type.startswith('multipart/form-data'):
# #         logger.debug(f"Summarize API: Parsed FormData. Form: {request.form.to_dict()}, Files: {list(request.files.keys())}")
# #         text_to_process, error_msg, original_filename = get_text_from_request_data(request.form, request.files)
# #         data_source_params = request.form 
# #     else: 
# #         logger.warning(f"Summarize API: Unsupported content type: {request.content_type}")
# #         return jsonify({"status": "error", "error": "Unsupported content type."}), 415

# #     if error_msg: return jsonify({"status": "error", "error": error_msg}), 400
# #     if not text_to_process: return jsonify({"status": "error", "error": "Missing text for summarization after attempting extraction."}), 400

# #     s_type = data_source_params.get('type', 'extractive')
# #     s_count_str = data_source_params.get('sentence_count', '3')
# #     try: s_count = int(s_count_str)
# #     except ValueError: return jsonify({"status":"error", "error": "Invalid sentence_count."}), 400
# #     if s_type not in ['extractive', 'abstractive']: return jsonify({"status": "error", "error": "Invalid summary type"}), 400
    
# #     logger.info(f"Summarize API: Type: {s_type}, Sentences: {s_count}, Text len: {len(text_to_process)}")
# #     result = azure_services.extractive_summarize(text_to_process, s_count) if s_type == 'extractive' else azure_services.abstractive_summarize(text_to_process, s_count)
# #     if 'error' in result: return jsonify({"status": "error", "error": result['error']}), 500
    
# #     preview = original_filename if original_filename else text_to_process[:500]
# #     save_processing_result('pdf' if original_filename else 'text_summary', f'{s_type}_summary', preview, result, {"type": s_type, "sentence_count": s_count})
# #     return jsonify({"status": "success", "summary_data": result, "original_text_processed": text_to_process if not original_filename else None, "processed_filename": original_filename})


# # # --- Page Rendering Routes ---
# # @app.route('/')
# # def index(): 
# #     try:
# #         # You can pass any necessary context variables to index.html here if needed
# #         return render_template('index.html')
# #     except Exception as e:
# #         logger.error(f"Error rendering index.html: {e}", exc_info=True)
# #         # Instead of abort(500) which might be too generic,
# #         # render a specific error page or return a JSON error if it's an API-like context
# #         return render_template('500.html', error_message="Error rendering homepage template.", error_detail=str(e)), 500


# # @app.route('/about')
# # def about(): return render_template('about.html')
# # @app.route('/image-analyzer-page')
# # @login_required
# # def image_analyzer_page(): return render_template('image_analyzer.html')
# # @app.route('/live-chat-page')
# # @login_required
# # def live_chat_page(): return render_template('live_chat.html')
# # @app.route('/doc-qa-page')
# # @login_required
# # def doc_qa_page(): return render_template('doc_qa.html')

# # @app.route('/my-summaries')
# # @login_required
# # def my_summaries():
# #     page = request.args.get('page', 1, type=int); per_page = 10 
# #     summaries_pagination_obj = db.session.query(Summary).filter_by(user_id=current_user.id)\
# #         .order_by(Summary.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
# #     summaries_list = [s.to_dict() for s in summaries_pagination_obj.items]
# #     try: summaries_json_str = json.dumps(summaries_list)
# #     except TypeError as e: logger.error(f"Error serializing summaries: {e}"); summaries_json_str = "[]"
# #     return render_template('my_summaries.html', summaries=summaries_pagination_obj, summaries_json=summaries_json_str)

# # # --- Auth Routes ---
# # @app.route('/login', methods=['GET', 'POST'])
# # def login(): 
# #     if current_user.is_authenticated: return redirect(url_for('index'))
# #     if request.method == 'POST':
# #         username = request.form.get('username'); password = request.form.get('password')
# #         user = User.query.filter_by(username=username).first()
# #         if user and user.check_password(password):
# #             login_user(user, remember=request.form.get('remember') == 'on')
# #             next_page = request.args.get('next')
# #             if not next_page or not next_page.startswith('/'): next_page = url_for('index')
# #             flash('Logged in successfully!', 'success'); return redirect(next_page)
# #         else: flash('Invalid username or password. Please try again.', 'danger')
# #     return render_template('login.html')

# # @app.route('/register', methods=['GET', 'POST'])
# # def register(): 
# #     if current_user.is_authenticated: return redirect(url_for('index'))
# #     if request.method == 'POST':
# #         username = request.form.get('username'); password = request.form.get('password')
# #         if not username or not password: flash('Username and password are required.', 'warning'); return redirect(url_for('register'))
# #         if User.query.filter_by(username=username).first(): flash('Username already exists.', 'warning'); return redirect(url_for('register'))
# #         new_user = User(username=username); new_user.set_password(password)
# #         try: db.session.add(new_user); db.session.commit(); flash('Registration successful! Please log in.', 'success'); return redirect(url_for('login'))
# #         except Exception as e: db.session.rollback(); logger.error(f"Reg error {username}: {e}"); flash('Registration error.', 'danger')
# #     return render_template('register.html')

# # @app.route('/logout')
# # @login_required
# # def logout(): logout_user(); flash('You have been logged out.', 'info'); return redirect(url_for('index'))

# # # --- Other API Routes ---
# # @app.route('/api/analyze-image', methods=['POST'])
# # @login_required
# # def analyze_image_api(): 
# #     if 'imageFile' not in request.files: return jsonify({"status": "error", "error": "No 'imageFile' part"}), 400
# #     image_file = request.files['imageFile']
# #     if image_file.filename == '': return jsonify({"status": "error", "error": "No image selected"}), 400
    
# #     feature_map_client_to_sdk = {
# #         "description": VisualFeatureTypes.description, "tags": VisualFeatureTypes.tags,
# #         "objects": VisualFeatureTypes.objects, "faces": VisualFeatureTypes.faces,
# #         "adult": VisualFeatureTypes.adult, "brands": VisualFeatureTypes.brands,
# #         "categories": VisualFeatureTypes.categories, "color": VisualFeatureTypes.color
# #     }
# #     selected_sdk_features = []
# #     form_features_names = [] 
# #     for feature_key_form, sdk_feature_enum in feature_map_client_to_sdk.items():
# #         if request.form.get(feature_key_form) == 'true':
# #             selected_sdk_features.append(sdk_feature_enum)
# #             form_features_names.append(feature_key_form)
            
# #     if not selected_sdk_features:
# #          return jsonify({"status": "error", "error": "No analysis features selected"}), 400
        
# #     if image_file and allowed_file(image_file.filename, {'png', 'jpg', 'jpeg', 'gif', 'bmp'}):
# #         filename = secure_filename(image_file.filename)
# #         temp_filename = f"{uuid.uuid4()}_{filename}"
# #         temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_images')
# #         os.makedirs(temp_dir, exist_ok=True)
# #         temp_path = os.path.join(temp_dir, temp_filename)
# #         try:
# #             image_file.save(temp_path)
# #             analysis_result = azure_services.analyze_image(temp_path, visual_features_enums=selected_sdk_features)
# #         finally:
# #             if os.path.exists(temp_path): os.remove(temp_path)
# #         if 'error' in analysis_result: return jsonify({"status": "error", "error": analysis_result['error']}), 500
# #         save_processing_result('image', 'vision_analysis', filename, analysis_result, {"features_requested": form_features_names})
# #         return jsonify({"status": "success", "analysis": analysis_result, "filename": filename})
# #     else: return jsonify({"status": "error", "error": "Invalid image file type"}), 400

# # @app.route('/api/youtube-transcript', methods=['POST'])
# # @login_required
# # def youtube_transcript_api_route(): 
# #     if not request.is_json: return jsonify({"status": "error", "error": "Request must be JSON"}), 415
# #     data = request.get_json(); url = data.get('url')
# #     if not url: return jsonify({"status": "error", "error": "Missing 'url'"}), 400
# #     from background_tasks import youtube_transcript 
# #     task = youtube_transcript.apply_async(args=[url]) 
# #     try: result = task.get(timeout=120) 
# #     except Exception as e: logger.error(f"YT task error: {e}"); return jsonify({"status":"error", "error": str(e)}), 500
# #     if result.get('status') == 'error': return jsonify(result), result.get('http_status_code', 400) 
# #     save_processing_result('youtube', 'transcript', url, result, {"url": url})
# #     return jsonify({"status": "success", "transcript": result})


# # @app.route('/api/transcribe-audio', methods=['POST'])
# # @login_required
# # def transcribe_audio_route(): 
# #     if 'audio' not in request.files: return jsonify({"status": "error", "error": "No audio file part"}), 400
# #     audio_f = request.files['audio']; lang = request.form.get('language')
# #     if audio_f.filename == '': return jsonify({"status": "error", "error": "No audio selected"}), 400
# #     if audio_f and allowed_file(audio_f.filename, {'wav', 'mp3', 'ogg', 'flac', 'm4a'}): 
# #         fname = secure_filename(audio_f.filename)
# #         tmp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_audio'); os.makedirs(tmp_dir, exist_ok=True)
# #         fpath = os.path.join(tmp_dir, f"{uuid.uuid4()}_{fname}")
# #         try:
# #             audio_f.save(fpath); from background_tasks import transcribe_audio
# #             task = transcribe_audio.apply_async(args=[fpath, lang])
# #             result = task.get(timeout=600) 
# #         finally:
# #             if os.path.exists(fpath): os.remove(fpath)
# #         if 'error' in result: return jsonify(result), result.get('http_status_code', 400)
# #         save_processing_result('audio', 'transcribe_audio', fname, result, {"language": lang})
# #         return jsonify({"status": "success", "transcription": result})
# #     else: return jsonify({"status": "error", "error": "Invalid audio file type"}), 400

# # @app.route('/api/get-user-documents', methods=['GET'])
# # @login_required
# # def get_user_documents_route(): 
# #     try:
# #         docs = document_qa.get_user_documents(current_user.id)
# #         return jsonify({"status": "success", "documents": docs})
# #     except Exception as e: logger.error(f"Doc fetch error {current_user.id}: {e}", exc_info=True); return jsonify({"status": "error", "error": "Could not get docs."}), 500

# # @app.route('/api/document-qa', methods=['POST'])
# # @login_required
# # def upload_document_for_qa_api(): 
# #     if 'document' not in request.files: return jsonify({"status": "error", "error": "No 'document' part"}), 400
# #     doc_file = request.files['document']
# #     if doc_file.filename == '': return jsonify({"status": "error", "error": "No document selected"}), 400
# #     if not allowed_file(doc_file.filename, {'pdf', 'txt', 'docx'}): return jsonify({"status": "error", "error": "Invalid doc format"}), 400
    
# #     filename = secure_filename(doc_file.filename)
# #     temp_upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_docqa_upload_{uuid.uuid4()}_{filename}")
# #     try:
# #         doc_file.save(temp_upload_path)
# #         file_size = os.path.getsize(temp_upload_path)
# #         doc_id = document_qa.add_document(temp_upload_path, current_user.id, file_size)
# #     except Exception as e:
# #         logger.error(f"Document upload and processing error for QA: {e}", exc_info=True)
# #         return jsonify({"status": "error", "error": "Server error during document processing for QA."}), 500
# #     finally:
# #         if os.path.exists(temp_upload_path):
# #             try: os.remove(temp_upload_path)
# #             except Exception as e_rem: logger.error(f"Error removing temp QA upload {temp_upload_path}: {e_rem}")

# #     if not doc_id: return jsonify({"status": "error", "error": "Failed to add document to QA system."}), 500
# #     return jsonify({"status": "success", "message": "Document uploaded successfully for Q&A.", "doc_id": doc_id, "filename": filename, "size": file_size}), 201

# # @app.route('/api/document/<string:document_id>/ask', methods=['POST'])
# # @login_required
# # def api_document_ask_route(document_id): 
# #     if not request.is_json: return jsonify({"status": "error", "error": "Request must be JSON"}), 415
# #     data = request.get_json(); question = data.get('question')
# #     if not question: return jsonify({"status": "error", "error": "Question missing"}), 400
        
# #     ans_data = document_qa.query_document(document_id, question, user_id_for_auth=current_user.id) 
# #     if 'error' in ans_data: 
# #         status_code = 404 if "not found" in ans_data['error'].lower() else 500
# #         return jsonify({"status": "error", "error": ans_data['error']}), status_code
    
# #     doc_meta = document_qa.get_document_metadata(document_id)
# #     doc_name_preview = doc_meta.get('file_name', f"DocID:{document_id}") if doc_meta else f"DocID:{document_id}"
# #     save_processing_result('document_qa', 'question_answer', f"{doc_name_preview} - Q: {question[:100]}", 
# #                            {"question": question, "answer_data": ans_data}, 
# #                            {"document_id": document_id, "question": question})
# #     return jsonify({"status": "success", **ans_data})

# # @app.route('/api/document/<string:document_id>', methods=['DELETE'])
# # @login_required
# # def api_document_delete_route(document_id): 
# #     if document_qa.delete_document(document_id, current_user.id): 
# #         return jsonify({"status": "success", "message": "Document deleted successfully."})
# #     else: 
# #         return jsonify({"status": "error", "error": "Delete failed. Document not found or access denied."}), 404


# # socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*", logger=True, engineio_logger=True)
# # @socketio.on('connect')
# # def handle_connect_socket(): logger.info(f"Socket.IO Client connected: SID {request.sid}")

# # @socketio.on('join_room')
# # def on_join_room(data):
# #     username = data.get('user', 'Anon'); room = data.get('room', 'general')
# #     join_room(room); logger.info(f"User {username} (SID:{request.sid}) joined room: {room}")
# #     emit('user_joined', {'user': username, 'room': room}, to=room)

# # @socketio.on('leave_room')
# # def on_leave_room(data):
# #     username = data.get('user', 'Anon'); room = data.get('room', 'general')
# #     leave_room(room); logger.info(f"User {username} (SID:{request.sid}) left room: {room}")
# #     emit('user_left', {'user': username, 'room': room}, to=room, include_self=False)

# # @socketio.on('text_message')
# # def handle_chat_text_message(data):
# #     room = data.get('room','general'); user = data.get('user','Anon'); text = data.get('text',''); lang_code = data.get('translate_to')
# #     logger.info(f"Message from {user} in {room}: '{text}', ToLang: {lang_code}")
# #     orig_txt = text; orig_lang_name = "Original"; trans_txt = text; trans_lang_name = None 
# #     if lang_code and lang_code.strip() != "": 
# #         trans_res = azure_services.translate_text(text, [lang_code])
# #         if not trans_res.get('error') and trans_res.get(lang_code):
# #             trans_txt = trans_res[lang_code]; trans_lang_name = lang_code 
# #             logger.info(f"Translated '{text}' to '{trans_txt}' ({lang_code}) for {user}")
# #         else: logger.warning(f"Translate fail for {user}: {trans_res.get('error')}")
# #     payload = {'user':user, 'text':trans_txt, 
# #                'original_text': orig_txt if trans_txt.lower()!=orig_txt.lower() else None,
# #                'original_lang_name': orig_lang_name if trans_txt.lower()!=orig_txt.lower() else None, 
# #                'translated_to_lang_name': trans_lang_name, 'timestamp':datetime.now(timezone.utc).isoformat(), 'room':room}
# #     emit('chat_message', payload, to=room)

# # @socketio.on('typing')
# # def on_typing_socket(data): emit('typing', data, to=data.get('room','general'), include_self=False)

# # @socketio.on('stop_typing')
# # def on_stop_typing_socket(data): emit('stop_typing', data, to=data.get('room','general'), include_self=False)

# # @socketio.on('disconnect')
# # def handle_socket_disconnect_event(): logger.info(f"Socket.IO Client disconnected: SID {request.sid}")


# # @app.route('/api/get-speech-token', methods=['GET'])
# # @login_required
# # def get_speech_token_route():
# #     creds = azure_services.get_speech_token()
# #     if 'error' in creds: return jsonify(creds), 503
# #     return jsonify(creds)

# # @app.errorhandler(400)
# # def bad_request_error_handler(e): 
# #     msg = str(e.description if hasattr(e, 'description') else e)
# #     logger.warning(f"400: {msg} for {request.url}")
# #     if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html: return jsonify(status="error",error="Bad Request",message=msg),400
# #     return render_template('400.html', error=e),400 

# # @app.errorhandler(404)
# # def page_not_found_error_handler(e): 
# #     msg = str(e.description if hasattr(e, 'description') else e)
# #     logger.warning(f"404: {request.path} - {msg}")
# #     if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html: return jsonify(status="error",error="Not Found",message=msg),404
# #     return render_template('404.html', error=e),404

# # @app.errorhandler(415)
# # def unsupported_media_type_error_handler(e):
# #     msg = str(e.description if hasattr(e, 'description') else e)
# #     logger.warning(f"415: {msg} for {request.url}")
# #     if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html: return jsonify(status="error",error="Unsupported Media Type",message=msg),415
# #     return render_template('500.html',error_code=415,error_message="Unsupported Media Type",error_detail=msg),415

# # @app.errorhandler(500)
# # def internal_server_error_handler_page(e): 
# #     logger.error(f"500: {e} for {request.url}", exc_info=sys.exc_info()); db.session.rollback()
# #     if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html: return jsonify(status="error",error="Internal Server Error",message="Unexpected server error."),500
# #     return render_template('500.html', error=e),500


# # if __name__ == '__main__':
# #     logger.info("Starting Flask-SocketIO development server with eventlet...")
# #     try:
# #         socketio.run(app, debug=app.debug, host='0.0.0.0', port=5000)
# #     except KeyboardInterrupt: 
# #         logger.info("Application shutting down via KeyboardInterrupt...")
# #     except Exception as e: 
# #         logger.critical(f"Failed to start application: {e}", exc_info=True)




# # """
# # Main Flask Application
# # """
# import os
# import sys
# import logging
# import uuid
# import json
# import io 
# from datetime import datetime, timezone 
# from werkzeug.utils import secure_filename
# from werkzeug.security import generate_password_hash, check_password_hash
# import eventlet
# eventlet.monkey_patch()

# from typing import Optional, Dict, List, Any, Tuple

# from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, abort
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
# from flask_socketio import SocketIO, emit, join_room, leave_room

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(pathname)s:%(lineno)d]')
# logger = logging.getLogger(__name__)

# app = Flask(__name__)

# # --- Application Configuration ---
# base_dir = os.path.abspath(os.path.dirname(__file__))
# from dotenv import load_dotenv
# dotenv_path = os.path.join(base_dir, '.env')
# if os.path.exists(dotenv_path):
#     logger.info(f"Attempting to load .env file from: {dotenv_path}")
#     load_dotenv(dotenv_path=dotenv_path)
#     logger.info(".env file loaded successfully.")
# else:
#     logger.warning(f".env file not found at: {dotenv_path}.")

# app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-please-change-ASAP')
# if app.config['SECRET_KEY'] == 'dev-secret-key-please-change-ASAP' and not app.debug:
#     logger.critical("CRITICAL: Using default FLASK_SECRET_KEY in a non-debug environment. THIS IS HIGHLY INSECURE. SET A STRONG, UNIQUE KEY IN YOUR .env FILE.")

# instance_folder_path = os.path.join(base_dir, 'instance')
# os.makedirs(instance_folder_path, exist_ok=True)

# default_db_filename = "toolkit_v4_2.db" 
# db_path_from_env = os.environ.get('DATABASE_URL', f'sqlite:///{default_db_filename}')
# logger.info(f"DATABASE_URL from environment (or default): {db_path_from_env}")
# if db_path_from_env.startswith('sqlite:///'):
#     db_file_part = db_path_from_env[len('sqlite:///'):]
#     if os.path.isabs(db_file_part): absolute_db_path = db_file_part
#     elif db_file_part.startswith('instance/'): absolute_db_path = os.path.join(base_dir, db_file_part)
#     else: absolute_db_path = os.path.join(instance_folder_path, db_file_part)
#     db_dir = os.path.dirname(absolute_db_path)
#     if not os.path.exists(db_dir): os.makedirs(db_dir, exist_ok=True)
#     app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{absolute_db_path.replace(os.sep, "/")}'
# else:
#     app.config['SQLALCHEMY_DATABASE_URI'] = db_path_from_env
# logger.info(f"Final SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# upload_folder_name = os.environ.get('UPLOAD_FOLDER_NAME', 'uploads')
# upload_folder_path = os.path.join(base_dir, upload_folder_name)
# app.config['UPLOAD_FOLDER'] = upload_folder_path
# max_content_length_str = os.environ.get('MAX_CONTENT_LENGTH', '16777216')
# if '#' in max_content_length_str: max_content_length_str = max_content_length_str.split('#')[0].strip()
# app.config['MAX_CONTENT_LENGTH'] = int(max_content_length_str)
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# logger.info(f"Ensured uploads folder exists at: {app.config['UPLOAD_FOLDER']}")

# logger.info(f"TRANSLATOR_SUBSCRIPTION_KEY: {os.environ.get('TRANSLATOR_SUBSCRIPTION_KEY', 'Not set')[:5]}...")
# logger.info(f"LANGUAGE_SUBSCRIPTION_KEY: {os.environ.get('LANGUAGE_SUBSCRIPTION_KEY', 'Not set')[:5]}...")
# logger.info(f"SPEECH_SUBSCRIPTION_KEY: {os.environ.get('SPEECH_SUBSCRIPTION_KEY', 'Not set')[:5]}...")
# logger.info(f"VISION_SUBSCRIPTION_KEY: {os.environ.get('VISION_SUBSCRIPTION_KEY', 'Not set')[:5]}...")

# db = SQLAlchemy(app)
# login_manager = LoginManager(app)
# login_manager.login_view = 'login'
# login_manager.login_message_category = 'info'

# try:
#     from azure_services import azure_services, VisualFeatureTypes 
#     import document_qa
#     document_qa.init_document_qa(app.config['UPLOAD_FOLDER']) 
# except ImportError as e:
#     logger.critical(f"Failed to import core modules (azure_services, document_qa): {e}", exc_info=True)
#     sys.exit("Application cannot start due to missing core modules.")


# try:
#     import nltk
#     nltk.data.find('tokenizers/punkt'); nltk.data.find('corpora/stopwords')
# except LookupError as e:
#     resource_name = str(e).split("'")[1] if "'" in str(e) else "nltk_resource"
#     logger.warning(f"NLTK resource '{resource_name}' missing. Downloading...")
#     try: nltk.download(resource_name, quiet=True); logger.info(f"NLTK resource '{resource_name}' downloaded.")
#     except Exception as de: logger.error(f"Failed to download NLTK '{resource_name}': {de}")

# class User(UserMixin, db.Model):
#     __tablename__ = 'user'
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     password_hash = db.Column(db.String(256), nullable=False) 
#     summaries = db.relationship('Summary', backref='user', lazy='dynamic', cascade="all, delete-orphan")
#     def set_password(self, password): self.password_hash = generate_password_hash(password)
#     def check_password(self, password): return check_password_hash(self.password_hash, password)

# class Summary(db.Model):
#     __tablename__ = 'summary'
#     id = db.Column(db.Integer, primary_key=True)
#     input_type = db.Column(db.String(50), nullable=False)
#     action_type = db.Column(db.String(50), nullable=False)
#     original_content_preview = db.Column(db.Text, nullable=True)
#     processed_content = db.Column(db.JSON, nullable=True)
#     details_json = db.Column(db.JSON, nullable=True) 
#     timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
#     def to_dict(self):
#         return {'id': self.id, 'input_type': self.input_type, 'action_type': self.action_type,
#                 'original_content_preview': self.original_content_preview,
#                 'processed_content': self.processed_content, 'details_json': self.details_json,
#                 'timestamp': self.timestamp.isoformat() if self.timestamp else None, 'user_id': self.user_id}
# try:
#     with app.app_context(): 
#         db.create_all()
#         if not User.query.filter_by(username="testuser").first():
#             test_user = User(username="testuser"); test_user.set_password("password")
#             db.session.add(test_user); db.session.commit()
#             logger.info("Test user 'testuser' created.")
# except Exception as e: logger.error(f"DB init error: {e}", exc_info=True)

# @login_manager.user_loader
# def load_user(user_id: str) -> Optional[User]:
#     try: return db.session.get(User, int(user_id)) 
#     except Exception as e: logger.error(f"Failed to load user by ID: {user_id}", exc_info=True); return None

# @app.context_processor
# def inject_current_year(): return {'current_year': datetime.now(timezone.utc).year}

# def save_processing_result(input_type:str, action_type:str, original_preview:Optional[str], 
#                            processed_data:Dict[str,Any], request_details:Optional[Dict[str,Any]]=None) -> Optional[int]:
#     if current_user.is_authenticated:
#         try:
#             max_preview_len = 1000 
#             if original_preview and len(original_preview) > max_preview_len:
#                 original_preview = original_preview[:max_preview_len] + "..."

#             entry = Summary(user_id=current_user.id, input_type=input_type, action_type=action_type,
#                             original_content_preview=original_preview, processed_content=processed_data,
#                             details_json=request_details, timestamp=datetime.now(timezone.utc))
#             db.session.add(entry); db.session.commit(); 
#             logger.info(f"Saved processing result for user {current_user.id}, action {action_type}, summary ID {entry.id}")
#             return entry.id
#         except Exception as e: 
#             db.session.rollback()
#             logger.error(f"DB save error for user {current_user.id}, action {action_type}: {e}", exc_info=True)
#     return None

# def allowed_file(filename:Optional[str], exts:set) -> bool: 
#     return filename is not None and '.' in filename and filename.rsplit('.',1)[1].lower() in exts

# def get_text_from_request_data(request_form_data: Dict[str, Any], request_files_data) -> Tuple[Optional[str], Optional[str], Optional[str]]:
#     text_content = request_form_data.get('text') 
#     original_filename = None
#     error_message = None

#     if text_content:
#         logger.debug("Helper: Using direct text from request form data.")
#         return text_content, None, None 

#     file_key_for_pdf_extraction = 'pdf_file' 
    
#     if file_key_for_pdf_extraction in request_files_data:
#         pdf_file_storage = request_files_data[file_key_for_pdf_extraction]
#         if pdf_file_storage and pdf_file_storage.filename:
#             original_filename = secure_filename(pdf_file_storage.filename)
#             logger.info(f"Helper: Processing PDF '{original_filename}' via key '{file_key_for_pdf_extraction}'.")
#             if not allowed_file(original_filename, {'pdf'}):
#                 return None, "Invalid PDF file type for text extraction. Only .pdf is allowed.", original_filename
            
#             upload_folder_abs = app.config.get('UPLOAD_FOLDER')
#             if not upload_folder_abs or not os.path.isabs(upload_folder_abs):
#                 logger.error(f"UPLOAD_FOLDER '{upload_folder_abs}' is not absolute or not configured. Cannot save temp PDF.")
#                 return None, "Server configuration error for file uploads.", original_filename

#             temp_dir = os.path.join(upload_folder_abs, 'temp_pdf_extraction_api_v4_1')
#             try:
#                 os.makedirs(temp_dir, exist_ok=True)
#             except OSError as e:
#                 logger.error(f"Helper: Could not create temp directory {temp_dir}: {e}", exc_info=True)
#                 return None, f"Server error creating temp directory for PDF: {str(e)}", original_filename

#             temp_pdf_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{original_filename}")
            
#             try:
#                 pdf_file_storage.save(temp_pdf_path)
#                 logger.info(f"Helper: Temporarily saved PDF for extraction: {temp_pdf_path}")
#                 text_content = document_qa.extract_text_from_document(temp_pdf_path) 
#                 if not text_content or not text_content.strip():
#                     error_message = "Could not extract meaningful text from the PDF. It might be image-based, empty, or protected."
#                     logger.warning(f"Helper: No meaningful text extracted from PDF: {original_filename}")
#                 else:
#                     logger.info(f"Helper: Successfully extracted {len(text_content)} chars from PDF: {original_filename}")
#             except Exception as e:
#                 logger.error(f"Helper: Error during PDF text extraction for '{original_filename}': {e}", exc_info=True)
#                 error_message = f"Server error during PDF text extraction: {str(e)}"
#             finally:
#                 if os.path.exists(temp_pdf_path):
#                     try: os.remove(temp_pdf_path); logger.debug(f"Helper: Removed temp PDF: {temp_pdf_path}")
#                     except Exception as e_rem: logger.error(f"Helper: Error removing temp PDF {temp_pdf_path}: {e_rem}")
#             return text_content, error_message, original_filename
#         else:
#             logger.warning(f"Helper: '{file_key_for_pdf_extraction}' in request.files but it's invalid or has no filename.")
#             return None, f"A PDF file via '{file_key_for_pdf_extraction}' was expected but not properly provided.", None
            
#     logger.debug("Helper: No direct text or 'pdf_file' found in request for text extraction.")
#     return None, "No text or PDF file ('pdf_file') found in the request for text extraction.", None

# @app.route('/')
# def index(): 
#     try:
#         return render_template('index.html')
#     except Exception as e:
#         logger.error(f"Error rendering index.html: {e}", exc_info=True)
#         return render_template('500.html', error_message="Error rendering homepage template.", error_detail=str(e)), 500

# @app.route('/about')
# def about(): return render_template('about.html')

# @app.route('/image-analyzer-page')
# @login_required
# def image_analyzer_page(): return render_template('image_analyzer.html')

# @app.route('/live-chat-page')
# @login_required
# def live_chat_page(): return render_template('live_chat.html')

# @app.route('/doc-qa-page')
# @login_required
# def doc_qa_page(): 
#     try:
#         return render_template('doc_qa.html')
#     except Exception as e:
#         logger.error(f"Error rendering doc_qa.html: {e}", exc_info=True)
#         abort(500) 

# @app.route('/my-summaries')
# @login_required
# def my_summaries():
#     page = request.args.get('page', 1, type=int); per_page = 10 
#     summaries_pagination_obj = db.session.query(Summary).filter_by(user_id=current_user.id)\
#         .order_by(Summary.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
#     summaries_list_for_json = []
#     if summaries_pagination_obj:
#         summaries_list_for_json = [s.to_dict() for s in summaries_pagination_obj.items]
    
#     try: 
#         summaries_json_str = json.dumps(summaries_list_for_json)
#     except TypeError as e: 
#         logger.error(f"Error serializing summaries for my_summaries page: {e}", exc_info=True)
#         summaries_json_str = "[]" 

#     return render_template('my_summaries.html', summaries=summaries_pagination_obj, summaries_json=summaries_json_str)

# @app.route('/login', methods=['GET', 'POST'])
# def login(): 
#     if current_user.is_authenticated: return redirect(url_for('index'))
#     if request.method == 'POST':
#         username = request.form.get('username'); password = request.form.get('password')
#         user = User.query.filter_by(username=username).first()
#         if user and user.check_password(password):
#             login_user(user, remember=request.form.get('remember') == 'on')
#             next_page = request.args.get('next')
#             if not next_page or not next_page.startswith('/'): next_page = url_for('index')
#             flash('Logged in successfully!', 'success'); return redirect(next_page)
#         else: flash('Invalid username or password. Please try again.', 'danger')
#     return render_template('login.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register(): 
#     if current_user.is_authenticated: return redirect(url_for('index'))
#     if request.method == 'POST':
#         username = request.form.get('username'); password = request.form.get('password')
#         if not username or not password: flash('Username and password are required.', 'warning'); return redirect(url_for('register'))
#         if User.query.filter_by(username=username).first(): flash('Username already exists.', 'warning'); return redirect(url_for('register'))
#         new_user = User(username=username); new_user.set_password(password)
#         try: 
#             db.session.add(new_user); db.session.commit()
#             flash('Registration successful! Please log in.', 'success'); return redirect(url_for('login'))
#         except Exception as e: 
#             db.session.rollback()
#             logger.error(f"Reg error {username}: {e}", exc_info=True)
#             flash('An error occurred during registration. Please try again.', 'danger')
#     return render_template('register.html')

# @app.route('/logout')
# @login_required
# def logout(): logout_user(); flash('You have been logged out.', 'info'); return redirect(url_for('index'))

# @app.route('/api/translate', methods=['POST'])
# @login_required 
# def translate_text_api(): 
#     text_to_process = None; original_filename = None; error_msg = None
#     data_source_params = {} 
#     logger.debug(f"Translate API: Received request. Content-Type: {request.content_type}")

#     if request.content_type and request.content_type.startswith('application/json'):
#         data_source_params = request.get_json()
#         if not data_source_params: return jsonify({"status": "error", "error": "Invalid JSON request."}), 400
#         text_to_process = data_source_params.get('text')
#     elif request.content_type and request.content_type.startswith('multipart/form-data'):
#         text_to_process, error_msg, original_filename = get_text_from_request_data(request.form, request.files)
#         data_source_params = request.form.to_dict() 
#     else:
#         return jsonify({"status": "error", "error": "Unsupported content type. Must be JSON or FormData."}), 415

#     if error_msg: return jsonify({"status": "error", "error": error_msg, "processed_filename": original_filename}), 400
#     if not text_to_process: return jsonify({"status": "error", "error": "Missing text to translate after attempting extraction."}), 400

#     targets_from_form = data_source_params.get('target_languages') or request.form.getlist('targetLanguages[]') 
#     targets = []
#     if isinstance(targets_from_form, str):
#         try: targets = json.loads(targets_from_form)
#         except json.JSONDecodeError: 
#             logger.warning(f"Could not parse target_languages string from form data: {targets_from_form}. Assuming single language if not list-like.")
#             targets = [targets_from_form] if targets_from_form else []
#     elif isinstance(targets_from_form, list): 
#         targets = targets_from_form
    
#     if not targets : return jsonify({"status": "error", "error": "Missing 'target_languages'"}), 400
    
#     source = data_source_params.get('source_language') or data_source_params.get('sourceLanguageClient')

#     results = azure_services.translate_text(text_to_process, targets, source)
#     if 'error' in results: 
#         return jsonify({"status": "error", "error": results['error']}), 500
    
#     preview = original_filename if original_filename else text_to_process[:500]
#     save_processing_result('pdf' if original_filename else 'text', 'translate', preview, 
#                            {"translations": results}, 
#                            {"target_languages": targets, "source_language": source})
#     return jsonify({"status": "success", "translations": results, 
#                     "original_text_processed": text_to_process if not original_filename else None, 
#                     "processed_filename": original_filename})

# @app.route('/api/analyze-sentiment', methods=['POST'])
# @login_required
# def analyze_sentiment_api():
#     text_to_process = None; original_filename = None; error_msg = None
#     if request.content_type and request.content_type.startswith('application/json'):
#         data = request.get_json(); text_to_process = data.get('text')
#         if not data: return jsonify({"status": "error", "error": "Invalid JSON request."}), 400
#     elif request.content_type and request.content_type.startswith('multipart/form-data'):
#         text_to_process, error_msg, original_filename = get_text_from_request_data(request.form, request.files)
#     else: return jsonify({"status": "error", "error": "Unsupported content type."}), 415

#     if error_msg: return jsonify({"status": "error", "error": error_msg, "processed_filename": original_filename}), 400
#     if not text_to_process: return jsonify({"status": "error", "error": "Missing text for sentiment analysis."}), 400
        
#     result = azure_services.analyze_sentiment(text_to_process)
#     if 'error' in result: return jsonify({"status": "error", "error": result['error']}), 500
    
#     preview = original_filename if original_filename else text_to_process[:500]
#     save_processing_result('pdf' if original_filename else 'text', 'sentiment', preview, 
#                            {"sentiment_analysis": result}) 
#     return jsonify({"status": "success", "sentiment_analysis": result, "original_text_processed": text_to_process if not original_filename else None, "processed_filename": original_filename})

# @app.route('/api/summarize', methods=['POST'])
# @login_required
# def summarize_api(): 
#     text_to_process = None; original_filename = None; error_msg = None
#     data_source_params = {} 
#     if request.content_type and request.content_type.startswith('application/json'):
#         data_source_params = request.get_json()
#         if not data_source_params: return jsonify({"status": "error", "error": "Invalid JSON request."}), 400
#         text_to_process = data_source_params.get('text')
#     elif request.content_type and request.content_type.startswith('multipart/form-data'):
#         text_to_process, error_msg, original_filename = get_text_from_request_data(request.form, request.files)
#         data_source_params = request.form.to_dict()
#     else: return jsonify({"status": "error", "error": "Unsupported content type."}), 415

#     if error_msg: return jsonify({"status": "error", "error": error_msg, "processed_filename": original_filename}), 400
#     if not text_to_process: return jsonify({"status": "error", "error": "Missing text for summarization."}), 400

#     s_type = data_source_params.get('type', 'extractive')
#     s_count_str = data_source_params.get('sentence_count') or data_source_params.get('sentenceCountClient', '3')
#     try: s_count = int(s_count_str)
#     except (ValueError, TypeError): return jsonify({"status":"error", "error": "Invalid sentence_count format."}), 400
#     if s_type not in ['extractive', 'abstractive']: return jsonify({"status": "error", "error": "Invalid summary type"}), 400
    
#     result = azure_services.extractive_summarize(text_to_process, s_count) if s_type == 'extractive' else azure_services.abstractive_summarize(text_to_process, s_count)
#     if 'error' in result: return jsonify({"status": "error", "error": result['error']}), 500
    
#     preview = original_filename if original_filename else text_to_process[:500]
#     save_processing_result('pdf' if original_filename else 'text_summary', f'{s_type}_summary', preview, 
#                            {"summary_data": result}, 
#                            {"type": s_type, "sentence_count": s_count})
#     return jsonify({"status": "success", "summary_data": result, "original_text_processed": text_to_process if not original_filename else None, "processed_filename": original_filename})

# @app.route('/api/analyze-image', methods=['POST'])
# @login_required
# def analyze_image_api(): 
#     if 'imageFile' not in request.files: return jsonify({"status": "error", "error": "No 'imageFile' part"}), 400
#     image_file = request.files['imageFile']
#     if image_file.filename == '': return jsonify({"status": "error", "error": "No image selected"}), 400
    
#     feature_map_client_to_sdk = {
#         "description": VisualFeatureTypes.description, "tags": VisualFeatureTypes.tags,
#         "objects": VisualFeatureTypes.objects, "faces": VisualFeatureTypes.faces,
#         "adult": VisualFeatureTypes.adult, "brands": VisualFeatureTypes.brands,
#         "categories": VisualFeatureTypes.categories, "color": VisualFeatureTypes.color
#     }
#     selected_sdk_features: List[VisualFeatureTypes] = [] 
#     form_features_names: List[str] = [] 
#     for feature_key_form, sdk_feature_enum in feature_map_client_to_sdk.items():
#         if request.form.get(feature_key_form) == 'true': 
#             if sdk_feature_enum: 
#                 selected_sdk_features.append(sdk_feature_enum)
#             form_features_names.append(feature_key_form)
            
#     if not selected_sdk_features:
#          return jsonify({"status": "error", "error": "No analysis features selected or VisualFeatureTypes not available"}), 400
        
#     if image_file and allowed_file(image_file.filename, {'png', 'jpg', 'jpeg', 'gif', 'bmp'}):
#         filename = secure_filename(image_file.filename)
#         temp_filename = f"{uuid.uuid4()}_{filename}" 
#         temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_images')
#         os.makedirs(temp_dir, exist_ok=True)
#         temp_path = os.path.join(temp_dir, temp_filename)
#         try:
#             image_file.save(temp_path)
#             analysis_result = azure_services.analyze_image(temp_path, visual_features_enums=selected_sdk_features)
#         finally:
#             if os.path.exists(temp_path): os.remove(temp_path)
#         if 'error' in analysis_result: return jsonify({"status": "error", "error": analysis_result['error']}), 500
#         save_processing_result('image', 'vision_analysis', filename, 
#                                {"analysis": analysis_result}, 
#                                {"features_requested": form_features_names})
#         return jsonify({"status": "success", "analysis": analysis_result, "filename": filename})
#     else: return jsonify({"status": "error", "error": "Invalid image file type"}), 400

# @app.route('/api/youtube-transcript', methods=['POST'])
# @login_required
# def youtube_transcript_api_route(): 
#     if not request.is_json: return jsonify({"status": "error", "error": "Request must be JSON"}), 415
#     data = request.get_json(); url = data.get('url')
#     if not url: return jsonify({"status": "error", "error": "Missing 'url'"}), 400
#     from background_tasks import youtube_transcript 
#     task = youtube_transcript.apply_async(args=[url]) 
#     try: result = task.get(timeout=120) 
#     except Exception as e: logger.error(f"YT task error: {e}"); return jsonify({"status":"error", "error": str(e)}), 500
#     if result.get('status') == 'error': return jsonify(result), result.get('http_status_code', 400) 
#     save_processing_result('youtube', 'transcript', url, 
#                            {"transcript": result}, 
#                            {"url": url})
#     return jsonify({"status": "success", "transcript": result})


# @app.route('/api/transcribe-audio', methods=['POST'])
# @login_required
# def transcribe_audio_route(): 
#     if 'audio' not in request.files: return jsonify({"status": "error", "error": "No audio file part"}), 400
#     audio_f = request.files['audio']; lang = request.form.get('language') 
#     if audio_f.filename == '': return jsonify({"status": "error", "error": "No audio selected"}), 400
#     if audio_f and allowed_file(audio_f.filename, {'wav', 'mp3', 'ogg', 'flac', 'm4a'}): 
#         fname = secure_filename(audio_f.filename)
#         tmp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_audio'); os.makedirs(tmp_dir, exist_ok=True)
#         fpath = os.path.join(tmp_dir, f"{uuid.uuid4()}_{fname}")
#         try:
#             audio_f.save(fpath); from background_tasks import transcribe_audio
#             task = transcribe_audio.apply_async(args=[fpath, lang])
#             result = task.get(timeout=600) 
#         finally:
#             if os.path.exists(fpath): os.remove(fpath)
#         if 'error' in result: return jsonify(result), result.get('http_status_code', 400)
#         save_processing_result('audio', 'transcribe_audio', fname, 
#                                {"transcription": result}, 
#                                {"language": lang})
#         return jsonify({"status": "success", "transcription": result})
#     else: return jsonify({"status": "error", "error": "Invalid audio file type"}), 400

# @app.route('/api/get-user-documents', methods=['GET'])
# @login_required
# def get_user_documents_route(): 
#     try:
#         docs = document_qa.get_user_documents(current_user.id)
#         return jsonify({"status": "success", "documents": docs})
#     except Exception as e: 
#         logger.error(f"Error fetching documents for user {current_user.id}: {e}", exc_info=True)
#         return jsonify({"status": "error", "error": "Could not retrieve documents."}), 500

# @app.route('/api/document-qa', methods=['POST']) 
# @login_required
# def upload_document_for_qa_api(): 
#     if 'document' not in request.files: return jsonify({"status": "error", "error": "No 'document' file part in request"}), 400
#     doc_file = request.files['document']
#     if doc_file.filename == '': return jsonify({"status": "error", "error": "No document selected for upload"}), 400
#     if not allowed_file(doc_file.filename, {'pdf', 'txt', 'docx'}): 
#         return jsonify({"status": "error", "error": "Invalid document format. Allowed: pdf, txt, docx"}), 400
    
#     filename = secure_filename(doc_file.filename)
#     temp_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_doc_uploads')
#     os.makedirs(temp_upload_dir, exist_ok=True)
#     temp_upload_path = os.path.join(temp_upload_dir, f"temp_docqa_upload_{uuid.uuid4()}_{filename}")
    
#     try:
#         doc_file.save(temp_upload_path)
#         file_size = os.path.getsize(temp_upload_path)
#         doc_id = document_qa.add_document(temp_upload_path, current_user.id, file_size)
#     except Exception as e:
#         logger.error(f"Document upload and initial processing error for QA: {e}", exc_info=True)
#         return jsonify({"status": "error", "error": "Server error during document processing for QA."}), 500
#     finally:
#         if os.path.exists(temp_upload_path):
#             try: os.remove(temp_upload_path)
#             except Exception as e_rem: logger.error(f"Error removing temp QA upload {temp_upload_path}: {e_rem}")

#     if not doc_id: return jsonify({"status": "error", "error": "Failed to add document to QA system after processing."}), 500
    
#     save_processing_result(input_type='document_upload', action_type='doc_upload_qa', 
#                            original_preview=filename, 
#                            processed_data={"doc_id": doc_id, "filename": filename, "size": file_size})
#     return jsonify({"status": "success", "message": "Document uploaded successfully for Q&A.", "doc_id": doc_id, "filename": filename, "size": file_size}), 201

# @app.route('/api/document/<string:document_id>/ask', methods=['POST'])
# @login_required
# def api_document_ask_route(document_id): 
#     if not request.is_json: return jsonify({"status": "error", "error": "Request must be JSON"}), 415
#     data = request.get_json(); question = data.get('question')
#     if not question: return jsonify({"status": "error", "error": "Question missing"}), 400
        
#     ans_data = document_qa.query_document(document_id, question, user_id_for_auth=current_user.id) 
#     if 'error' in ans_data: 
#         status_code = 404 if "not found" in ans_data['error'].lower() or "access denied" in ans_data['error'].lower() else 500
#         return jsonify({"status": "error", "error": ans_data['error']}), status_code
    
#     doc_meta = document_qa.get_document_metadata(document_id)
#     doc_name_preview = doc_meta.get('file_name', f"DocID:{document_id}") if doc_meta else f"DocID:{document_id}"
    
#     save_processing_result(input_type='document_qa', action_type='question_answer', 
#                            original_preview=f"{doc_name_preview} - Q: {question[:100]}", 
#                            processed_data={"answer_data": ans_data}, 
#                            request_details={"document_id": document_id, "question": question})
#     return jsonify({"status": "success", **ans_data}) 

# @app.route('/api/document/<string:document_id>', methods=['DELETE'])
# @login_required
# def api_document_delete_route(document_id): 
#     if document_qa.delete_document(document_id, current_user.id): 
#         return jsonify({"status": "success", "message": "Document deleted successfully."})
#     else: 
#         return jsonify({"status": "error", "error": "Delete failed. Document not found or access denied."}), 404


# socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*", logger=True, engineio_logger=True)

# @socketio.on('connect')
# def handle_connect_socket(): 
#     logger.info(f"Socket.IO Client connected: SID {request.sid}")

# @socketio.on('join_room')
# def on_join_room(data: Dict[str, str]):
#     username = data.get('user', 'AnonymousUser'); room = data.get('room', 'default_room')
#     join_room(room); 
#     logger.info(f"User {username} (SID:{request.sid}) joined room: {room}")
#     emit('user_joined', {'user': username, 'room': room}, to=room)

# @socketio.on('leave_room')
# def on_leave_room(data: Dict[str, str]):
#     username = data.get('user', 'AnonymousUser'); room = data.get('room', 'default_room')
#     leave_room(room); 
#     logger.info(f"User {username} (SID:{request.sid}) left room: {room}")
#     emit('user_left', {'user': username, 'room': room}, to=room, include_self=False)

# @socketio.on('text_message')
# def handle_chat_text_message(data: Dict[str, Any]):
#     room = data.get('room', 'default_room')
#     user = data.get('user', 'AnonymousUser')
#     original_text = data.get('text', '') # This is the text from client (e.g., recognized speech)
#     target_lang_code = data.get('translate_to')

#     logger.info(f"Received message from {user} in {room}: '{original_text}', Translate To: {target_lang_code}")

#     text_to_display = original_text
#     original_text_if_translated = None # Will hold original if translation occurs
#     translated_lang_name_for_payload = None

#     if target_lang_code and target_lang_code.strip() != "":
#         logger.info(f"Attempting translation for '{original_text}' to '{target_lang_code}' for user {user}")
#         translation_result = azure_services.translate_text(original_text, [target_lang_code])
        
#         # Check if translation was successful and a result for the target language exists
#         if not translation_result.get('error') and translation_result.get(target_lang_code):
#             translated_text = translation_result.get(target_lang_code)
#             if translated_text and translated_text.strip().lower() != original_text.strip().lower():
#                 text_to_display = translated_text
#                 original_text_if_translated = original_text # Store the original text
#                 translated_lang_name_for_payload = target_lang_code
#                 logger.info(f"Successfully translated '{original_text}' to '{text_to_display}' ({target_lang_code}) for user {user}")
#             else:
#                 # Translation resulted in the same text or was empty, or target lang not in result
#                 logger.warning(f"Translation to '{target_lang_code}' resulted in same/empty text or key missing. Original: '{original_text}', Result: '{translation_result}'. Using original.")
#                 # text_to_display remains original_text
#         else:
#             logger.warning(f"Translation failed for user {user}: {translation_result.get('error', 'Unknown translation error')}")
#             # text_to_display remains original_text
    
#     payload = {
#         'user': user,
#         'text': text_to_display, # This is the main text to be shown in the bubble
#         'original_text': original_text_if_translated, # This is non-null only if translation happened AND was different
#         'original_lang_name': "Original" if original_text_if_translated else None,
#         'translated_to_lang_name': translated_lang_name_for_payload,
#         'timestamp': datetime.now(timezone.utc).isoformat(),
#         'room': room
#     }
    
#     logger.debug(f"Emitting chat_message payload: {json.dumps(payload)}")
#     emit('chat_message', payload, to=room)


# @socketio.on('typing')
# def on_typing_socket(data: Dict[str, str]): emit('typing', data, to=data.get('room','default_room'), include_self=False)

# @socketio.on('stop_typing')
# def on_stop_typing_socket(data: Dict[str, str]): emit('stop_typing', data, to=data.get('room','default_room'), include_self=False)

# @socketio.on('disconnect')
# def handle_socket_disconnect_event(): 
#     logger.info(f"Socket.IO Client disconnected: SID {request.sid}")


# @app.route('/api/get-speech-token', methods=['GET'])
# @login_required
# def get_speech_token_route():
#     creds = azure_services.get_speech_token()
#     if 'error' in creds: return jsonify(creds), 503 
#     return jsonify(creds)

# @app.errorhandler(400)
# def bad_request_error_handler(e): 
#     msg = str(e.description if hasattr(e, 'description') and e.description else e)
#     logger.warning(f"400 Bad Request: {msg} for URL {request.url}", exc_info=True)
#     if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html: 
#         return jsonify(status="error",error="Bad Request",message=msg),400
#     return render_template('400.html', error_message=msg, error_detail=msg),400 

# @app.errorhandler(404)
# def page_not_found_error_handler(e): 
#     msg = str(e.description if hasattr(e, 'description') and e.description else e)
#     logger.warning(f"404 Not Found: {request.path} - {msg}")
#     if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html: 
#         return jsonify(status="error",error="Not Found",message=msg),404
#     return render_template('404.html', error_message=msg),404

# @app.errorhandler(415)
# def unsupported_media_type_error_handler(e):
#     msg = str(e.description if hasattr(e, 'description') and e.description else e)
#     logger.warning(f"415 Unsupported Media Type: {msg} for URL {request.url}")
#     if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html: 
#         return jsonify(status="error",error="Unsupported Media Type",message=msg),415
#     return render_template('500.html',error_code=415,error_message="Unsupported Media Type",error_detail=msg),415

# @app.errorhandler(500)
# def internal_server_error_handler_page(e): 
#     original_exception = getattr(e, "original_exception", e)
#     logger.error(f"500 Internal Server Error: {original_exception} for URL {request.url}", exc_info=sys.exc_info())
#     db.session.rollback() 
#     if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html: 
#         return jsonify(status="error",error="Internal Server Error",message="An unexpected server error occurred."),500
#     return render_template('500.html', error_message="Internal Server Error", error_detail=str(original_exception)),500


# if __name__ == '__main__':
#     logger.info("Starting Flask-SocketIO development server with eventlet...")
#     try:
#         socketio.run(app, debug=app.debug, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), use_reloader=app.debug)
#     except KeyboardInterrupt: 
#         logger.info("Application shutting down via KeyboardInterrupt...")
#     except Exception as e: 
#         logger.critical(f"Failed to start application: {e}", exc_info=True)

# """
# Main Flask Application
# """
import os
import sys
import logging
import uuid
import json
import io 
from datetime import datetime, timezone 
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import eventlet
eventlet.monkey_patch()

from typing import Optional, Dict, List, Any, Tuple

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(pathname)s:%(lineno)d]')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- Application Configuration ---
base_dir = os.path.abspath(os.path.dirname(__file__))
from dotenv import load_dotenv
dotenv_path = os.path.join(base_dir, '.env')
if os.path.exists(dotenv_path):
    logger.info(f"Attempting to load .env file from: {dotenv_path}")
    load_dotenv(dotenv_path=dotenv_path)
    logger.info(".env file loaded successfully.")
else:
    logger.warning(f".env file not found at: {dotenv_path}.")

app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-please-change-ASAP')
if app.config['SECRET_KEY'] == 'dev-secret-key-please-change-ASAP' and not app.debug:
    logger.critical("CRITICAL: Using default FLASK_SECRET_KEY in a non-debug environment. THIS IS HIGHLY INSECURE. SET A STRONG, UNIQUE KEY IN YOUR .env FILE.")

instance_folder_path = os.path.join(base_dir, 'instance')
os.makedirs(instance_folder_path, exist_ok=True)

default_db_filename = "toolkit_v4_2.db" 
db_path_from_env = os.environ.get('DATABASE_URL', f'sqlite:///{default_db_filename}')
logger.info(f"DATABASE_URL from environment (or default): {db_path_from_env}")
if db_path_from_env.startswith('sqlite:///'):
    db_file_part = db_path_from_env[len('sqlite:///'):]
    if os.path.isabs(db_file_part): absolute_db_path = db_file_part
    elif db_file_part.startswith('instance/'): absolute_db_path = os.path.join(base_dir, db_file_part)
    else: absolute_db_path = os.path.join(instance_folder_path, db_file_part)
    db_dir = os.path.dirname(absolute_db_path)
    if not os.path.exists(db_dir): os.makedirs(db_dir, exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{absolute_db_path.replace(os.sep, "/")}'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_path_from_env
logger.info(f"Final SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

upload_folder_name = os.environ.get('UPLOAD_FOLDER_NAME', 'uploads')
upload_folder_path = os.path.join(base_dir, upload_folder_name)
app.config['UPLOAD_FOLDER'] = upload_folder_path
max_content_length_str = os.environ.get('MAX_CONTENT_LENGTH', '16777216')
if '#' in max_content_length_str: max_content_length_str = max_content_length_str.split('#')[0].strip()
app.config['MAX_CONTENT_LENGTH'] = int(max_content_length_str)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
logger.info(f"Ensured uploads folder exists at: {app.config['UPLOAD_FOLDER']}")

logger.info(f"TRANSLATOR_SUBSCRIPTION_KEY: {os.environ.get('TRANSLATOR_SUBSCRIPTION_KEY', 'Not set')[:5]}...")
logger.info(f"LANGUAGE_SUBSCRIPTION_KEY: {os.environ.get('LANGUAGE_SUBSCRIPTION_KEY', 'Not set')[:5]}...")
logger.info(f"SPEECH_SUBSCRIPTION_KEY: {os.environ.get('SPEECH_SUBSCRIPTION_KEY', 'Not set')[:5]}...")
logger.info(f"VISION_SUBSCRIPTION_KEY: {os.environ.get('VISION_SUBSCRIPTION_KEY', 'Not set')[:5]}...")

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

try:
    from azure_services import azure_services, VisualFeatureTypes 
    import document_qa
    document_qa.init_document_qa(app.config['UPLOAD_FOLDER']) 
except ImportError as e:
    logger.critical(f"Failed to import core modules (azure_services, document_qa): {e}", exc_info=True)
    sys.exit("Application cannot start due to missing core modules.")


try:
    import nltk
    nltk.data.find('tokenizers/punkt'); nltk.data.find('corpora/stopwords')
except LookupError as e:
    resource_name = str(e).split("'")[1] if "'" in str(e) else "nltk_resource"
    logger.warning(f"NLTK resource '{resource_name}' missing. Downloading...")
    try: nltk.download(resource_name, quiet=True); logger.info(f"NLTK resource '{resource_name}' downloaded.")
    except Exception as de: logger.error(f"Failed to download NLTK '{resource_name}': {de}")

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False) 
    summaries = db.relationship('Summary', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)

class Summary(db.Model):
    __tablename__ = 'summary'
    id = db.Column(db.Integer, primary_key=True)
    input_type = db.Column(db.String(50), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)
    original_content_preview = db.Column(db.Text, nullable=True)
    processed_content = db.Column(db.JSON, nullable=True)
    details_json = db.Column(db.JSON, nullable=True) 
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    def to_dict(self):
        return {'id': self.id, 'input_type': self.input_type, 'action_type': self.action_type,
                'original_content_preview': self.original_content_preview,
                'processed_content': self.processed_content, 'details_json': self.details_json,
                'timestamp': self.timestamp.isoformat() if self.timestamp else None, 'user_id': self.user_id}
try:
    with app.app_context(): 
        db.create_all()
        if not User.query.filter_by(username="testuser").first():
            test_user = User(username="testuser"); test_user.set_password("password")
            db.session.add(test_user); db.session.commit()
            logger.info("Test user 'testuser' created.")
except Exception as e: logger.error(f"DB init error: {e}", exc_info=True)

@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    try: return db.session.get(User, int(user_id)) 
    except Exception as e: logger.error(f"Failed to load user by ID: {user_id}", exc_info=True); return None

@app.context_processor
def inject_current_year(): return {'current_year': datetime.now(timezone.utc).year}

def save_processing_result(input_type:str, action_type:str, original_preview:Optional[str], 
                           processed_data:Dict[str,Any], request_details:Optional[Dict[str,Any]]=None) -> Optional[int]:
    if current_user.is_authenticated:
        try:
            max_preview_len = 1000 
            if original_preview and len(original_preview) > max_preview_len:
                original_preview = original_preview[:max_preview_len] + "..."

            entry = Summary(user_id=current_user.id, input_type=input_type, action_type=action_type,
                            original_content_preview=original_preview, processed_content=processed_data,
                            details_json=request_details, timestamp=datetime.now(timezone.utc))
            db.session.add(entry); db.session.commit(); 
            logger.info(f"Saved processing result for user {current_user.id}, action {action_type}, summary ID {entry.id}")
            return entry.id
        except Exception as e: 
            db.session.rollback()
            logger.error(f"DB save error for user {current_user.id}, action {action_type}: {e}", exc_info=True)
    return None

def allowed_file(filename:Optional[str], exts:set) -> bool: 
    return filename is not None and '.' in filename and filename.rsplit('.',1)[1].lower() in exts

def get_text_from_request_data(request_form_data: Dict[str, Any], request_files_data) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    text_content = request_form_data.get('text') 
    original_filename = None
    error_message = None

    if text_content:
        logger.debug("Helper: Using direct text from request form data.")
        return text_content, None, None 

    file_key_for_pdf_extraction = 'pdf_file' 
    
    if file_key_for_pdf_extraction in request_files_data:
        pdf_file_storage = request_files_data[file_key_for_pdf_extraction]
        if pdf_file_storage and pdf_file_storage.filename:
            original_filename = secure_filename(pdf_file_storage.filename)
            logger.info(f"Helper: Processing PDF '{original_filename}' via key '{file_key_for_pdf_extraction}'.")
            if not allowed_file(original_filename, {'pdf'}):
                return None, "Invalid PDF file type for text extraction. Only .pdf is allowed.", original_filename
            
            upload_folder_abs = app.config.get('UPLOAD_FOLDER')
            if not upload_folder_abs or not os.path.isabs(upload_folder_abs):
                logger.error(f"UPLOAD_FOLDER '{upload_folder_abs}' is not absolute or not configured. Cannot save temp PDF.")
                return None, "Server configuration error for file uploads.", original_filename

            temp_dir = os.path.join(upload_folder_abs, 'temp_pdf_extraction_api_v4_1')
            try:
                os.makedirs(temp_dir, exist_ok=True)
            except OSError as e:
                logger.error(f"Helper: Could not create temp directory {temp_dir}: {e}", exc_info=True)
                return None, f"Server error creating temp directory for PDF: {str(e)}", original_filename

            temp_pdf_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{original_filename}")
            
            try:
                pdf_file_storage.save(temp_pdf_path)
                logger.info(f"Helper: Temporarily saved PDF for extraction: {temp_pdf_path}")
                text_content = document_qa.extract_text_from_document(temp_pdf_path) 
                if not text_content or not text_content.strip():
                    error_message = "Could not extract meaningful text from the PDF. It might be image-based, empty, or protected."
                    logger.warning(f"Helper: No meaningful text extracted from PDF: {original_filename}")
                else:
                    logger.info(f"Helper: Successfully extracted {len(text_content)} chars from PDF: {original_filename}")
            except Exception as e:
                logger.error(f"Helper: Error during PDF text extraction for '{original_filename}': {e}", exc_info=True)
                error_message = f"Server error during PDF text extraction: {str(e)}"
            finally:
                if os.path.exists(temp_pdf_path):
                    try: os.remove(temp_pdf_path); logger.debug(f"Helper: Removed temp PDF: {temp_pdf_path}")
                    except Exception as e_rem: logger.error(f"Helper: Error removing temp PDF {temp_pdf_path}: {e_rem}")
            return text_content, error_message, original_filename
        else:
            logger.warning(f"Helper: '{file_key_for_pdf_extraction}' in request.files but it's invalid or has no filename.")
            return None, f"A PDF file via '{file_key_for_pdf_extraction}' was expected but not properly provided.", None
            
    logger.debug("Helper: No direct text or 'pdf_file' found in request for text extraction.")
    return None, "No text or PDF file ('pdf_file') found in the request for text extraction.", None

@app.route('/')
def index(): 
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index.html: {e}", exc_info=True)
        return render_template('500.html', error_message="Error rendering homepage template.", error_detail=str(e)), 500

@app.route('/about')
def about(): return render_template('about.html')

@app.route('/image-analyzer-page')
@login_required
def image_analyzer_page(): return render_template('image_analyzer.html')

@app.route('/live-chat-page')
@login_required
def live_chat_page(): return render_template('live_chat.html') # The 'room' variable will be undefined here

@app.route('/doc-qa-page')
@login_required
def doc_qa_page(): 
    try:
        return render_template('doc_qa.html')
    except Exception as e:
        logger.error(f"Error rendering doc_qa.html: {e}", exc_info=True)
        abort(500) 

@app.route('/my-summaries')
@login_required
def my_summaries():
    page = request.args.get('page', 1, type=int); per_page = 10 
    summaries_pagination_obj = db.session.query(Summary).filter_by(user_id=current_user.id)\
        .order_by(Summary.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    summaries_list_for_json = []
    if summaries_pagination_obj:
        summaries_list_for_json = [s.to_dict() for s in summaries_pagination_obj.items]
    
    try: 
        summaries_json_str = json.dumps(summaries_list_for_json)
    except TypeError as e: 
        logger.error(f"Error serializing summaries for my_summaries page: {e}", exc_info=True)
        summaries_json_str = "[]" 

    return render_template('my_summaries.html', summaries=summaries_pagination_obj, summaries_json=summaries_json_str)

@app.route('/login', methods=['GET', 'POST'])
def login(): 
    if current_user.is_authenticated: return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username'); password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=request.form.get('remember') == 'on')
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'): next_page = url_for('index')
            flash('Logged in successfully!', 'success'); return redirect(next_page)
        else: flash('Invalid username or password. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register(): 
    if current_user.is_authenticated: return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username'); password = request.form.get('password')
        if not username or not password: flash('Username and password are required.', 'warning'); return redirect(url_for('register'))
        if User.query.filter_by(username=username).first(): flash('Username already exists.', 'warning'); return redirect(url_for('register'))
        new_user = User(username=username); new_user.set_password(password)
        try: 
            db.session.add(new_user); db.session.commit()
            flash('Registration successful! Please log in.', 'success'); return redirect(url_for('login'))
        except Exception as e: 
            db.session.rollback()
            logger.error(f"Reg error {username}: {e}", exc_info=True)
            flash('An error occurred during registration. Please try again.', 'danger')
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout(): logout_user(); flash('You have been logged out.', 'info'); return redirect(url_for('index'))

@app.route('/api/translate', methods=['POST'])
@login_required 
def translate_text_api(): 
    text_to_process = None; original_filename = None; error_msg = None
    data_source_params = {} 
    logger.debug(f"Translate API: Received request. Content-Type: {request.content_type}")

    if request.content_type and request.content_type.startswith('application/json'):
        data_source_params = request.get_json()
        if not data_source_params: return jsonify({"status": "error", "error": "Invalid JSON request."}), 400
        text_to_process = data_source_params.get('text')
    elif request.content_type and request.content_type.startswith('multipart/form-data'):
        text_to_process, error_msg, original_filename = get_text_from_request_data(request.form, request.files)
        data_source_params = request.form.to_dict() 
    else:
        return jsonify({"status": "error", "error": "Unsupported content type. Must be JSON or FormData."}), 415

    if error_msg: return jsonify({"status": "error", "error": error_msg, "processed_filename": original_filename}), 400
    if not text_to_process: return jsonify({"status": "error", "error": "Missing text to translate after attempting extraction."}), 400

    targets_from_form = data_source_params.get('target_languages') or request.form.getlist('targetLanguages[]') 
    targets = []
    if isinstance(targets_from_form, str):
        try: targets = json.loads(targets_from_form)
        except json.JSONDecodeError: 
            logger.warning(f"Could not parse target_languages string from form data: {targets_from_form}. Assuming single language if not list-like.")
            targets = [targets_from_form] if targets_from_form else []
    elif isinstance(targets_from_form, list): 
        targets = targets_from_form
    
    if not targets : return jsonify({"status": "error", "error": "Missing 'target_languages'"}), 400
    
    source = data_source_params.get('source_language') or data_source_params.get('sourceLanguageClient')

    results = azure_services.translate_text(text_to_process, targets, source)
    if 'error' in results: 
        return jsonify({"status": "error", "error": results['error']}), 500
    
    preview = original_filename if original_filename else text_to_process[:500]
    save_processing_result('pdf' if original_filename else 'text', 'translate', preview, 
                           {"translations": results}, 
                           {"target_languages": targets, "source_language": source})
    return jsonify({"status": "success", "translations": results, 
                    "original_text_processed": text_to_process if not original_filename else None, 
                    "processed_filename": original_filename})

@app.route('/api/analyze-sentiment', methods=['POST'])
@login_required
def analyze_sentiment_api():
    text_to_process = None; original_filename = None; error_msg = None
    if request.content_type and request.content_type.startswith('application/json'):
        data = request.get_json(); text_to_process = data.get('text')
        if not data: return jsonify({"status": "error", "error": "Invalid JSON request."}), 400
    elif request.content_type and request.content_type.startswith('multipart/form-data'):
        text_to_process, error_msg, original_filename = get_text_from_request_data(request.form, request.files)
    else: return jsonify({"status": "error", "error": "Unsupported content type."}), 415

    if error_msg: return jsonify({"status": "error", "error": error_msg, "processed_filename": original_filename}), 400
    if not text_to_process: return jsonify({"status": "error", "error": "Missing text for sentiment analysis."}), 400
        
    result = azure_services.analyze_sentiment(text_to_process)
    if 'error' in result: return jsonify({"status": "error", "error": result['error']}), 500
    
    preview = original_filename if original_filename else text_to_process[:500]
    save_processing_result('pdf' if original_filename else 'text', 'sentiment', preview, 
                           {"sentiment_analysis": result}) 
    return jsonify({"status": "success", "sentiment_analysis": result, "original_text_processed": text_to_process if not original_filename else None, "processed_filename": original_filename})

@app.route('/api/summarize', methods=['POST'])
@login_required
def summarize_api(): 
    text_to_process = None; original_filename = None; error_msg = None
    data_source_params = {} 
    if request.content_type and request.content_type.startswith('application/json'):
        data_source_params = request.get_json()
        if not data_source_params: return jsonify({"status": "error", "error": "Invalid JSON request."}), 400
        text_to_process = data_source_params.get('text')
    elif request.content_type and request.content_type.startswith('multipart/form-data'):
        text_to_process, error_msg, original_filename = get_text_from_request_data(request.form, request.files)
        data_source_params = request.form.to_dict()
    else: return jsonify({"status": "error", "error": "Unsupported content type."}), 415

    if error_msg: return jsonify({"status": "error", "error": error_msg, "processed_filename": original_filename}), 400
    if not text_to_process: return jsonify({"status": "error", "error": "Missing text for summarization."}), 400

    s_type = data_source_params.get('type', 'extractive')
    s_count_str = data_source_params.get('sentence_count') or data_source_params.get('sentenceCountClient', '3')
    try: s_count = int(s_count_str)
    except (ValueError, TypeError): return jsonify({"status":"error", "error": "Invalid sentence_count format."}), 400
    if s_type not in ['extractive', 'abstractive']: return jsonify({"status": "error", "error": "Invalid summary type"}), 400
    
    result = azure_services.extractive_summarize(text_to_process, s_count) if s_type == 'extractive' else azure_services.abstractive_summarize(text_to_process, s_count)
    if 'error' in result: return jsonify({"status": "error", "error": result['error']}), 500
    
    preview = original_filename if original_filename else text_to_process[:500]
    save_processing_result('pdf' if original_filename else 'text_summary', f'{s_type}_summary', preview, 
                           {"summary_data": result}, 
                           {"type": s_type, "sentence_count": s_count})
    return jsonify({"status": "success", "summary_data": result, "original_text_processed": text_to_process if not original_filename else None, "processed_filename": original_filename})

@app.route('/api/analyze-image', methods=['POST'])
@login_required
def analyze_image_api(): 
    if 'imageFile' not in request.files: return jsonify({"status": "error", "error": "No 'imageFile' part"}), 400
    image_file = request.files['imageFile']
    if image_file.filename == '': return jsonify({"status": "error", "error": "No image selected"}), 400
    
    feature_map_client_to_sdk = {
        "description": VisualFeatureTypes.description, "tags": VisualFeatureTypes.tags,
        "objects": VisualFeatureTypes.objects, "faces": VisualFeatureTypes.faces,
        "adult": VisualFeatureTypes.adult, "brands": VisualFeatureTypes.brands,
        "categories": VisualFeatureTypes.categories, "color": VisualFeatureTypes.color
    }
    selected_sdk_features: List[VisualFeatureTypes] = [] 
    form_features_names: List[str] = [] 
    for feature_key_form, sdk_feature_enum in feature_map_client_to_sdk.items():
        if request.form.get(feature_key_form) == 'true': 
            if sdk_feature_enum: 
                selected_sdk_features.append(sdk_feature_enum)
            form_features_names.append(feature_key_form)
            
    if not selected_sdk_features:
         return jsonify({"status": "error", "error": "No analysis features selected or VisualFeatureTypes not available"}), 400
        
    if image_file and allowed_file(image_file.filename, {'png', 'jpg', 'jpeg', 'gif', 'bmp'}):
        filename = secure_filename(image_file.filename)
        temp_filename = f"{uuid.uuid4()}_{filename}" 
        temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_images')
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, temp_filename)
        try:
            image_file.save(temp_path)
            analysis_result = azure_services.analyze_image(temp_path, visual_features_enums=selected_sdk_features)
        finally:
            if os.path.exists(temp_path): os.remove(temp_path)
        if 'error' in analysis_result: return jsonify({"status": "error", "error": analysis_result['error']}), 500
        save_processing_result('image', 'vision_analysis', filename, 
                               {"analysis": analysis_result}, 
                               {"features_requested": form_features_names})
        return jsonify({"status": "success", "analysis": analysis_result, "filename": filename})
    else: return jsonify({"status": "error", "error": "Invalid image file type"}), 400

@app.route('/api/youtube-transcript', methods=['POST'])
@login_required
def youtube_transcript_api_route(): 
    if not request.is_json: return jsonify({"status": "error", "error": "Request must be JSON"}), 415
    data = request.get_json(); url = data.get('url')
    if not url: return jsonify({"status": "error", "error": "Missing 'url'"}), 400
    from background_tasks import youtube_transcript 
    task = youtube_transcript.apply_async(args=[url]) 
    try: result = task.get(timeout=120) 
    except Exception as e: logger.error(f"YT task error: {e}"); return jsonify({"status":"error", "error": str(e)}), 500
    if result.get('status') == 'error': return jsonify(result), result.get('http_status_code', 400) 
    save_processing_result('youtube', 'transcript', url, 
                           {"transcript": result}, 
                           {"url": url})
    return jsonify({"status": "success", "transcript": result})


@app.route('/api/transcribe-audio', methods=['POST'])
@login_required
def transcribe_audio_route(): 
    if 'audio' not in request.files: return jsonify({"status": "error", "error": "No audio file part"}), 400
    audio_f = request.files['audio']; lang = request.form.get('language') 
    if audio_f.filename == '': return jsonify({"status": "error", "error": "No audio selected"}), 400
    if audio_f and allowed_file(audio_f.filename, {'wav', 'mp3', 'ogg', 'flac', 'm4a'}): 
        fname = secure_filename(audio_f.filename)
        tmp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_audio'); os.makedirs(tmp_dir, exist_ok=True)
        fpath = os.path.join(tmp_dir, f"{uuid.uuid4()}_{fname}")
        try:
            audio_f.save(fpath); from background_tasks import transcribe_audio
            task = transcribe_audio.apply_async(args=[fpath, lang])
            result = task.get(timeout=600) 
        finally:
            if os.path.exists(fpath): os.remove(fpath)
        if 'error' in result: return jsonify(result), result.get('http_status_code', 400)
        save_processing_result('audio', 'transcribe_audio', fname, 
                               {"transcription": result}, 
                               {"language": lang})
        return jsonify({"status": "success", "transcription": result})
    else: return jsonify({"status": "error", "error": "Invalid audio file type"}), 400

@app.route('/api/get-user-documents', methods=['GET'])
@login_required
def get_user_documents_route(): 
    try:
        docs = document_qa.get_user_documents(current_user.id)
        return jsonify({"status": "success", "documents": docs})
    except Exception as e: 
        logger.error(f"Error fetching documents for user {current_user.id}: {e}", exc_info=True)
        return jsonify({"status": "error", "error": "Could not retrieve documents."}), 500

@app.route('/api/document-qa', methods=['POST']) 
@login_required
def upload_document_for_qa_api(): 
    if 'document' not in request.files: return jsonify({"status": "error", "error": "No 'document' file part in request"}), 400
    doc_file = request.files['document']
    if doc_file.filename == '': return jsonify({"status": "error", "error": "No document selected for upload"}), 400
    if not allowed_file(doc_file.filename, {'pdf', 'txt', 'docx'}): 
        return jsonify({"status": "error", "error": "Invalid document format. Allowed: pdf, txt, docx"}), 400
    
    filename = secure_filename(doc_file.filename)
    temp_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_doc_uploads')
    os.makedirs(temp_upload_dir, exist_ok=True)
    temp_upload_path = os.path.join(temp_upload_dir, f"temp_docqa_upload_{uuid.uuid4()}_{filename}")
    
    try:
        doc_file.save(temp_upload_path)
        file_size = os.path.getsize(temp_upload_path)
        doc_id = document_qa.add_document(temp_upload_path, current_user.id, file_size)
    except Exception as e:
        logger.error(f"Document upload and initial processing error for QA: {e}", exc_info=True)
        return jsonify({"status": "error", "error": "Server error during document processing for QA."}), 500
    finally:
        if os.path.exists(temp_upload_path):
            try: os.remove(temp_upload_path)
            except Exception as e_rem: logger.error(f"Error removing temp QA upload {temp_upload_path}: {e_rem}")

    if not doc_id: return jsonify({"status": "error", "error": "Failed to add document to QA system after processing."}), 500
    
    save_processing_result(input_type='document_upload', action_type='doc_upload_qa', 
                           original_preview=filename, 
                           processed_data={"doc_id": doc_id, "filename": filename, "size": file_size})
    return jsonify({"status": "success", "message": "Document uploaded successfully for Q&A.", "doc_id": doc_id, "filename": filename, "size": file_size}), 201

@app.route('/api/document/<string:document_id>/ask', methods=['POST'])
@login_required
def api_document_ask_route(document_id): 
    if not request.is_json: return jsonify({"status": "error", "error": "Request must be JSON"}), 415
    data = request.get_json(); question = data.get('question')
    if not question: return jsonify({"status": "error", "error": "Question missing"}), 400
        
    ans_data = document_qa.query_document(document_id, question, user_id_for_auth=current_user.id) 
    if 'error' in ans_data: 
        status_code = 404 if "not found" in ans_data['error'].lower() or "access denied" in ans_data['error'].lower() else 500
        return jsonify({"status": "error", "error": ans_data['error']}), status_code
    
    doc_meta = document_qa.get_document_metadata(document_id)
    doc_name_preview = doc_meta.get('file_name', f"DocID:{document_id}") if doc_meta else f"DocID:{document_id}"
    
    save_processing_result(input_type='document_qa', action_type='question_answer', 
                           original_preview=f"{doc_name_preview} - Q: {question[:100]}", 
                           processed_data={"answer_data": ans_data}, 
                           request_details={"document_id": document_id, "question": question})
    return jsonify({"status": "success", **ans_data}) 

@app.route('/api/document/<string:document_id>', methods=['DELETE'])
@login_required
def api_document_delete_route(document_id): 
    if document_qa.delete_document(document_id, current_user.id): 
        return jsonify({"status": "success", "message": "Document deleted successfully."})
    else: 
        return jsonify({"status": "error", "error": "Delete failed. Document not found or access denied."}), 404


socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*", logger=True, engineio_logger=True)

@socketio.on('connect')
def handle_connect_socket(): 
    logger.info(f"Socket.IO Client connected: SID {request.sid}")

@socketio.on('join_room')
def on_join_room(data: Dict[str, str]):
    username = data.get('user', 'AnonymousUser'); room = data.get('room', 'default_room')
    join_room(room); 
    logger.info(f"User {username} (SID:{request.sid}) joined room: {room}")
    emit('user_joined', {'user': username, 'room': room}, to=room)

@socketio.on('leave_room')
def on_leave_room(data: Dict[str, str]):
    username = data.get('user', 'AnonymousUser'); room = data.get('room', 'default_room')
    leave_room(room); 
    logger.info(f"User {username} (SID:{request.sid}) left room: {room}")
    emit('user_left', {'user': username, 'room': room}, to=room, include_self=False)

# MODIFIED SOCKETIO TEXT MESSAGE HANDLER STARTS HERE
@socketio.on('text_message')
def handle_chat_text_message(data: Dict[str, Any]):
    room = data.get('room', 'default_room')
    user = data.get('user', 'AnonymousUser')
    # This is the text from client (e.g., recognized speech or typed text)
    original_text_from_client = data.get('text', '') 
    target_lang_code = data.get('translate_to')

    logger.info(f"Received text_message from {user} in {room}: '{original_text_from_client}', Translate To: {target_lang_code}")

    # Initialize variables for the payload
    text_to_display_in_bubble = original_text_from_client  # Default to original
    actual_original_text_for_payload = None  # Will hold original text only if translation occurs and is different
    original_lang_name_for_payload = None    # Language name of actual_original_text_for_payload
    translated_lang_name_for_payload = None  # Language code of text_to_display_in_bubble if it's a translation

    if target_lang_code and target_lang_code.strip() != "":
        logger.info(f"Attempting translation for '{original_text_from_client}' to '{target_lang_code}' for user {user}")
        
        translation_response = azure_services.translate_text(
            original_text_from_client, 
            [target_lang_code], 
            source_language=None  # Let Azure attempt to detect source language
        )
        
        translated_text_from_service = None
        detected_source_lang_code = None

        if not translation_response.get('error'):
            if isinstance(translation_response, dict) and target_lang_code in translation_response:
                 translated_text_from_service = translation_response[target_lang_code]
            elif isinstance(translation_response.get('translations'), dict) and target_lang_code in translation_response['translations']:
                 translated_text_from_service = translation_response['translations'][target_lang_code]

            if isinstance(translation_response, dict):
                detected_source_lang_code = translation_response.get('detected_source_language', 
                                                                  translation_response.get('detectedSourceLanguage'))
        
            if translated_text_from_service:
                if translated_text_from_service.strip().lower() != original_text_from_client.strip().lower():
                    text_to_display_in_bubble = translated_text_from_service
                    actual_original_text_for_payload = original_text_from_client
                    
                    if detected_source_lang_code:
                        # Assuming azure_services.get_language_name(code) exists
                        original_lang_name_for_payload = azure_services.get_language_name(detected_source_lang_code) or detected_source_lang_code
                    else:
                        original_lang_name_for_payload = "Original" 

                    translated_lang_name_for_payload = target_lang_code 
                    logger.info(f"Successfully translated '{original_text_from_client}' (from {original_lang_name_for_payload or 'auto-detected'}) to '{text_to_display_in_bubble}' ({target_lang_code}) for user {user}")
                else:
                    logger.warning(f"Translation to '{target_lang_code}' resulted in same text. Original: '{original_text_from_client}'. Using original text.")
            else:
                logger.warning(f"Translation attempt for '{target_lang_code}' did not yield text. Response: {translation_response}. Using original text.")
        else:
            logger.warning(f"Translation service returned an error for user {user}: {translation_response.get('error', 'Unknown translation error')}")
    
    payload = {
        'user': user,
        'text': text_to_display_in_bubble,
        'original_text': actual_original_text_for_payload,
        'original_lang_name': original_lang_name_for_payload,
        'translated_to_lang_name': translated_lang_name_for_payload,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'room': room
    }
    
    logger.debug(f"Emitting 'chat_message' event with payload: {json.dumps(payload)}")
    emit('chat_message', payload, to=room)
# MODIFIED SOCKETIO TEXT MESSAGE HANDLER ENDS HERE

@socketio.on('typing')
def on_typing_socket(data: Dict[str, str]): emit('typing', data, to=data.get('room','default_room'), include_self=False)

@socketio.on('stop_typing')
def on_stop_typing_socket(data: Dict[str, str]): emit('stop_typing', data, to=data.get('room','default_room'), include_self=False)

@socketio.on('disconnect')
def handle_socket_disconnect_event(): 
    logger.info(f"Socket.IO Client disconnected: SID {request.sid}")


@app.route('/api/get-speech-token', methods=['GET'])
@login_required
def get_speech_token_route():
    creds = azure_services.get_speech_token()
    if 'error' in creds: return jsonify(creds), 503 
    return jsonify(creds)

@app.errorhandler(400)
def bad_request_error_handler(e): 
    msg = str(e.description if hasattr(e, 'description') and e.description else e)
    logger.warning(f"400 Bad Request: {msg} for URL {request.url}", exc_info=True)
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html: 
        return jsonify(status="error",error="Bad Request",message=msg),400
    return render_template('400.html', error_message=msg, error_detail=msg),400 

@app.errorhandler(404)
def page_not_found_error_handler(e): 
    msg = str(e.description if hasattr(e, 'description') and e.description else e)
    logger.warning(f"404 Not Found: {request.path} - {msg}")
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html: 
        return jsonify(status="error",error="Not Found",message=msg),404
    return render_template('404.html', error_message=msg),404

@app.errorhandler(415)
def unsupported_media_type_error_handler(e):
    msg = str(e.description if hasattr(e, 'description') and e.description else e)
    logger.warning(f"415 Unsupported Media Type: {msg} for URL {request.url}")
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html: 
        return jsonify(status="error",error="Unsupported Media Type",message=msg),415
    return render_template('500.html',error_code=415,error_message="Unsupported Media Type",error_detail=msg),415

@app.errorhandler(500)
def internal_server_error_handler_page(e): 
    original_exception = getattr(e, "original_exception", e)
    logger.error(f"500 Internal Server Error: {original_exception} for URL {request.url}", exc_info=sys.exc_info())
    db.session.rollback() 
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html: 
        return jsonify(status="error",error="Internal Server Error",message="An unexpected server error occurred."),500
    return render_template('500.html', error_message="Internal Server Error", error_detail=str(original_exception)),500


if __name__ == '__main__':
    logger.info("Starting Flask-SocketIO development server with eventlet...")
    try:
        # For production, debug should be False and use_reloader should be False
        # For development, app.debug can control both.
        socketio.run(app, debug=app.debug, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), use_reloader=app.debug)
    except KeyboardInterrupt: 
        logger.info("Application shutting down via KeyboardInterrupt...")
    except Exception as e: 
        logger.critical(f"Failed to start application: {e}", exc_info=True)
