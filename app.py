import os
import re
import shutil
import uuid
from pathlib import Path

import gradio as gr

from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.tools import tool


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DEFAULT_PDF = BASE_DIR / "contract_compliance_dataset_10_documents.pdf"
CHROMA_DIR = BASE_DIR / "chroma_db"

LLM_MODEL = "llama3.2"
EMBED_MODEL = "nomic-embed-text"


# ============================================================
# LLM SETUP
# ============================================================

import os

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434"
)

llm = ChatOllama(
    model=LLM_MODEL,
    temperature=0,
    base_url=OLLAMA_BASE_URL
)

embeddings = OllamaEmbeddings(
    model=EMBED_MODEL,
    base_url=OLLAMA_BASE_URL
)

# ============================================================
# GLOBAL STATE
# ============================================================

STATE = {
    "documents": {},
    "selected_document": None,
    "chunks": [],
    "vectorstore": None
}


# ============================================================
# CONTRACT TYPE DETECTION
# ============================================================

def detect_contract_type(text):
    text_lower = text.lower()

    if "mutual nda" in text_lower or "confidential information" in text_lower:
        if "receiving party" in text_lower:
            return "Mutual NDA"

    if "service agreement" in text_lower or "service provider" in text_lower:
        return "Service Agreement"

    if "employment agreement" in text_lower or "employee" in text_lower:
        return "Employment Agreement"

    if "consultancy agreement" in text_lower or "consultant" in text_lower:
        return "Consultancy Agreement"

    if "commercial lease" in text_lower or "lessor" in text_lower:
        return "Commercial Lease"

    return "General Contract"


# ============================================================
# DOCUMENT SEGMENTATION
# ============================================================

def split_dataset_documents(pages):
    """
    The supplied PDF contains 10 synthetic contracts.
    This function separates them into individual contracts.

    For a normal user-uploaded single-contract PDF,
    the entire PDF becomes one document.
    """

    full_text = "\n".join(
        page.page_content for page in pages
    )

    patterns = [
        r"(?m)^1\s+—\s+Mutual NDA",
        r"(?m)^2\s+—\s+Service Agreement",
        r"(?m)^3\s+—\s+Employment Agreement",
        r"(?m)^4\s+—\s+Consultancy Agreement",
        r"(?m)^5\s+—\s+Commercial Lease",
        r"(?m)^6\s+—\s+Mutual NDA",
        r"(?m)^7\s+—\s+Service Agreement",
        r"(?m)^8\s+—\s+Employment Agreement",
        r"(?m)^9\s+—\s+Consultancy Agreement",
        r"(?m)^10\s+—\s+Commercial Lease",
    ]

    matches = []

    for pattern in patterns:
        match = re.search(pattern, full_text)
        if match:
            matches.append(match)

    if len(matches) >= 2:

        documents = {}

        for i, match in enumerate(matches):

            start = match.start()

            if i + 1 < len(matches):
                end = matches[i + 1].start()
            else:
                end = len(full_text)

            text = full_text[start:end].strip()

            title_match = re.match(
                r"(\d+\s+—\s+.+?)(?:\n|$)",
                text
            )

            if title_match:
                title = title_match.group(1).strip()
            else:
                title = f"Contract {i + 1}"

            documents[title] = text

        return documents

    # Normal single-contract PDF
    return {
        "Uploaded Contract": full_text
    }


# ============================================================
# CLAUSE-BASED SPLITTER
# ============================================================

def split_into_clauses(text):
    """
    Split on Section / numbered clause boundaries.

    This avoids splitting a legal clause in the middle.
    """

    # Normalize line endings
    text = text.replace("\r\n", "\n")

    # Section-based split
    pattern = r"(?=Section\s+\d+\b)"

    parts = re.split(pattern, text, flags=re.IGNORECASE)

    clauses = []

    for part in parts:

        part = part.strip()

        if len(part) < 20:
            continue

        clauses.append(part)

    return clauses


# ============================================================
# DETERMINISTIC COMPLIANCE RULES
# ============================================================

