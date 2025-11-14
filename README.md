# InformedConsent AI

A **100% free and open-source** patient consent management system with AI-powered OCR and natural language query processing. No cloud costs, no API fees, runs completely locally!

## Features

- **Free OCR**: Tesseract & pdfplumber (no cost)
- **Free AI**: Ollama with Llama 3.1 (runs locally)
- **Free Database**: SQLite (no server needed)
- **Free Hosting**: Can run locally or deploy to free tiers
- **Secure**: SHA-256 password hashing, session tokens
- **Privacy**: All data stays on your infrastructure
- **Offline Capable**: Works without internet

## Tech Stack (All Free!)

| Component | Technology | Cost |
|-----------|-----------|------|
| OCR | Tesseract / pdfplumber | $0 |
| AI/LLM | Ollama (Llama 3.1) | $0 |
| Database | SQLite | $0 |
| Backend | Python + Flask | $0 |
| Frontend | HTML/CSS/JS | $0 |
| **Total** | | **$0** |

## Project Structure

```
informed-consent-ai/
├── api/
│   ├── app.py              # Flask API server
│   ├── database.py         # SQLite database models
│   ├── ocr_processor.py    # PDF text extraction
│   └── ai_analyzer.py      # Ollama AI analysis
├── frontend/
│   └── index.html          # Patient portal UI
├── scripts/
│   └── ingest_pdf.py       # PDF ingestion script
├── uploads/                # PDF storage
├── data/                   # SQLite database
├── requirements.txt        # Python dependencies
├── .env.example           # Configuration template
└── README.md              # This file
```

## Quick Start (5 minutes)

### 1. Install Prerequisites

**macOS:**
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11
brew install python@3.11

# Install Tesseract (for scanned PDFs)
brew install tesseract

# Install Poppler (for PDF to image conversion)
brew install poppler
```

**Linux (Ubuntu/Debian):**
```bash
# Update system
sudo apt-get update

# Install Python
sudo apt-get install python3.11 python3-pip

# Install Tesseract
sudo apt-get install tesseract-ocr

# Install Poppler
sudo apt-get install poppler-utils
```

**Windows:**
```bash
# Install Python from: https://www.python.org/downloads/
# Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
# Install Poppler from: https://github.com/oschwartz10612/poppler-windows/releases/
```

### 2. Install Ollama (Local AI)

**All Platforms:**
1. Download from: https://ollama.ai/download
2. Install and run
3. Pull the model:
```bash
ollama pull llama3.1
```

### 3. Set Up Project

```bash
# Clone/navigate to project
cd informed-consent-ai

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env if needed (defaults work fine)
```

### 4. Initialize Database

```bash
cd api
python database.py
cd ..
```

### 5. Start Services

**Terminal 1 - Start Ollama (if not running):**
```bash
ollama serve
```

**Terminal 2 - Start API Server:**
```bash
cd api
python app.py
```

**Terminal 3 - Open Frontend:**
```bash
open frontend/index.html
# or just double-click index.html
```

## Usage

### Process Consent PDFs

**Single PDF:**
```bash
cd scripts
python ingest_pdf.py path/to/consent.pdf
```

**Batch Process Directory:**
```bash
python ingest_pdf.py path/to/pdfs/
```

**Output:**
```
Processing: consent_form.pdf
Step 1: Extracting text from PDF...
✓ Extracted 1250 characters

Step 2: Analyzing with AI...
✓ Analysis complete
  Patient: John Smith
  Email: john.smith@example.com
  Procedure: Appendectomy

Step 3: Storing in database...
✓ Stored successfully

PROCESSING COMPLETE
Patient Account:
  Email: john.smith@example.com
  Password: john123!
```

### Patient Portal

1. Open `frontend/index.html` in browser
2. Login with:
   - Email: From consent form
   - Password: `{firstname}123!` (e.g., `john123!`)
3. Ask questions:
   - "What did I consent to?"
   - "Tell me about my procedure"
   - "Did I decline anything?"

## API Endpoints

Base URL: `http://localhost:5000/api`

### Authentication

**Login:**
```bash
POST /api/login
Content-Type: application/json

{
  "email": "john.smith@example.com",
  "password": "john123!"
}

Response:
{
  "success": true,
  "session_token": "abc123...",
  "patient_name": "John Smith",
  "email": "john.smith@example.com"
}
```

**Logout:**
```bash
POST /api/logout
Authorization: Bearer <session_token>
```

### Queries

**Ask Question:**
```bash
POST /api/query
Authorization: Bearer <session_token>
Content-Type: application/json

{
  "query": "What did I consent to?"
}

Response:
{
  "answer": "Based on your consent form...",
  "query": "What did I consent to?"
}
```

**Get Statistics:**
```bash
GET /api/stats
Authorization: Bearer <session_token>

Response:
{
  "consent_forms": 2,
  "patient_name": "John Smith",
  "email": "john.smith@example.com"
}
```

**Health Check:**
```bash
GET /api/health

Response:
{
  "status": "healthy",
  "database": "connected",
  "ollama": "connected",
  "model": "llama3.1"
}
```

## Configuration

Edit `.env` file:

```bash
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this

# Database
DATABASE_PATH=./data/consent_system.db

# Uploads
UPLOAD_FOLDER=./uploads

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1  # or mistral, gemma2, etc.

# OCR Configuration
OCR_ENGINE=auto  # Options: pdfplumber, tesseract, auto

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000

# Session Configuration
SESSION_EXPIRY_HOURS=8
```

## Deployment Options (All Free!)

### Option 1: Local Development
```bash
python api/app.py
```
Access at: `http://localhost:5000`

