# 🛡️ ContractGuardAI

ContractGuardAI is an AI-powered contract analysis assistant designed to help users understand contracts, identify important clauses, detect potential risks, and extract key information from legal documents.

## 🚀 Features

- 📄 Upload and analyze contracts
- 🤖 AI-powered contract understanding
- 🔍 Identify important clauses
- ⚠️ Detect potential risks and unusual terms
- 📌 Extract key contract information
- 📅 Identify important dates and deadlines
- 💰 Analyze payment and financial terms
- 👥 Identify parties and responsibilities
- 📝 Generate easy-to-understand contract summaries
- 💬 Ask questions about uploaded contracts
- 🌐 Web-based interface
- 📱 Mobile-friendly design

## 🎯 Problem Statement

Contracts can contain complex legal language that is difficult for users to understand.

ContractGuardAI helps simplify contract information by presenting important clauses, obligations, deadlines, and potential areas of concern in a clearer format.

> **Note:** ContractGuardAI is an AI assistance tool and does not provide legal advice. Users should consult a qualified legal professional for legal decisions.

## 🏗️ How It Works

```text
User
  │
  ▼
Upload Contract
  │
  ▼
ContractGuardAI
  │
  ├── Document Processing
  ├── Text Extraction
  ├── Clause Analysis
  ├── Risk Detection
  └── AI Analysis
  │
  ▼
Contract Summary
  │
  ├── Important Clauses
  ├── Risks
  ├── Obligations
  ├── Dates
  └── Questions & Answers
````

## 🧩 Key Capabilities

### 📄 Contract Upload

Users can upload a contract document for analysis.

### 🔍 Clause Analysis

The system identifies important sections such as:

* Termination clauses
* Payment terms
* Renewal clauses
* Confidentiality clauses
* Liability clauses
* Intellectual property clauses
* Dispute resolution clauses

### ⚠️ Risk Identification

ContractGuardAI can highlight terms that may require additional attention.

Examples include:

* Automatic renewal
* Long notice periods
* Penalty clauses
* Unclear obligations
* Liability limitations
* Termination restrictions

### 🤖 AI Contract Assistant

Users can ask questions about their uploaded contract and receive responses based on the document.

Example questions:

```text
What is the termination period?

When does this contract expire?

What are my payment obligations?

Is there an automatic renewal clause?

What happens if I terminate the contract early?
```

## 🛠️ Technologies Used

* Python
* AI / LLM
* FastAPI
* HTML
* CSS
* JavaScript
* GitHub
* Render

## 📁 Project Structure

```text
contract-guardai.agent/
│
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
├── data/
│
├── api.py
├── app.py
├── agent.py
├── config.py
├── ingestion.py
├── retriever.py
├── tools.py
│
├── requirements.txt
├── requirements-public.txt
├── render.yaml
├── README.md
└── .env
```

> The exact project structure may vary depending on the current implementation.

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/badugukarthik/contract-guardai.agent.git
```

Move into the project:

```bash
cd contract-guardai.agent
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## 🔐 Environment Variables

Create a `.env` file for API keys and other private configuration.

Example:

```env
GROQ_API_KEY=your_api_key_here
```

⚠️ **Never upload your real API keys, passwords, or secrets to GitHub.**

Add `.env` to your `.gitignore` file:

```text
.env
.venv/
__pycache__/
```

## ▶️ Running Locally

If the project uses FastAPI, start the server with:

```bash
uvicorn api:app --reload
```

The application will normally be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

## 🌐 Deployment

The project can be deployed using platforms such as Render.

The repository can contain a `render.yaml` configuration file for deployment.

Example production start command:

```bash
uvicorn api_public:app --host 0.0.0.0 --port $PORT
```

After deployment, the application can be accessed through a public web URL from a computer or mobile device.

## 🔒 Security

ContractGuardAI may process sensitive documents. Users should avoid uploading confidential information unless they understand how their deployment and data storage are configured.

Important security practices:

* Never commit API keys to GitHub.
* Never commit `.env` files.
* Protect uploaded documents.
* Use environment variables for secrets.
* Use HTTPS for production deployments.
* Avoid storing sensitive documents unnecessarily.

## ⚖️ Legal Disclaimer

ContractGuardAI is an AI-powered document analysis tool.

It is **not a law firm, lawyer, or legal advisor** and does not provide legal advice.

AI-generated results may contain errors or omissions. Users should consult a qualified legal professional before making important legal or contractual decisions.

## 🔮 Future Improvements

* 📑 Support for more document formats
* 🌍 Multi-language contract analysis
* 📊 Contract risk scoring
* 🔔 Deadline reminders
* 📧 Email notifications
* 👤 User authentication
* 🗄️ Secure document storage
* 📱 Improved mobile experience
* 🔗 Contract comparison
* 🧠 Improved clause detection

## 👨‍💻 Author

**saisathwik**

GitHub:

[https://github.com/saisathwik](https://github.com/badugukarthik)

## 📄 License

This project is currently intended for educational, development, and hackathon purposes.

```

### ⚠️ Before you commit it

If your repository contains a `.env` file, **don't upload it** if it contains your actual API key.

Your repository should contain your source code and configuration templates, but secrets should stay in environment variables.

If you show me the **files inside your `contract-guardai.agent` project**, I can also make this README match your **actual project structure and features** instead of using generic filenames.
```