RULES = {

    "Mutual NDA": [

        {
            "name": "Parties",
            "keywords": ["parties:"]
        },

        {
            "name": "Effective Date",
            "keywords": ["effective date"]
        },

        {
            "name": "Purpose",
            "keywords": ["purpose:"]
        },

        {
            "name": "Confidentiality",
            "keywords": ["confidentiality"]
        },

        {
            "name": "Confidentiality Survival Period",
            "keywords": ["confidentiality obligations", "after disclosure"]
        },

        {
            "name": "Permitted Disclosure",
            "keywords": ["permitted disclosure"]
        },

        {
            "name": "Return / Destruction",
            "keywords": ["return or destruction", "return", "destroy"]
        },

        {
            "name": "Intellectual Property",
            "keywords": ["intellectual property"]
        },

        {
            "name": "Governing Law",
            "keywords": ["governing law"]
        },

        {
            "name": "Dispute Resolution",
            "keywords": ["dispute resolution"]
        },

        {
            "name": "Notices",
            "keywords": ["notices"]
        },

        {
            "name": "Amendments",
            "keywords": ["amendments"]
        },

        {
            "name": "Signatures",
            "keywords": ["signatures"]
        }
    ],

    "Service Agreement": [

        {
            "name": "Parties",
            "keywords": ["service provider", "client"]
        },

        {
            "name": "Effective Date",
            "keywords": ["effective date"]
        },

        {
            "name": "Scope of Services",
            "keywords": ["scope of services"]
        },

        {
            "name": "Term",
            "keywords": ["term:"]
        },

        {
            "name": "Payment Deadline",
            "keywords": ["payable within"]
        },

        {
            "name": "Intellectual Property",
            "keywords": ["intellectual property"]
        },

        {
            "name": "Confidentiality",
            "keywords": ["confidentiality"]
        },

        {
            "name": "Data Protection",
            "keywords": ["data protection"]
        },

        {
            "name": "Liability",
            "keywords": ["liability"]
        },

        {
            "name": "Termination",
            "keywords": ["termination"]
        },

        {
            "name": "Termination Notice Period",
            "keywords": ["days' written notice"]
        },

        {
            "name": "Force Majeure",
            "keywords": ["force majeure"]
        },

        {
            "name": "Governing Law",
            "keywords": ["governing law"]
        },

        {
            "name": "Dispute Resolution",
            "keywords": ["dispute resolution"]
        },

        {
            "name": "Notices",
            "keywords": ["notices"]
        },

        {
            "name": "Signatures",
            "keywords": ["signatures"]
        }
    ],

    "Employment Agreement": [

        {
            "name": "Parties",
            "keywords": ["employer", "employee"]
        },

        {
            "name": "Effective Date",
            "keywords": ["effective date"]
        },

        {
            "name": "Position and Duties",
            "keywords": ["position"]
        },

        {
            "name": "Compensation",
            "keywords": ["compensation"]
        },

        {
            "name": "Term",
            "keywords": ["term:"]
        },

        {
            "name": "Confidentiality",
            "keywords": ["confidentiality"]
        },

        {
            "name": "Intellectual Property",
            "keywords": ["intellectual property"]
        },

        {
            "name": "Data Protection",
            "keywords": ["data protection"]
        },

        {
            "name": "Termination",
            "keywords": ["termination"]
        },

        {
            "name": "Termination Notice Period",
            "keywords": ["days' written notice"]
        },

        {
            "name": "Return of Property",
            "keywords": ["return of property"]
        },

        {
            "name": "Governing Law",
            "keywords": ["governing law"]
        },

        {
            "name": "Dispute Resolution",
            "keywords": ["dispute resolution"]
        },

        {
            "name": "Notices",
            "keywords": ["notices"]
        },

        {
            "name": "Amendments",
            "keywords": ["amendments"]
        },

        {
            "name": "Signatures",
            "keywords": ["signatures"]
        }
    ],

    "Consultancy Agreement": [

        {
            "name": "Parties",
            "keywords": ["consultant", "client"]
        },

        {
            "name": "Effective Date",
            "keywords": ["effective date"]
        },

        {
            "name": "Services",
            "keywords": ["services"]
        },

        {
            "name": "Term",
            "keywords": ["term:"]
        },

        {
            "name": "Payment Deadline",
            "keywords": ["payable within"]
        },

        {
            "name": "Expenses",
            "keywords": ["expenses"]
        },

        {
            "name": "Confidentiality",
            "keywords": ["confidentiality"]
        },

        {
            "name": "Intellectual Property",
            "keywords": ["intellectual property"]
        },

        {
            "name": "Data Protection",
            "keywords": ["data protection"]
        },

        {
            "name": "Liability",
            "keywords": ["liability"]
        },

        {
            "name": "Termination",
            "keywords": ["termination"]
        },

        {
            "name": "Termination Notice Period",
            "keywords": ["days' written notice"]
        },

        {
            "name": "Force Majeure",
            "keywords": ["force majeure"]
        },

        {
            "name": "Governing Law",
            "keywords": ["governing law"]
        },

        {
            "name": "Dispute Resolution",
            "keywords": ["dispute resolution"]
        },

        {
            "name": "Notices",
            "keywords": ["notices"]
        },

        {
            "name": "Amendments",
            "keywords": ["amendments"]
        },

        {
            "name": "Signatures",
            "keywords": ["signatures"]
        }
    ],

    "Commercial Lease": [

        {
            "name": "Parties",
            "keywords": ["lessor", "lessee"]
        },

        {
            "name": "Property",
            "keywords": ["property"]
        },

        {
            "name": "Commencement Date",
            "keywords": ["commencement date"]
        },

        {
            "name": "Term",
            "keywords": ["term:"]
        },

        {
            "name": "Rent",
            "keywords": ["rent:"]
        },

        {
            "name": "Security Deposit",
            "keywords": ["security deposit"]
        },

        {
            "name": "Renewal",
            "keywords": ["renewal"]
        },

        {
            "name": "Maintenance",
            "keywords": ["maintenance"]
        },

        {
            "name": "Termination",
            "keywords": ["termination"]
        },

        {
            "name": "Confidentiality",
            "keywords": ["confidentiality"]
        },

        {
            "name": "Force Majeure",
            "keywords": ["force majeure"]
        },

        {
            "name": "Governing Law",
            "keywords": ["governing law"]
        },

        {
            "name": "Dispute Resolution",
            "keywords": ["dispute resolution"]
        },

        {
            "name": "Notices",
            "keywords": ["notices"]
        },

        {
            "name": "Amendments",
            "keywords": ["amendments"]
        },

        {
            "name": "Signatures",
            "keywords": ["signatures"]
        }
    ],

    "General Contract": [

        {
            "name": "Parties",
            "keywords": ["parties"]
        },

        {
            "name": "Effective Date",
            "keywords": ["effective date"]
        },

        {
            "name": "Term",
            "keywords": ["term"]
        },

        {
            "name": "Confidentiality",
            "keywords": ["confidentiality"]
        },

        {
            "name": "Termination",
            "keywords": ["termination"]
        },

        {
            "name": "Liability",
            "keywords": ["liability"]
        },

        {
            "name": "Governing Law",
            "keywords": ["governing law"]
        },

        {
            "name": "Dispute Resolution",
            "keywords": ["dispute resolution"]
        },

        {
            "name": "Notices",
            "keywords": ["notices"]
        },

        {
            "name": "Signatures",
            "keywords": ["signatures"]
        }
    ]
}


