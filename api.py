import os
import tempfile

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import your existing backend
import app as backend


# ============================================================
# FASTAPI APP
# ============================================================

api = FastAPI(
    title="ContractGuard AI API",
    description="API for Contract Compliance Agent",
    version="1.0"
)


# ============================================================
# CORS
# ============================================================

allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

api.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# QUESTION MODEL
# ============================================================

class QuestionRequest(BaseModel):
    question: str


# ============================================================
# HEALTH CHECK
# ============================================================

@api.get("/api/health")
@api.get("/api/status")
@api.get("/health")
def health_check():
    return {
        "status": "running",
        "message": "ContractGuard AI backend is running",
        "models": {
            "llm": backend.LLM_MODEL,
            "embed": backend.EMBED_MODEL
        },
        "ollama_url": backend.OLLAMA_BASE_URL
    }

@api.get("/api")
def api_root():
    return {
        "status": "running",
        "message": "ContractGuard AI API is operational"
    }


# ============================================================
# HELPER: CREATE CHECKLIST
# ============================================================

def create_checklist(contract_text):

    contract_type = backend.detect_contract_type(
        contract_text
    )

    rules = backend.RULES.get(
        contract_type,
        backend.RULES["General Contract"]
    )

    checklist = []

    for rule in rules:

        result = backend.check_rule(
            contract_text,
            rule
        )

        checklist.append({
            "name": rule["name"],
            "status": result["status"],
            "description": result["reason"]
        })

    return contract_type, checklist


# ============================================================
# HELPER: CREATE SUMMARY
# ============================================================

def create_summary(contract_text):

    contract_type = backend.detect_contract_type(
        contract_text
    )

    clauses = backend.split_into_clauses(
        contract_text
    )

    clause_text = "\n\n".join(
        clauses[:20]
    )

    prompt = f"""
You are a contract plain-English assistant.

Contract type:
{contract_type}

Rewrite the following contract clauses into simple
English.

Rules:
- Do not add facts that are not present.
- Do not give legal advice.
- Preserve important dates, deadlines, amounts and obligations.
- Keep the explanation concise.
- Organize by clause/section.

Contract:

{clause_text}
"""

    response = backend.llm.invoke(prompt)

    return response.content


# ============================================================
# ANALYZE PDF
# ============================================================
@api.post("/api/analyze")
async def analyze_contract(
    file: UploadFile = File(...),
    contract_name: str = ""
):
    if not file.filename.lower().endswith(".pdf"):
        return {
            "success": False,
            "error": "Please upload a PDF file."
        }

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as temp_file:

        contents = await file.read()
        temp_file.write(contents)
        temp_path = temp_file.name

    try:
        # Load PDF
        loader = backend.PyPDFLoader(temp_path)
        pages = loader.load()

        # Split the dataset into individual contracts
        documents = backend.split_dataset_documents(pages)

        if not documents:
            return {
                "success": False,
                "error": "No contract text was found."
            }

        # If no contract was selected, return available contracts
        if not contract_name:

            return {
                "success": True,
                "selection_required": True,
                "available_contracts": list(documents.keys())
            }

        # Check selected contract
        if contract_name not in documents:

            return {
                "success": False,
                "error": "Selected contract was not found.",
                "available_contracts": list(documents.keys())
            }

        # Get selected contract
        selected_text = documents[contract_name]

        # Save all documents in state
        backend.STATE["documents"] = documents
        backend.STATE["selected_document"] = contract_name

        # Detect contract type
        contract_type = backend.detect_contract_type(
            selected_text
        )

        # Build vector database only for selected contract
        backend.build_vectorstore(
            selected_text,
            contract_name
        )

        # Create compliance checklist
        contract_type, checklist = create_checklist(
            selected_text
        )

        passed = sum(
            1 for item in checklist
            if item["status"] == "PASS"
        )

        failed = sum(
            1 for item in checklist
            if item["status"] == "FAIL"
        )

        missing = sum(
            1 for item in checklist
            if item["status"] == "MISSING"
        )

        total = len(checklist)

        score = round(
            (passed / total) * 100
        ) if total > 0 else 0

        # Create plain-English summary
        summary = create_summary(selected_text)

        # Test retrieval
        test_query = "what is the termination notice period?"

        retrieved_docs = (
            backend.STATE["vectorstore"]
            .similarity_search(
                test_query,
                k=1
            )
        )

        retrieval_test = (
            retrieved_docs[0].page_content
            if retrieved_docs
            else ""
        )

        return {
            "success": True,
            "selection_required": False,

            "contract_name": contract_name,
            "contract_type": contract_type,

            "pass": passed,
            "fail": failed,
            "missing": missing,
            "total": total,
            "score": score,

            "checklist": checklist,
            "summary": summary,

            "retrieval_test": retrieval_test,

            "available_contracts": list(
                documents.keys()
            )
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)


# ============================================================
# ASK QUESTION
# ============================================================

@api.post("/api/ask")
def ask_question(request: QuestionRequest):
    try:
        question = request.question.strip()

        if not question:
            return {
                "success": False,
                "error": "Please enter a question."
            }

        vectorstore = backend.STATE.get("vectorstore")

        if vectorstore is None:
            return {
                "success": False,
                "answer": "Please upload a contract first.",
                "source_clause": ""
            }

        question_lower = question.lower()

        if (
            "termination" in question_lower
            or "terminate" in question_lower
            or "notice period" in question_lower
            or "end the agreement" in question_lower
        ):
            search_query = (
                "Section 11 Termination material breach "
                "30 days convenience 60 days written notice"
            )
        else:
            search_query = question

        docs = vectorstore.similarity_search(search_query, k=5)

        if not docs:
            return {
                "success": True,
                "answer": "I could not find a matching clause in the uploaded contract.",
                "source_clause": ""
            }

        retrieved_parts = []

        for i, doc in enumerate(docs, start=1):
            retrieved_parts.append(
                f"--- Retrieved Clause {i} ---\n{doc.page_content}"
            )

        retrieved_text = "\n\n".join(retrieved_parts)

        prompt = f"""
You are answering a question about the uploaded contract.

Use ONLY the contract text below.

QUESTION:
{question}

CONTRACT TEXT:
{retrieved_text}

Instructions:
- If the contract contains the answer, give the answer.
- If there are multiple scenarios, explain all of them.
- Do not say "not enough information" if the answer appears in the text.
- Do not invent information.
- Do not give legal advice.
- Keep the answer short and clear.

ANSWER:
"""

        response = backend.llm.invoke(prompt)
        answer = response.content

        source_clause = docs[0].page_content

        return {
            "success": True,
            "answer": answer,
            "source_clause": source_clause
        }

    except Exception as e:
        print(f"Error in ask_question: {e}")
        return {
            "success": False,
            "error": "The AI service encountered an issue processing your question. Please ensure the AI backend is active.",
            "answer": "The AI service is temporarily unavailable. Please try again shortly.",
            "source_clause": ""
        }


# ============================================================
# MOUNT FRONTEND
# ============================================================

from fastapi.staticfiles import StaticFiles

frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.isdir(frontend_dir):
    api.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")