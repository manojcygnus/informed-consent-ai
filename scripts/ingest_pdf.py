"""
PDF Ingestion Script - Process consent PDFs and store in database
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import DatabaseManager, Patient, Consent, EntityIndex
from api.ocr_processor import OCRProcessor
from api.ai_analyzer import AIAnalyzer
from dotenv import load_dotenv

load_dotenv()


class PDFIngestionService:
    """Process consent PDFs and populate database"""

    def __init__(self):
        """Initialize ingestion service"""
        self.db_manager = DatabaseManager(os.getenv('DATABASE_PATH', './data/consent_system.db'))
        self.ocr_processor = OCRProcessor(os.getenv('OCR_ENGINE', 'auto'))
        self.ai_analyzer = AIAnalyzer(
            model=os.getenv('OLLAMA_MODEL', 'llama3.1'),
            host=os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        )

    def process_pdf(self, pdf_path):
        """
        Process a consent PDF file

        Args:
            pdf_path: Path to PDF file

        Returns:
            dict: Processing result
        """
        print(f"\n{'='*60}")
        print(f"Processing: {pdf_path}")
        print(f"{'='*60}\n")

        try:
            # Step 1: Extract text with OCR
            print("Step 1: Extracting text from PDF...")
            ocr_text = self.ocr_processor.extract_text_from_pdf(pdf_path)
            print(f"✓ Extracted {len(ocr_text)} characters")

            # Step 2: AI Analysis
            print("\nStep 2: Analyzing with AI...")
            analysis = self.ai_analyzer.analyze_consent_form(ocr_text)
            print(f"✓ Analysis complete")
            print(f"  Patient: {analysis['patient_name']}")
            print(f"  Email: {analysis['patient_email']}")
            print(f"  Procedure: {analysis['procedure']}")

            # Step 3: Store in database
            print("\nStep 3: Storing in database...")
            result = self._store_consent_data(pdf_path, ocr_text, analysis)
            print(f"✓ Stored successfully")

            print(f"\n{'='*60}")
            print("PROCESSING COMPLETE")
            print(f"{'='*60}")
            print(f"Patient Account:")
            print(f"  Email: {analysis['patient_email']}")
            print(f"  Password: {result['default_password']}")
            print(f"{'='*60}\n")

            return result

        except Exception as e:
            print(f"\n✗ Error processing PDF: {str(e)}")
            raise

    def _store_consent_data(self, pdf_path, ocr_text, analysis):
        """Store consent data in database"""
        db_session = self.db_manager.get_session()

        try:
            filename = os.path.basename(pdf_path)
            patient_email = analysis['patient_email'].lower()
            patient_name = analysis['patient_name']

            # Step 1: Create or get patient account
            patient = db_session.query(Patient).filter(Patient.email == patient_email).first()

            if not patient:
                # Create new patient
                print(f"  Creating new patient account for {patient_email}...")
                patient = Patient(
                    email=patient_email,
                    patient_name=patient_name
                )

                # Generate default password: firstname123!
                first_name = patient_name.split()[0].lower()
                default_password = f"{first_name}123!"
                patient.set_password(default_password)
                patient.default_password = default_password

                db_session.add(patient)
                db_session.flush()  # Get patient.id
                print(f"  ✓ Patient account created")
            else:
                print(f"  ✓ Using existing patient account")
                default_password = patient.default_password

            # Step 2: Create consent record
            print(f"  Creating consent record...")
            consent = Consent(
                patient_id=patient.id,
                filename=filename,
                full_text=ocr_text,
                ai_analysis_json=json.dumps(analysis),
                processed_timestamp=datetime.utcnow()
            )
            db_session.add(consent)
            db_session.flush()  # Get consent.id
            print(f"  ✓ Consent record created")

            # Step 3: Create entity index for searchability
            print(f"  Creating entity index...")
            entity_index = EntityIndex(
                consent_id=consent.id,
                patient_id=patient.id,
                patient_name=analysis['patient_name'],
                patient_email=analysis['patient_email'],
                patient_dob=analysis.get('patient_dob'),
                doctor_name=analysis.get('doctor_name'),
                procedure=analysis.get('procedure'),
                procedure_date=analysis.get('procedure_date'),
                consented_items=json.dumps(analysis.get('consented_items', [])),
                declined_items=json.dumps(analysis.get('declined_items', [])),
                summary=analysis.get('summary'),
                search_terms=self._generate_search_terms(analysis),
                processed_timestamp=datetime.utcnow()
            )
            db_session.add(entity_index)
            print(f"  ✓ Entity index created")

            # Commit all changes
            db_session.commit()

            return {
                'success': True,
                'patient_id': patient.id,
                'patient_name': patient_name,
                'patient_email': patient_email,
                'default_password': default_password,
                'consent_id': consent.id,
                'filename': filename
            }

        except Exception as e:
            db_session.rollback()
            raise e
        finally:
            db_session.close()

    def _generate_search_terms(self, analysis):
        """Generate search terms for entity index"""
        terms = []

        # Add patient name variations
        if analysis.get('patient_name'):
            terms.append(analysis['patient_name'].lower())
            name_parts = analysis['patient_name'].lower().split()
            terms.extend(name_parts)

        # Add email
        if analysis.get('patient_email'):
            terms.append(analysis['patient_email'].lower())

        # Add procedure
        if analysis.get('procedure'):
            terms.append(analysis['procedure'].lower())

        # Add doctor
        if analysis.get('doctor_name'):
            terms.append(analysis['doctor_name'].lower())

        return ' '.join(set(terms))

    def process_directory(self, directory_path):
        """Process all PDFs in a directory"""
        if not os.path.isdir(directory_path):
            print(f"Error: {directory_path} is not a directory")
            return

        pdf_files = [f for f in os.listdir(directory_path) if f.endswith('.pdf')]

        if not pdf_files:
            print(f"No PDF files found in {directory_path}")
            return

        print(f"\nFound {len(pdf_files)} PDF files to process\n")

        results = []
        for pdf_file in pdf_files:
            pdf_path = os.path.join(directory_path, pdf_file)
            try:
                result = self.process_pdf(pdf_path)
                results.append(result)
            except Exception as e:
                print(f"Failed to process {pdf_file}: {str(e)}")
                continue

        # Summary
        print(f"\n{'='*60}")
        print("BATCH PROCESSING COMPLETE")
        print(f"{'='*60}")
        print(f"Total processed: {len(results)}/{len(pdf_files)}")
        print(f"\nPatient Accounts Created/Updated:")
        for result in results:
            print(f"  • {result['patient_email']} → Password: {result['default_password']}")
        print(f"{'='*60}\n")


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Process single PDF:    python ingest_pdf.py <path_to_pdf>")
        print("  Process directory:     python ingest_pdf.py <path_to_directory>")
        sys.exit(1)

    path = sys.argv[1]

    # Check Ollama
    print("Checking Ollama connection...")
    analyzer = AIAnalyzer()
    if not analyzer.check_ollama_connection():
        print("\nERROR: Ollama is not running or model not found!")
        print("Please:")
        print("1. Install Ollama: https://ollama.ai/download")
        print("2. Start Ollama: ollama serve")
        print("3. Pull model: ollama pull llama3.1")
        sys.exit(1)

    # Initialize service
    service = PDFIngestionService()

    # Process path
    if os.path.isfile(path):
        service.process_pdf(path)
    elif os.path.isdir(path):
        service.process_directory(path)
    else:
        print(f"Error: {path} not found")
        sys.exit(1)


if __name__ == '__main__':
    main()