# ============================================================
# DETERMINISTIC CHECKER
# ============================================================

def check_rule(contract_text, rule):

    text = contract_text.lower()

    found = all(
        keyword.lower() in text
        for keyword in rule["keywords"]
    )

    if not found:
        return {
            "status": "MISSING",
            "reason": "Required clause/detail was not detected."
        }

    # Special deterministic checks

    name = rule["name"]

    if name == "Confidentiality Survival Period":

        patterns = [
            r"confidentiality obligations.*?\d+\s+years?",
            r"obligations.*?\d+\s+years?.*?after",
            r"confidential.*?\d+\s+years?.*?after"
        ]

        if any(re.search(p, text, re.IGNORECASE)
               for p in patterns):

            return {
                "status": "PASS",
                "reason": "A confidentiality survival period was detected."
            }

        return {
            "status": "FAIL",
            "reason": "Confidentiality exists, but a survival period was not detected."
        }

    if name == "Payment Deadline":

        if re.search(
            r"payable\s+(within|on|by).*?\d+\s+days?",
            text,
            re.IGNORECASE
        ):
            return {
                "status": "PASS",
                "reason": "A payment deadline was detected."
            }

        return {
            "status": "FAIL",
            "reason": "Payment terms exist, but a clear payment deadline was not detected."
        }

    if name == "Termination Notice Period":

        if re.search(
            r"\d+\s+days?['’]?\s+written\s+notice",
            text,
            re.IGNORECASE
        ):
            return {
                "status": "PASS",
                "reason": "A numerical termination notice period was detected."
            }

        return {
            "status": "FAIL",
            "reason": "Termination exists, but a specific notice period was not detected."
        }

    if name == "Liability":

        if re.search(
            r"liability.*?(limited|limit|aggregate)",
            text,
            re.IGNORECASE
        ):
            return {
                "status": "PASS",
                "reason": "A liability limitation was detected."
            }

        return {
            "status": "FAIL",
            "reason": "A liability clause exists but a limitation was not detected."
        }

    return {
        "status": "PASS",
        "reason": "Required clause detected."
    }


