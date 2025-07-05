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

## Testing

```bash
# Run all tests
pytest -m evals/test_classification_assertions.py -v

# Run tests that don't require API key
pytest -m evals/test_classification_assertions.py -v -m "not skipif"
```

## 🚀 CI/CD with GitHub Actions

This project includes automated testing using GitHub Actions.

### Setting Up GitHub Actions

1. **Configure Actions Permissions**

   Go to your GitHub repository → Settings → Actions → General

   **Actions permissions:**
   - Select "Allow all actions and reusable workflows"
   - This allows the repository to use any GitHub Actions from the marketplace

   **Workflow permissions:**
   - Select "Read and write permissions"
   - This allows workflows to read repository contents and write back results (like test reports, artifacts, etc.)
   - Check "Allow GitHub Actions to create and approve pull requests" if you want automated PR creation

2. **Copy Workflow Files**

   Copy the existing GitHub workflow files from the root of this project:
   - Copy `.github/workflows/` directory from the project root
   - Place it in the root of your repository (not inside `customer_support_ai/`)
   - Adjust file paths in the workflow files if your project structure differs

   **Important:** The workflow files expect the Python code to be in the `customer_support_ai/` directory. If your structure is different, update the paths in the workflow YAML files accordingly.

### GitHub Secrets Setup

1. **Navigate to Repository Settings**
   - Go to your GitHub repository
   - Click on "Settings" tab
   - Select "Secrets and variables" → "Actions"

2. **Add Required Secrets**
   - Click "New repository secret"
   - Add `OPENAI_API_KEY` with your OpenAI API key
   - Add any other environment variables your app needs

3. **Optional Secrets for Deployment**
   - `DEPLOY_KEY`: SSH key or API token for deployment
   - `DOCKER_USERNAME` & `DOCKER_PASSWORD`: For Docker Hub
   - `AWS_ACCESS_KEY_ID` & `AWS_SECRET_ACCESS_KEY`: For AWS deployment

### Workflow Features

- **Automated Testing**: Runs on every push and pull request to `main`
- **Environment Isolation**: Each job runs in a fresh Ubuntu environment
- **Secure Secrets**: API keys and sensitive data are encrypted
- **Branch Protection**: Only trigger from `main` branch
- **Status Checks**: See test results directly in pull requests

### Troubleshooting

- **Tests failing**: Check if all required secrets are set
- **API rate limits**: Consider using test mocks for frequent runs
- **Dependencies**: Ensure `requirements.txt` is up to date
- **Permission errors**: Verify Actions permissions are set to "Allow all actions and reusable workflows"
- **Workflow not running**: Check that Workflow permissions are set to "Read and write permissions"

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

TEST PR