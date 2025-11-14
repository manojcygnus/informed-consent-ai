# InformedConsent AI - Quick Start Guide (5 Minutes)

## Step 1: Install Ollama (2 minutes)

1. Visit: https://ollama.ai/download
2. Download and install for your OS
3. Open terminal and run:
```bash
ollama pull llama3.1
```

## Step 2: Install Python Dependencies (1 minute)

```bash
# Navigate to project
cd informed-consent-ai

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Install Tesseract (Optional - for scanned PDFs)

**macOS:**
```bash
brew install tesseract poppler
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr poppler-utils
```

**Windows:**
- Download Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- Download Poppler: https://github.com/oschwartz10612/poppler-windows/releases/

## Step 4: Initialize Database (30 seconds)

```bash
cd api
python database.py
cd ..
```

## Step 5: Start the System (30 seconds)

**Terminal 1 - Start API:**
```bash
cd api
python app.py
```

**Terminal 2 - Open Frontend:**
```bash
# Just open in browser
open frontend/index.html
# or double-click the file
```

## Step 6: Process a Consent Form (1 minute)

```bash
# In a new terminal
cd scripts
python ingest_pdf.py path/to/your/consent.pdf
```

You'll get output like:
```
PROCESSING COMPLETE
Patient Account:
  Email: john.smith@example.com
  Password: john123!
```

## Step 7: Login and Query (30 seconds)

1. Open `frontend/index.html` in browser
2. Login with email and password from Step 6
3. Ask: "What did I consent to?"

## That's It!

You now have a fully functional, free consent management system running locally!

## Quick Test (No PDF Available?)

Create a test patient manually:

```bash
cd api
python
```

```python
from database import DatabaseManager, Patient

db = DatabaseManager()
session = db.get_session()

patient = Patient(
    email="test@example.com",
    patient_name="Test User"
)
patient.set_password("test123!")
patient.default_password = "test123!"

session.add(patient)
session.commit()
session.close()

print("Test account created!")
print("Email: test@example.com")
print("Password: test123!")
```

Now you can login with these credentials!

## Next Steps

- Read the full README.md for detailed documentation
- Process your actual consent PDFs
- Customize the frontend
- Deploy to free hosting

## Need Help?

Check the troubleshooting section in README.md
