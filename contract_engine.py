import re
from pathlib import Path
from tempfile import NamedTemporaryFile

import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from groq import Groq


# ============================================================
# GROQ
# ============================================================

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not configured.")

groq_client = Groq(api_key=GROQ_API_KEY)

LLM_MODEL = "openai/gpt-oss-20b"


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
# DATASET DOCUMENT SPLITTING
# ============================================================

def split_dataset_documents(pages):

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

    return {
        "Uploaded Contract": full_text
    }


# ============================================================
# CLAUSE SPLITTER
# ============================================================

def split_into_clauses(text):

    text = text.replace("\r\n", "\n")

    pattern = r"(?=Section\s+\d+\b)"

    parts = re.split(
        pattern,
        text,
        flags=re.IGNORECASE
    )

    clauses = []

    for part in parts:

        part = part.strip()

        if len(part) < 20:
            continue

        clauses.append(part)

    return clauses


# ============================================================
# COMPLIANCE RULES
# ============================================================

RULES = {

    "Mutual NDA": [
        {"name": "Parties", "keywords": ["parties:"]},
        {"name": "Effective Date", "keywords": ["effective date"]},
        {"name": "Purpose", "keywords": ["purpose:"]},
        {"name": "Confidentiality", "keywords": ["confidentiality"]},
        {
            "name": "Confidentiality Survival Period",
            "keywords": ["confidentiality obligations", "after disclosure"]
        },
        {"name": "Permitted Disclosure", "keywords": ["permitted disclosure"]},
        {
            "name": "Return / Destruction",
            "keywords": ["return or destruction", "return", "destroy"]
        },
        {"name": "Intellectual Property", "keywords": ["intellectual property"]},
        {"name": "Governing Law", "keywords": ["governing law"]},
        {"name": "Dispute Resolution", "keywords": ["dispute resolution"]},
        {"name": "Notices", "keywords": ["notices"]},
        {"name": "Amendments", "keywords": ["amendments"]},
        {"name": "Signatures", "keywords": ["signatures"]},
    ],

    "Service Agreement": [
        {"name": "Parties", "keywords": ["service provider", "client"]},
        {"name": "Effective Date", "keywords": ["effective date"]},
        {"name": "Scope of Services", "keywords": ["scope of services"]},
        {"name": "Term", "keywords": ["term:"]},
        {"name": "Payment Deadline", "keywords": ["payable within"]},
        {"name": "Intellectual Property", "keywords": ["intellectual property"]},
        {"name": "Confidentiality", "keywords": ["confidentiality"]},
        {"name": "Data Protection", "keywords": ["data protection"]},
        {"name": "Liability", "keywords": ["liability"]},
        {"name": "Termination", "keywords": ["termination"]},
        {"name": "Termination Notice Period", "keywords": ["days' written notice"]},
        {"name": "Force Majeure", "keywords": ["force majeure"]},
        {"name": "Governing Law", "keywords": ["governing law"]},
        {"name": "Dispute Resolution", "keywords": ["dispute resolution"]},
        {"name": "Notices", "keywords": ["notices"]},
        {"name": "Signatures", "keywords": ["signatures"]},
    ],

    "Employment Agreement": [
        {"name": "Parties", "keywords": ["employer", "employee"]},
        {"name": "Effective Date", "keywords": ["effective date"]},
        {"name": "Position and Duties", "keywords": ["position"]},
        {"name": "Compensation", "keywords": ["compensation"]},
        {"name": "Term", "keywords": ["term:"]},
        {"name": "Confidentiality", "keywords": ["confidentiality"]},
        {"name": "Intellectual Property", "keywords": ["intellectual property"]},
        {"name": "Data Protection", "keywords": ["data protection"]},
        {"name": "Termination", "keywords": ["termination"]},
        {"name": "Termination Notice Period", "keywords": ["days' written notice"]},
        {"name": "Return of Property", "keywords": ["return of property"]},
        {"name": "Governing Law", "keywords": ["governing law"]},
        {"name": "Dispute Resolution", "keywords": ["dispute resolution"]},
        {"name": "Notices", "keywords": ["notices"]},
        {"name": "Amendments", "keywords": ["amendments"]},
        {"name": "Signatures", "keywords": ["signatures"]},
    ],

    "Consultancy Agreement": [
        {"name": "Parties", "keywords": ["consultant", "client"]},
        {"name": "Effective Date", "keywords": ["effective date"]},
        {"name": "Services", "keywords": ["services"]},
        {"name": "Term", "keywords": ["term:"]},
        {"name": "Payment Deadline", "keywords": ["payable within"]},
        {"name": "Expenses", "keywords": ["expenses"]},
        {"name": "Confidentiality", "keywords": ["confidentiality"]},
        {"name": "Intellectual Property", "keywords": ["intellectual property"]},
        {"name": "Data Protection", "keywords": ["data protection"]},
        {"name": "Liability", "keywords": ["liability"]},
        {"name": "Termination", "keywords": ["termination"]},
        {"name": "Termination Notice Period", "keywords": ["days' written notice"]},
        {"name": "Force Majeure", "keywords": ["force majeure"]},
        {"name": "Governing Law", "keywords": ["governing law"]},
        {"name": "Dispute Resolution", "keywords": ["dispute resolution"]},
        {"name": "Notices", "keywords": ["notices"]},
        {"name": "Amendments", "keywords": ["amendments"]},
        {"name": "Signatures", "keywords": ["signatures"]},
    ],

    "Commercial Lease": [
        {"name": "Parties", "keywords": ["lessor", "lessee"]},
        {"name": "Property", "keywords": ["property"]},
        {"name": "Commencement Date", "keywords": ["commencement date"]},
        {"name": "Term", "keywords": ["term:"]},
        {"name": "Rent", "keywords": ["rent:"]},
        {"name": "Security Deposit", "keywords": ["security deposit"]},
        {"name": "Renewal", "keywords": ["renewal"]},
        {"name": "Maintenance", "keywords": ["maintenance"]},
        {"name": "Termination", "keywords": ["termination"]},
        {"name": "Confidentiality", "keywords": ["confidentiality"]},
        {"name": "Force Majeure", "keywords": ["force majeure"]},
        {"name": "Governing Law", "keywords": ["governing law"]},
        {"name": "Dispute Resolution", "keywords": ["dispute resolution"]},
        {"name": "Notices", "keywords": ["notices"]},
        {"name": "Amendments", "keywords": ["amendments"]},
        {"name": "Signatures", "keywords": ["signatures"]},
    ],

    "General Contract": [
        {"name": "Parties", "keywords": ["parties"]},
        {"name": "Effective Date", "keywords": ["effective date"]},
        {"name": "Term", "keywords": ["term"]},
        {"name": "Confidentiality", "keywords": ["confidentiality"]},
        {"name": "Termination", "keywords": ["termination"]},
        {"name": "Liability", "keywords": ["liability"]},
        {"name": "Governing Law", "keywords": ["governing law"]},
        {"name": "Dispute Resolution", "keywords": ["dispute resolution"]},
        {"name": "Notices", "keywords": ["notices"]},
        {"name": "Signatures", "keywords": ["signatures"]},
    ],
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

    name = rule["name"]

    if name == "Confidentiality Survival Period":

        patterns = [
            r"confidentiality obligations.*?\d+\s+years?",
            r"obligations.*?\d+\s+years?.*?after",
            r"confidential.*?\d+\s+years?.*?after"
        ]

        if any(
            re.search(p, text, re.IGNORECASE)
            for p in patterns
        ):
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
# CONTRACT ANALYSIS
# ============================================================

def analyze_contract(contract_text, contract_name="Uploaded Contract"):

    contract_type = detect_contract_type(contract_text)

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
            "name": rule["name"],
            "status": result["status"],
            "description": result["reason"]
        })

    passed = sum(
        1 for x in checklist
        if x["status"] == "PASS"
    )

    failed = sum(
        1 for x in checklist
        if x["status"] == "FAIL"
    )

    missing = sum(
        1 for x in checklist
        if x["status"] == "MISSING"
    )

    total = len(checklist)

    score = round(
        (passed / total) * 100
    ) if total else 0

    # --------------------------------------------------------
    # Groq plain-English summary
    # --------------------------------------------------------

    clauses = split_into_clauses(contract_text)

    clause_text = "\n\n".join(
        clauses[:20]
    )

    prompt = f"""
You are a contract plain-English assistant.

Contract type:
{contract_type}

Rewrite the following contract clauses into simple English.

Rules:
- Do not add facts that are not present.
- Do not give legal advice.
- Preserve important dates, deadlines, amounts and obligations.
- Keep the explanation concise.
- Organize by clause/section.

Contract:

{clause_text}
"""

    response = groq_client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    summary = response.choices[0].message.content

    return {
        "success": True,
        "contract_name": contract_name,
        "contract_type": contract_type,
        "summary": summary,
        "checklist": checklist,
        "pass": passed,
        "fail": failed,
        "missing": missing,
        "total": total,
        "score": score,
        "contract_text": contract_text,
        "clauses": clauses,
    }


