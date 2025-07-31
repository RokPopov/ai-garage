# Legal Document Intake System

Automatically extract data from legal documents (employment contracts & payslips) using AI powered processing with LangGraph, Docling, and OpenAI.

## ✨ Features

- **AI-Powered Document Processing**: Extract structured data from PDFs, DOCX, and images
- **Employment Contract Processing**: Extract employee details, salary, benefits, and terms
- **Payslip Data Extraction**: Parse payroll information with tax calculations
- **Professional PDF Generation**: Create formatted reports from extracted data
- **Real-time Processing**: Track document processing status with live updates
- **Modern Web Interface**: Streamlit frontend
- **RESTful API**: FastAPI backend for scalable integration

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the project root:

```env
# Copy from .env.example and add your API key
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run the Application

**Terminal 1 - Backend:**
```bash
python run_backend.py
# Backend will start at http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
python run_streamlit.py
# Frontend will start at http://localhost:8501
```

### 4. Usage

1. Open http://localhost:8501 in your browser
2. Upload an employment contract or payslip (PDF, DOCX, or image)
3. Select the document type
4. Click "Process Document"
5. Wait for AI processing to complete
6. Review extracted data and download PDF report

## 📋 Document Types Supported

### Employment Contracts
- Employee personal information
- Job details and compensation
- Benefits and allowances
- Contract terms and conditions
- Company information

### Payslips
- Employee identification
- Salary breakdowns
- Tax and deductions
- Year-to-date calculations
- Payment details

## 📁 Project Structure

```
legal_document_intake/
├
 backend/
   ├
    main.py                    # FastAPI application
   ├
    schemas.py                 # Pydantic models
   ├
    services/
   ├
    document_processor.py  # Docling integration
   ├
    extraction_service.py  # OpenAI + Instructor
   ├
    pdf_generator.py       # ReportLab PDF generation
   ├
    workflows/
   ├
    processing_workflow.py # LangGraph workflow
 ├
 streamlit_ui/
   ├
    app.py                     # Streamlit frontend
   ├
    utils.py                   # API client utilities
 ├
 tests/
   ├
    test_document_processing.py # Core functionality tests
   ├
    test_api_endpoints.py      # API endpoint tests
   ├
    __init__.py
 ├
 uploads/                       # Uploaded documents
 ├
 generated_pdfs/                # Generated PDF reports
 ├
 requirements.txt               # Python dependencies
 ├
 run_backend.py                 # Backend startup script
 ├
 run_streamlit.py               # Frontend startup script
 ├
 run_tests.py                   # Test runner
 ├
 .env.example                   # Environment template
```

## 🛠️ Technology Stack

- **Backend**: FastAPI, Pydantic, Uvicorn, Pandas
- **UI**: Streamlit
- **Document Processing**: Docling (IBM Open Source)
- **AI Integration**: OpenAI API, Instructor
- **Workflow**: LangGraph
- **PDF Generation**: ReportLab
- **Testing**: Pytest, FastAPI TestClient

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python run_tests.py

# Run specific test modules
python -m pytest tests/test_document_processing.py -v
python -m pytest tests/test_api_endpoints.py -v

# Run tests without API key (basic validation)
python -m pytest tests/ -v -m "not skipif"
```

### Test Coverage

- **Document Processing Tests**: Core functionality validation
- **API Endpoint Tests**: FastAPI route testing
- **Integration Tests**: End-to-end workflow testing
- **Data Validation Tests**: Pydantic model validation
- **Skipped Tests**: Future implementation examples (see `tests/TESTING.md`)

📚 **For detailed testing documentation, see [`tests/TESTING.md`](tests/TESTING.md)**

### Sample Documents

The system includes sample documents for demonstration:

1. **Employment Contract**: Complete contract with all fields
2. **Payslip**: Monthly payslip with tax calculations

### Demo Workflow

1. Start both backend and frontend servers
2. Upload sample employment contract
3. Show real-time processing status
4. Review extracted data in the web interface
5. Download generated PDF report
6. Repeat with payslip document
7. Demonstrate error handling with invalid files

### Key Demo Points

- **Speed**: Processing typically takes 10-30 seconds
- **Accuracy**: AI extraction with structured validation
- **User Experience**: Professional interface with progress tracking
- **Output Quality**: Professional PDF reports
- **Error Handling**: Graceful failure management

## 📚 API Documentation

### Core Endpoints

- `GET /health` - System health check
- `POST /upload` - Upload document for processing
- `GET /status/{job_id}` - Check processing status
- `GET /download/{job_id}` - Download generated PDF
- `GET /docs` - Interactive API documentation

### Example API Usage

```python
import requests

# Upload document
files = {"file": open("contract.pdf", "rb")}
data = {"document_type": "employment_contract"}
response = requests.post("http://localhost:8000/upload", files=files, data=data)
job_id = response.json()["job_id"]

# Check status
status = requests.get(f"http://localhost:8000/status/{job_id}")
print(status.json())

# Download result
pdf = requests.get(f"http://localhost:8000/download/{job_id}")
with open("result.pdf", "wb") as f:
    f.write(pdf.content)
```

## 🐛 Troubleshooting

### Common Issues

1. **"OpenAI API key not set"**
   - Solution: Add `OPENAI_API_KEY` to your `.env` file

2. **"System Unavailable"**
   - Solution: Start the backend server with `python run_backend.py`

3. **"Processing stuck"**
   - Solution: Check OpenAI API key and rate limits

4. **"Upload failed"**
   - Solution: Ensure file format is supported (PDF, DOCX, PNG, JPG)

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python run_backend.py
```

## 🚀 Production Deployment

### Environment Variables

```env
# Production settings
OPENAI_API_KEY=your_production_key
API_HOST=0.0.0.0
API_PORT=8000
MAX_FILE_SIZE=10485760
LOG_LEVEL=INFO
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📈 Performance & Scaling

- **Processing Speed**: 10-30 seconds per document
- **File Size Limit**: 10MB default (configurable)
- **Concurrent Jobs**: Memory-based queue (Redis recommended for production)
- **Rate Limits**: OpenAI API rate limits apply

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`python run_tests.py`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🙏 Acknowledgments

- [Docling](https://github.com/DS4SD/docling) - Advanced document processing
- [LangGraph](https://github.com/langchain-ai/langgraph) - Workflow orchestration
- [Instructor](https://github.com/jxnl/instructor) - Structured LLM outputs
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Streamlit](https://streamlit.io/) - Beautiful web interfaces

---

**If this project helped you, please give it a star!**
