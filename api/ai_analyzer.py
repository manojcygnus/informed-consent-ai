"""
AI Analysis Module - Free Implementation using Ollama
Uses local LLM models (Llama 3.1, Mistral, etc.) for zero-cost AI processing
"""

import json
import re
import ollama


class AIAnalyzer:
    """Handle AI analysis using local Ollama models"""

    def __init__(self, model='llama3.1', host='http://localhost:11434'):
        """
        Initialize AI analyzer with Ollama

        Args:
            model: Ollama model name (llama3.1, mistral, gemma2, etc.)
            host: Ollama server URL
        """
        self.model = model
        self.host = host
        print(f"Initialized AI Analyzer with model: {model}")

    def analyze_consent_form(self, ocr_text):
        """
        Analyze consent form text and extract structured information

        Args:
            ocr_text: Raw text extracted from PDF

        Returns:
            dict: Structured consent data
        """
        print(f"Analyzing consent form with {self.model}...")

        prompt = f"""You are a medical consent form analyzer. Analyze the following consent form text and extract information in JSON format.

CONSENT FORM TEXT:
{ocr_text}

Extract the following information and return ONLY a valid JSON object with these fields:
- patient_name: Patient's full name
- patient_email: Patient's email address (if available)
- patient_dob: Patient's date of birth (format: YYYY-MM-DD or as written)
- doctor_name: Name of the doctor/physician
- procedure: Medical procedure or treatment
- procedure_date: Date of procedure (format: YYYY-MM-DD or as written)
- consented_items: Array of items/procedures the patient consented to
- declined_items: Array of items the patient declined or refused
- summary: A 2-3 sentence summary of the consent form

Important:
- Return ONLY the JSON object, no additional text
- If a field is not found, use null
- For email, if not found, generate format: firstname.lastname@example.com
- For consented_items and declined_items, return arrays even if empty
- Be thorough in identifying what was consented to vs declined

JSON Response:"""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }]
            )

            response_text = response['message']['content'].strip()

            # Extract JSON from response (handle cases where model adds extra text)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)

            # Parse JSON
            analysis = json.loads(response_text)

            # Validate and set defaults
            analysis = self._validate_analysis(analysis)

            print("AI analysis completed successfully!")
            return analysis

        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON from AI response: {e}")
            print(f"Raw response: {response_text[:500]}")
            # Return default structure
            return self._get_default_analysis()

        except Exception as e:
            print(f"AI analysis failed: {str(e)}")
            return self._get_default_analysis()

    def answer_query(self, query, patient_consents):
        """
        Answer patient query using their consent form data

        Args:
            query: Patient's natural language question
            patient_consents: List of consent data for this patient

        Returns:
            str: AI-generated answer
        """
        print(f"Processing query with {self.model}...")

        # Format consent data for context
        context = self._format_consents_for_context(patient_consents)

        prompt = f"""You are a helpful medical consent assistant. Answer the patient's question based ONLY on their consent form data below.

PATIENT'S CONSENT FORMS:
{context}

PATIENT'S QUESTION:
{query}

IMPORTANT RULES:
- Answer based ONLY on the consent form data provided above
- Be clear, patient-friendly, and concise
- If the information is not in the consent forms, politely say you don't have that information
- NEVER discuss or mention other patients' data
- Focus on what the patient consented to, declined, procedures, and dates
- Be helpful and professional

Your Answer:"""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }]
            )

            answer = response['message']['content'].strip()
            print("Query answered successfully!")
            return answer

        except Exception as e:
            print(f"Query processing failed: {str(e)}")
            return "I apologize, but I'm having trouble processing your query right now. Please try again."

    def _format_consents_for_context(self, patient_consents):
        """Format consent data for AI context"""
        if not patient_consents:
            return "No consent forms found."

        context_parts = []
        for idx, consent in enumerate(patient_consents, 1):
            context_parts.append(f"""
CONSENT FORM #{idx}:
- Patient: {consent.get('patient_name', 'Unknown')}
- Procedure: {consent.get('procedure', 'Unknown')}
- Doctor: {consent.get('doctor_name', 'Unknown')}
- Date: {consent.get('procedure_date', 'Unknown')}
- Consented to: {', '.join(consent.get('consented_items', [])) or 'None listed'}
- Declined: {', '.join(consent.get('declined_items', [])) or 'None listed'}
- Summary: {consent.get('summary', 'No summary available')}
""")

        return '\n'.join(context_parts)

    def _validate_analysis(self, analysis):
        """Ensure analysis has all required fields"""
        defaults = self._get_default_analysis()

        for key in defaults:
            if key not in analysis or analysis[key] is None:
                analysis[key] = defaults[key]

        return analysis

    def _get_default_analysis(self):
        """Get default analysis structure"""
        return {
            'patient_name': 'Unknown',
            'patient_email': 'unknown@example.com',
            'patient_dob': None,
            'doctor_name': 'Unknown',
            'procedure': 'Unknown',
            'procedure_date': None,
            'consented_items': [],
            'declined_items': [],
            'summary': 'Unable to extract summary from consent form.'
        }

    def check_ollama_connection(self):
        """Check if Ollama is running and model is available"""
        try:
            # Try to list models
            models = ollama.list()
            print(f"Ollama is running. Available models: {[m['name'] for m in models.get('models', [])]}")

            # Check if our model is available
            model_names = [m['name'] for m in models.get('models', [])]
            if not any(self.model in name for name in model_names):
                print(f"Warning: Model '{self.model}' not found. Available models: {model_names}")
                print(f"Download it with: ollama pull {self.model}")
                return False

            return True

        except Exception as e:
            print(f"Ollama connection failed: {str(e)}")
            print("Make sure Ollama is running: 'ollama serve'")
            return False


# Test function
def test_analyzer():
    """Test AI analyzer"""
    analyzer = AIAnalyzer()

    # Check connection
    if not analyzer.check_ollama_connection():
        print("\nPlease install and start Ollama:")
        print("1. Install: https://ollama.ai/download")
        print("2. Run: ollama serve")
        print("3. Pull model: ollama pull llama3.1")
        return

    # Test analysis
    sample_text = """
    PATIENT CONSENT FORM

    Patient Name: John Smith
    Email: john.smith@email.com
    Date of Birth: 1985-03-15

    I hereby consent to undergo an Appendectomy procedure
    to be performed by Dr. Sarah Johnson on November 15, 2024.

    I consent to:
    - Surgical procedure (Appendectomy)
    - General anesthesia
    - Post-operative care

    I decline:
    - Participation in medical research
    - Photography of the procedure
    """

    result = analyzer.analyze_consent_form(sample_text)
    print("\n" + "="*50)
    print("ANALYSIS RESULT:")
    print("="*50)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    test_analyzer()