# ============================================================
# PDF PROCESSING
# ============================================================

def extract_contracts_from_pdf(pdf_bytes):

    temp_path = None

    try:

        with NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp:

            temp.write(pdf_bytes)
            temp_path = temp.name

        loader = PyPDFLoader(temp_path)

        pages = loader.load()

        return split_dataset_documents(pages)

    finally:

        if temp_path:

            try:
                Path(temp_path).unlink()
            except Exception:
                pass


# ============================================================
# SIMPLE LOCAL CLAUSE RETRIEVAL
# ============================================================

def retrieve_relevant_clauses(
    question,
    contract_text,
    clauses,
    top_k=3
):

    question_words = set(
        re.findall(
            r"\b[a-zA-Z]{3,}\b",
            question.lower()
        )
    )

    scored = []

    for clause in clauses:

        clause_words = set(
            re.findall(
                r"\b[a-zA-Z]{3,}\b",
                clause.lower()
            )
        )

        score = len(
            question_words & clause_words
        )

        scored.append(
            (score, clause)
        )

    scored.sort(
        key=lambda x: x[0],
        reverse=True
    )

    selected = [
        clause
        for score, clause in scored[:top_k]
        if score > 0
    ]

    if not selected:
        selected = clauses[:top_k]

    return selected


# ============================================================
# ASK AI
# ============================================================

def answer_question(
    question,
    contract_text,
    clauses
):

    retrieved_clauses = retrieve_relevant_clauses(
        question,
        contract_text,
        clauses
    )

    retrieved_text = "\n\n".join(
        f"--- Retrieved Clause {i} ---\n{clause}"
        for i, clause in enumerate(
            retrieved_clauses,
            start=1
        )
    )

    prompt = f"""
You answer questions about a contract.

IMPORTANT RULES:

1. Answer ONLY using the retrieved contract text below.
2. Do not invent missing information.
3. If the answer is not contained in the retrieved text,
   say that the retrieved contract text does not contain
   enough information.
4. Always quote the exact relevant clause.
5. Clearly identify the source as "Retrieved contract clause".
6. Do not provide legal advice.

User question:
{question}

Retrieved contract text:
{retrieved_text}

Return:

Answer:
<short plain-English answer>

Retrieved contract clause:
"<exact text copied from the retrieved result>"

Source:
Contract retrieval
"""

    response = groq_client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response.choices[0].message.content

    source_clause = (
        retrieved_clauses[0]
        if retrieved_clauses
        else ""
    )

    return {
        "success": True,
        "answer": answer,
        "source_clause": source_clause,
    }