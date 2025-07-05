# Customer Support AI Classifier

Automatically classify customer support tickets using LangGraph, Instructor, and Pydantic.

## Features

- AI-powered ticket classification with structured outputs
- Web interface built with Streamlit
- Batch processing via CSV upload
- Basic assertion-based evaluation suite

## Installation

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
cd customer_support_ai
pip install -r requirements.txt
```

## Configuration

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

### Web Interface

```bash
streamlit run streamlit_ui/app.py
```

### Programmatic Usage

```python
from app.classifier import TicketClassifier

classifier = TicketClassifier()
result = classifier.classify_ticket("My order arrived damaged")

print(f"Category: {result.category}")
print(f"Confidence: {result.confidence}")
```

### Batch Processing

```python
import pandas as pd
from app.classifier import TicketClassifier

df = pd.read_csv('tickets.csv')
classifier = TicketClassifier()

for ticket in df['ticket']:
    result = classifier.classify_ticket(ticket)
    print(f"{ticket} -> {result.category}")
```

## Project Structure

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🙏 Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) for the workflow orchestration
- [Instructor](https://github.com/jxnl/instructor) for structured LLM outputs
- [Pydantic](https://github.com/pydantic/pydantic) for data validation
- [Streamlit](https://streamlit.io/) for the beautiful web interface

---

⭐ **If this project helped you, please give it a star!** ⭐

## Supported Categories

- Shipping & Tracking
- Order Issue (Missing, Damaged, Wrong Item)
- Product Question - Bought Online
- Product Question - Bought In Store
- Wholesale Inquiry
- Collab or Sponsorship
- Website or Tech Issue
- Something Else

## Testing

```bash
# Run all tests
pytest -m evals/test_classification_assertions.py -v

# Run tests that don't require API key
pytest -m evals/test_classification_assertions.py -v -m "not skipif"
```