# ============================================================
# TOOL 1
# CLAUSE SIMPLIFICATION + CHECKLIST
# ============================================================

@tool
def simplify_and_check_contract(contract_text: str) -> str:
    """
    Automatically simplifies contract clauses into plain English and
    runs deterministic compliance checks.

    The checklist checks required clause types using predefined
    regex/keyword rules. Each rule returns PASS when the expected
    clause/detail is detected, FAIL when a clause exists but a required
    detail such as a deadline is missing, or MISSING when the required
    clause is not detected.

    The tool returns a plain-English summary followed by a deterministic
    compliance checklist containing PASS, FAIL, or MISSING statuses.
    """

    contract_type = detect_contract_type(contract_text)

    clauses = split_into_clauses(contract_text)

    rules = RULES.get(
        contract_type,
        RULES["General Contract"]
    )

    checklist = []

    for rule in rules:

        result = check_rule(
            contract_text,
            rule
        )

        checklist.append({
            "clause": rule["name"],
            "status": result["status"],
            "reason": result["reason"]
        })

    # --------------------------------------------------------
    # LLM simplification
    # --------------------------------------------------------

    clause_text = "\n\n".join(clauses[:20])

    prompt = f"""
You are a contract plain-English assistant.

Contract type:
{contract_type}

Rewrite the following clauses into simple English.

Rules:
- Do not add facts that are not present.
- Do not give legal advice.
- Preserve important dates, deadlines, amounts and obligations.
- Keep the explanation concise.
- Organize by clause/section.

Contract:

{clause_text}
"""

    response = llm.invoke(prompt)

    summary = response.content

    # --------------------------------------------------------
    # Format deterministic checklist
    # --------------------------------------------------------

    output = []

    output.append(
        f"# Contract Type\n{contract_type}\n"
    )

    output.append(
        "# Plain-English Summary\n"
    )

    output.append(summary)

    output.append(
        "\n\n# Deterministic Compliance Checklist\n"
    )

    for item in checklist:

        output.append(
            f"- **{item['status']}** — "
            f"{item['clause']}: "
            f"{item['reason']}"
        )

    return "\n".join(output)


# ============================================================
# TOOL 2
# RETRIEVE EXACT CONTRACT TEXT
# ============================================================