### Option 2: Render.com (Free Tier)
1. Create account at render.com
2. Connect GitHub repo
3. Create Web Service
4. Set environment variables
5. Deploy

**Free tier includes:**
- 750 hours/month
- Auto-sleep after 15 min inactivity
- Custom domains

### Option 3: Railway.app (Free Tier)
1. Create account at railway.app
2. Deploy from GitHub
3. Add SQLite volume
4. Set environment variables

**Free tier includes:**
- 500 hours/month
- 1GB storage

### Option 4: PythonAnywhere (Free Tier)
1. Create account at pythonanywhere.com
2. Upload code
3. Configure WSGI
4. Run

**Free tier includes:**
- 1 web app
- Limited CPU
- Perfect for small deployments

### Option 5: Docker
```bash
# Coming soon - Dockerfile included in next update
docker-compose up
```

## Testing

### Test OCR
```bash
cd api
python ocr_processor.py path/to/test.pdf
```

### Test AI Analyzer
```bash
cd api
python ai_analyzer.py
```

### Test Database
```bash
cd api
python database.py
```

### Test Full Pipeline
```bash
cd scripts
python ingest_pdf.py test_consent.pdf
```

## Troubleshooting

### Ollama Not Running
```
ERROR: Ollama connection failed

Solution:
1. Check Ollama is running: ollama serve
2. Check model is installed: ollama list
3. Pull model if needed: ollama pull llama3.1
```

### Tesseract Not Found
```
ERROR: Tesseract extraction failed

Solution (macOS):
brew install tesseract

Solution (Linux):
sudo apt-get install tesseract-ocr

Solution (Windows):
Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### Poppler Not Found
```
ERROR: Unable to get page count. Is poppler installed?

Solution (macOS):
brew install poppler

Solution (Linux):
sudo apt-get install poppler-utils
```

### Database Locked
```
ERROR: database is locked

Solution:
Close any other processes accessing the database
Or delete data/consent_system.db and reinitialize
```

### Port Already in Use
```
ERROR: Address already in use

Solution:
Change API_PORT in .env to a different port (e.g., 5001)
Or kill the process using port 5000
```

## Security Best Practices

1. **Change Secret Key**: Edit `SECRET_KEY` in `.env`
2. **Use HTTPS**: Deploy behind reverse proxy with SSL
3. **Secure Database**: Restrict file permissions on SQLite file
4. **Session Expiry**: Adjust `SESSION_EXPIRY_HOURS` as needed
5. **Strong Passwords**: Implement password policy in production
6. **Backup Data**: Regularly backup `data/consent_system.db`

## Performance Tips

1. **Use pdfplumber for digital PDFs** - Much faster than Tesseract
2. **Use smaller models** - Try `llama3.1:8b` for faster responses
3. **Add indexes** - Database includes indexes on frequently queried fields
4. **Cache responses** - Implement Redis cache for repeated queries
5. **Batch processing** - Process multiple PDFs at once

## Alternative Models

Ollama supports many models. To switch:

```bash
# Pull different model
ollama pull mistral
ollama pull gemma2
ollama pull codellama

# Update .env
OLLAMA_MODEL=mistral
```

**Recommended models:**
- `llama3.1` - Best balance of speed and accuracy
- `mistral` - Fast and efficient
- `gemma2` - Good for low-resource systems
- `phi3` - Smallest, fastest

## Database Schema

### Tables

**patients**
- id (Primary Key)
- email (Unique, Indexed)
- password_hash
- patient_name
- default_password
- created_at

**consents**
- id (Primary Key)
- patient_id (Foreign Key)
- filename
- full_text
- ai_analysis_json
- processed_timestamp

**entity_index**
- id (Primary Key)
- consent_id (Foreign Key, Unique)
- patient_id (Foreign Key, Indexed)
- patient_name, patient_email, patient_dob
- doctor_name, procedure, procedure_date
- consented_items, declined_items (JSON)
- summary
- search_terms
- processed_timestamp

**sessions**
- id (Primary Key)
- patient_id (Foreign Key)
- session_token (Unique, Indexed)
- created_at
- expires_at

## Comparison with Cloud Version

| Feature | Cloud (Google) | Free (This System) |
|---------|----------------|-------------------|
| OCR | Vision API ($1.50/1K) | Tesseract (Free) |
| AI | Gemini ($0.075/1M) | Ollama (Free) |
| Database | Firestore ($0.18/GB) | SQLite (Free) |
| Hosting | Cloud Run ($50+) | Local/Free tiers |
| Privacy | Data in cloud | Data local |
| Internet | Required | Optional |
| **Cost/month** | **$100-300** | **$0** |

## Limitations

1. **Processing Speed**: Slower than cloud (especially OCR)
2. **Scalability**: Not suitable for thousands of concurrent users
3. **Model Size**: Smaller models than GPT-4/Gemini Pro
4. **Hardware**: Requires decent CPU/RAM for AI processing

## Roadmap

- [ ] Docker support
- [ ] PostgreSQL option
- [ ] Better frontend (React/Vue)
- [ ] Multi-language support
- [ ] Admin dashboard
- [ ] Email notifications
- [ ] PDF generation
- [ ] Audit logs
- [ ] Role-based access

## Contributing

Contributions welcome! Please:
1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

## License

MIT License - Use freely in personal and commercial projects!

## Support

For issues or questions:
1. Check troubleshooting section
2. Review logs: `api/app.py` has debug output
3. Test components individually
4. Open GitHub issue

## Acknowledgments

- **Ollama** - Local LLM runtime
- **Tesseract** - OCR engine
- **pdfplumber** - PDF text extraction
- **Flask** - Web framework
- **SQLAlchemy** - Database ORM

---

**Built with love for the open-source community!**

No cloud costs. No API fees. Just free software.
