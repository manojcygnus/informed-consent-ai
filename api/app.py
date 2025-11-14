"""
Flask API for Free Consent Management System
Handles authentication, queries, and patient portal
"""

import os
import json
import secrets
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from database import DatabaseManager, Patient, Session, EntityIndex
from ai_analyzer import AIAnalyzer

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
CORS(app)

# Initialize database
DB_PATH = os.getenv('DATABASE_PATH', './data/consent_system.db')
db_manager = DatabaseManager(DB_PATH)

# Initialize AI analyzer
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.1')
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
ai_analyzer = AIAnalyzer(model=OLLAMA_MODEL, host=OLLAMA_HOST)

# Configuration
SESSION_EXPIRY_HOURS = int(os.getenv('SESSION_EXPIRY_HOURS', 8))


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/api/login', methods=['POST'])
def login():
    """Patient login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400

        # Get patient from database
        db_session = db_manager.get_session()
        patient = db_session.query(Patient).filter(Patient.email == email).first()

        if not patient:
            db_session.close()
            return jsonify({'error': 'Invalid credentials'}), 401

        # Verify password
        if not patient.check_password(password):
            db_session.close()
            return jsonify({'error': 'Invalid credentials'}), 401

        # Create session token
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=SESSION_EXPIRY_HOURS)

        new_session = Session(
            patient_id=patient.id,
            session_token=session_token,
            expires_at=expires_at
        )
        db_session.add(new_session)
        db_session.commit()

        response_data = {
            'success': True,
            'session_token': session_token,
            'patient_name': patient.patient_name,
            'email': patient.email,
            'expires_at': expires_at.isoformat()
        }

        db_session.close()
        return jsonify(response_data), 200

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500


@app.route('/api/logout', methods=['POST'])
def logout():
    """Patient logout endpoint"""
    try:
        session_token = request.headers.get('Authorization', '').replace('Bearer ', '')

        if not session_token:
            return jsonify({'error': 'No session token provided'}), 400

        db_session = db_manager.get_session()
        session = db_session.query(Session).filter(Session.session_token == session_token).first()

        if session:
            db_session.delete(session)
            db_session.commit()

        db_session.close()
        return jsonify({'success': True}), 200

    except Exception as e:
        print(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500


def validate_session(session_token):
    """Validate session token and return patient_id"""
    if not session_token:
        return None

    db_session = db_manager.get_session()
    session = db_session.query(Session).filter(Session.session_token == session_token).first()

    if not session:
        db_session.close()
        return None

    # Check if expired
    if session.expires_at < datetime.utcnow():
        db_session.delete(session)
        db_session.commit()
        db_session.close()
        return None

    patient_id = session.patient_id
    db_session.close()
    return patient_id


# ============================================================================
# QUERY ENDPOINTS
# ============================================================================

@app.route('/api/query', methods=['POST'])
def query():
    """Process patient query"""
    try:
        # Validate session
        session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        patient_id = validate_session(session_token)

        if not patient_id:
            return jsonify({'error': 'Invalid or expired session'}), 401

        # Get query
        data = request.get_json()
        query_text = data.get('query', '').strip()

        if not query_text:
            return jsonify({'error': 'Query text required'}), 400

        # Get patient's consent data
        db_session = db_manager.get_session()
        patient = db_session.query(Patient).filter(Patient.id == patient_id).first()

        if not patient:
            db_session.close()
            return jsonify({'error': 'Patient not found'}), 404

        # Get all consent forms for this patient
        consents = db_session.query(EntityIndex).filter(
            EntityIndex.patient_id == patient_id
        ).all()

        if not consents:
            db_session.close()
            return jsonify({
                'answer': 'I could not find any consent forms associated with your account. '
                         'Please contact your healthcare provider if you believe this is an error.'
            }), 200

        # Format consent data for AI
        consent_data = []
        for consent in consents:
            consent_dict = {
                'patient_name': consent.patient_name,
                'patient_email': consent.patient_email,
                'doctor_name': consent.doctor_name,
                'procedure': consent.procedure,
                'procedure_date': consent.procedure_date,
                'consented_items': json.loads(consent.consented_items) if consent.consented_items else [],
                'declined_items': json.loads(consent.declined_items) if consent.declined_items else [],
                'summary': consent.summary
            }
            consent_data.append(consent_dict)

        db_session.close()

        # Get AI answer
        answer = ai_analyzer.answer_query(query_text, consent_data)

        return jsonify({
            'answer': answer,
            'query': query_text
        }), 200

    except Exception as e:
        print(f"Query error: {str(e)}")
        return jsonify({'error': 'Query processing failed'}), 500


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    # Check Ollama connection
    ollama_status = ai_analyzer.check_ollama_connection()

    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'ollama': 'connected' if ollama_status else 'disconnected',
        'model': OLLAMA_MODEL
    }), 200


@app.route('/api/stats', methods=['GET'])
def stats():
    """Get system statistics (requires authentication)"""
    try:
        session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        patient_id = validate_session(session_token)

        if not patient_id:
            return jsonify({'error': 'Invalid or expired session'}), 401

        db_session = db_manager.get_session()

        # Get patient's consent count
        consent_count = db_session.query(EntityIndex).filter(
            EntityIndex.patient_id == patient_id
        ).count()

        patient = db_session.query(Patient).filter(Patient.id == patient_id).first()

        db_session.close()

        return jsonify({
            'consent_forms': consent_count,
            'patient_name': patient.patient_name if patient else 'Unknown',
            'email': patient.email if patient else 'Unknown'
        }), 200

    except Exception as e:
        print(f"Stats error: {str(e)}")
        return jsonify({'error': 'Failed to get statistics'}), 500


@app.route('/api/upload', methods=['POST'])
def upload_consent():
    """Upload and process consent PDF"""
    try:
        # Validate session
        session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        patient_id = validate_session(session_token)

        if not patient_id:
            return jsonify({'error': 'Invalid or expired session'}), 401

        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400

        # Save uploaded file
        upload_folder = os.getenv('UPLOAD_FOLDER', './uploads')
        os.makedirs(upload_folder, exist_ok=True)

        from werkzeug.utils import secure_filename
        import uuid

        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        # Process PDF
        from ocr_processor import OCRProcessor

        ocr = OCRProcessor(ocr_engine='auto')
        print(f"Processing uploaded PDF: {file.filename}")

        # Extract text
        text = ocr.extract_text_from_pdf(file_path)

        if not text or len(text) < 50:
            os.remove(file_path)  # Clean up
            return jsonify({'error': 'Could not extract text from PDF'}), 400

        # Analyze with AI
        analysis = ai_analyzer.analyze_consent_form(text)

        # Get patient info
        db_session = db_manager.get_session()
        patient = db_session.query(Patient).filter(Patient.id == patient_id).first()

        # Store in database
        from database import Consent, EntityIndex

        consent = Consent(
            patient_id=patient_id,
            filename=file.filename,
            full_text=text,
            ai_analysis_json=json.dumps(analysis),
            processed_timestamp=datetime.utcnow()
        )
        db_session.add(consent)
        db_session.commit()

        # Create entity index
        entity = EntityIndex(
            consent_id=consent.id,
            patient_id=patient_id,
            patient_name=analysis.get('patient_name', patient.patient_name),
            patient_email=analysis.get('patient_email', patient.email),
            patient_dob=analysis.get('patient_dob'),
            doctor_name=analysis.get('doctor_name'),
            procedure=analysis.get('procedure'),
            procedure_date=analysis.get('procedure_date'),
            consented_items=json.dumps(analysis.get('consented_items', [])),
            declined_items=json.dumps(analysis.get('declined_items', [])),
            summary=analysis.get('summary', ''),
            search_terms=' '.join([
                str(analysis.get('patient_name', '')),
                str(analysis.get('doctor_name', '')),
                str(analysis.get('procedure', '')),
                ' '.join(analysis.get('consented_items', []))
            ]).lower(),
            processed_timestamp=datetime.utcnow()
        )
        db_session.add(entity)
        db_session.commit()
        db_session.close()

        return jsonify({
            'success': True,
            'message': 'Consent form processed successfully',
            'analysis': analysis
        }), 200

    except Exception as e:
        print(f"Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to process PDF: {str(e)}'}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Initialize database
    print("Initializing database...")
    db_manager.init_db()

    # Check Ollama connection
    print("\nChecking Ollama connection...")
    if not ai_analyzer.check_ollama_connection():
        print("\nWARNING: Ollama is not running or model not found!")
        print("1. Install Ollama: https://ollama.ai/download")
        print("2. Start Ollama: ollama serve")
        print(f"3. Pull model: ollama pull {OLLAMA_MODEL}")
        print("\nAPI will start but AI features won't work until Ollama is running.\n")

    # Start Flask app
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 5000))

    print(f"\n{'='*60}")
    print(f"InformedConsent AI API")
    print(f"{'='*60}")
    print(f"Server: http://{host}:{port}")
    print(f"Health check: http://{host}:{port}/api/health")
    print(f"Database: {DB_PATH}")
    print(f"AI Model: {OLLAMA_MODEL}")
    print(f"{'='*60}\n")

    app.run(host=host, port=port, debug=True)