@tool
def retrieve_contract_text(query: str) -> str:
    """
    Retrieves the exact contract clause text relevant to a user question.

    The result must be used as the source text for answering follow-up
    questions. It returns the original retrieved clause text so the
    answer can cite the exact clause rather than relying on memory.
    """

    vectorstore = STATE.get("vectorstore")

    if vectorstore is None:
        return "No contract has been loaded."

    docs = vectorstore.similarity_search(
        query,
        k=3
    )

    if not docs:
        return "No matching contract clause was found."

    results = []

    for i, doc in enumerate(docs, start=1):

        results.append(
            f"--- Retrieved Clause {i} ---\n"
            f"{doc.page_content}\n"
        )

    return "\n".join(results)


# ============================================================
# CREATE VECTOR STORE
# ============================================================

def build_vectorstore(contract_text, contract_name):
    clauses = split_into_clauses(contract_text)

    if not clauses:
        clauses = [contract_text]

    # Create a unique Chroma directory for this uploaded contract.
    # This prevents Windows file-locking problems when a previous
    # Chroma database is still being used.
    unique_id = uuid.uuid4().hex[:12]
    contract_db_dir = CHROMA_DIR / unique_id

    contract_db_dir.mkdir(parents=True, exist_ok=True)

    vectorstore = Chroma.from_texts(
        texts=clauses,
        embedding=embeddings,
        persist_directory=str(contract_db_dir),
        collection_name="contract_clauses"
    )

    STATE["vectorstore"] = vectorstore
    STATE["chroma_dir"] = str(contract_db_dir)
    STATE["selected_document"] = contract_name

    return vectorstore

# ============================================================
# VERIFY RETRIEVAL
# ============================================================

def test_retrieval():

    if STATE["vectorstore"] is None:
        return "Vector store not initialized."

    query = "what is the termination notice period?"

    docs = STATE["vectorstore"].similarity_search(
        query,
        k=1
    )

    if not docs:
        return "Retrieval test failed."

    return (
        "### Retrieval Test\n\n"
        f"**Query:** {query}\n\n"
        f"**Retrieved clause:**\n\n"
        f"> {docs[0].page_content}"
    )


# ============================================================
# PROCESS PDF
# ============================================================

def process_pdf(file_path):

    if not file_path:
        return (
            "Please upload a PDF.",
            "",
            gr.update(choices=[], value=None),
            ""
        )

    try:

        loader = PyPDFLoader(file_path)

        pages = loader.load()

        documents = split_dataset_documents(pages)

        STATE["documents"] = documents

        choices = list(documents.keys())

        # Automatically select first document
        selected = choices[0]

        STATE["selected_document"] = selected

        contract_text = documents[selected]

        contract_type = detect_contract_type(
            contract_text
        )

        build_vectorstore(
            contract_text,
            selected
        )

        # ----------------------------------------------------
        # AUTOMATIC CHECK
        # ----------------------------------------------------

        analysis = simplify_and_check_contract.invoke(
            {
                "contract_text": contract_text
            }
        )

        retrieval_test = test_retrieval()

        return (
            analysis,
            retrieval_test,
            gr.update(
                choices=choices,
                value=selected
            ),
            f"Loaded **{selected}**\n\nType: **{contract_type}**"
        )

    except Exception as e:

        return (
            f"Error processing PDF:\n\n{str(e)}",
            "",
            gr.update(choices=[], value=None),
            ""
        )


# ============================================================
# SELECT CONTRACT
# ============================================================

def select_contract(contract_name):

    if not contract_name:
        return "", "", ""

    documents = STATE["documents"]

    if contract_name not in documents:
        return "", "", ""

    STATE["selected_document"] = contract_name

    contract_text = documents[contract_name]

    contract_type = detect_contract_type(
        contract_text
    )

    build_vectorstore(
        contract_text,
        contract_name
    )

    analysis = simplify_and_check_contract.invoke(
        {
            "contract_text": contract_text
        }
    )

    retrieval_test = test_retrieval()

    return (
        analysis,
        retrieval_test,
        f"Selected **{contract_name}**\n\n"
        f"Type: **{contract_type}**"
    )


# ============================================================
# FOLLOW-UP QUESTION
# ============================================================

def answer_question(question):

    if not question.strip():

        return "Please enter a question."

    if STATE["vectorstore"] is None:

        return (
            "Please upload a contract first."
        )

    # --------------------------------------------------------
    # RETRIEVE EXACT CLAUSE
    # --------------------------------------------------------

    retrieved = retrieve_contract_text.invoke(
        {
            "query": question
        }
    )

    # --------------------------------------------------------
    # ANSWER ONLY FROM RETRIEVED TEXT
    # --------------------------------------------------------

    prompt = f"""
You answer questions about a contract.

IMPORTANT RULES:

1. Answer ONLY using the retrieved contract text below.
2. Do not invent missing information.
3. If the answer is not contained in the retrieved text,
   say that the contract text retrieved does not contain
   enough information.
4. Always quote the exact relevant clause.
5. Clearly identify the source as "Retrieved contract clause".
6. Do not provide legal advice.

User question:
{question}

Retrieved contract text:
{retrieved}

Return:

Answer:
<short plain-English answer>

Retrieved contract clause:
"<exact text copied from the retrieved result>"

Source:
Contract retrieval
"""

    response = llm.invoke(prompt)

    return response.content


# ============================================================
# GRADIO UI
# ============================================================

DISCLAIMER = """
⚠️ **DISCLAIMER:** This application is for educational and
demonstration purposes only. It is not a substitute for review
by a licensed lawyer or qualified legal professional.
"""


with gr.Blocks(
    title="Contract Compliance Agent"
) as demo:

    gr.Markdown(
        """
# 📄 Contract Compliance Agent

Upload a contract and the agent will **automatically**:

1. Extract the contract
2. Identify its clauses
3. Rewrite important clauses in plain English
4. Run deterministic compliance checks
5. Show PASS / FAIL / MISSING results
6. Build a searchable contract vector store
7. Answer follow-up questions using retrieved contract text
8. Cite the exact clause used for the answer
"""
    )

    gr.Markdown(DISCLAIMER)

    # --------------------------------------------------------
    # UPLOAD
    # --------------------------------------------------------

    with gr.Row():

        upload = gr.File(
            label="Upload Contract PDF",
            file_types=[".pdf"],
            type="filepath"
        )

        contract_selector = gr.Dropdown(
            label="Contract in uploaded PDF",
            choices=[],
            interactive=True
        )

    contract_status = gr.Markdown()

    # --------------------------------------------------------
    # ANALYSIS
    # --------------------------------------------------------

    gr.Markdown(
        "## 🔎 Automatic Contract Analysis"
    )

    analysis_output = gr.Markdown(
        value="Upload a PDF. Analysis will run automatically."
    )

    # --------------------------------------------------------
    # RETRIEVAL TEST
    # --------------------------------------------------------

    gr.Markdown(
        "## 🧪 Retrieval Test"
    )

    retrieval_output = gr.Markdown()

    # --------------------------------------------------------
    # QUESTIONS
    # --------------------------------------------------------

    gr.Markdown(
        "## 💬 Ask About the Contract"
    )

    question = gr.Textbox(
        label="Your question",
        placeholder=(
            "Example: What is the termination notice period?"
        )
    )

    ask_button = gr.Button(
        "Ask Question",
        variant="primary"
    )

    answer_output = gr.Markdown()

    # --------------------------------------------------------
    # EVENTS
    # --------------------------------------------------------

    upload.change(
        fn=process_pdf,
        inputs=upload,
        outputs=[
            analysis_output,
            retrieval_output,
            contract_selector,
            contract_status
        ]
    )

    contract_selector.change(
        fn=select_contract,
        inputs=contract_selector,
        outputs=[
            analysis_output,
            retrieval_output,
            contract_status
        ]
    )

    ask_button.click(
        fn=answer_question,
        inputs=question,
        outputs=answer_output
    )

    question.submit(
        fn=answer_question,
        inputs=question,
        outputs=answer_output
    )


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("CONTRACT COMPLIANCE AGENT")
    print("=" * 60)

    print("\nStarting Gradio application...")

    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        inbrowser=True
    )
