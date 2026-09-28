import os
import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

API_BASE = os.getenv(
    "CONTRACTGUARD_API_URL",
    "https://toolkit-isbn-statute-modelling.trycloudflare.com"
).rstrip("/")


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ContractGuard AI",
    page_icon="🛡️",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

if "available_contracts" not in st.session_state:
    st.session_state.available_contracts = []

if "selected_contract" not in st.session_state:
    st.session_state.selected_contract = ""

if "answer" not in st.session_state:
    st.session_state.answer = None


# ============================================================
# HEADER
# ============================================================

st.title("🛡️ ContractGuard AI")
st.subheader("AI Contract Compliance & Plain-English Assistant")

st.info(
    "Upload a contract to automatically generate a plain-English "
    "summary and compliance checklist."
)

st.warning(
    "⚖️ This tool is not a substitute for a licensed lawyer's review."
)


# ============================================================
# BACKEND STATUS
# ============================================================

try:
    health = requests.get(
        f"{API_BASE}/api/health",
        timeout=5
    )

    if health.ok:
        st.success("🟢 ContractGuard backend is connected")
    else:
        st.error("🔴 Backend is not responding correctly")

except Exception:
    st.error(
        f"🔴 Cannot connect to backend at {API_BASE}"
    )


# ============================================================
# CONTRACT UPLOAD
# ============================================================

st.header("📄 Upload Contract")

uploaded_file = st.file_uploader(
    "Choose a PDF contract",
    type=["pdf"]
)


if uploaded_file is not None:

    st.session_state.uploaded_file = uploaded_file

    if st.button(
        "🔍 Analyze Contract",
        type="primary"
    ):

        with st.spinner(
            "Analyzing contract... Please wait."
        ):

            try:

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf"
                    )
                }

                response = requests.post(
                    f"{API_BASE}/api/analyze",
                    files=files,
                    timeout=300
                )

                data = response.json()

                if not data.get("success"):

                    st.error(
                        data.get(
                            "error",
                            "Contract analysis failed."
                        )
                    )

                elif data.get("selection_required"):

                    st.session_state.available_contracts = (
                        data.get(
                            "available_contracts",
                            []
                        )
                    )

                    st.info(
                        "This PDF contains multiple contracts. "
                        "Please select one below."
                    )

                else:

                    st.session_state.analysis = data
                    st.session_state.available_contracts = []

                    st.success(
                        "✅ Contract analyzed successfully!"
                    )

            except Exception as e:

                st.error(
                    f"Error connecting to backend: {e}"
                )


# ============================================================
# MULTIPLE CONTRACT SELECTION
# ============================================================

if st.session_state.available_contracts:

    st.header("📑 Select Contract")

    selected = st.selectbox(
        "Choose the contract you want to analyze",
        st.session_state.available_contracts
    )

    if st.button(
        "Analyze Selected Contract",
        type="primary"
    ):

        with st.spinner(
            "Analyzing selected contract..."
        ):

            try:

                original_file = (
                    st.session_state.uploaded_file
                )

                files = {
                    "file": (
                        original_file.name,
                        original_file.getvalue(),
                        "application/pdf"
                    )
                }

                response = requests.post(
                    f"{API_BASE}/api/analyze",
                    params={
                        "contract_name": selected
                    },
                    files=files,
                    timeout=300
                )

                data = response.json()

                if data.get("success"):

                    st.session_state.analysis = data
                    st.session_state.selected_contract = selected

                    st.success(
                        "✅ Selected contract analyzed successfully!"
                    )

                else:

                    st.error(
                        data.get(
                            "error",
                            "Analysis failed."
                        )
                    )

            except Exception as e:

                st.error(
                    f"Error connecting to backend: {e}"
                )


# ============================================================
# DISPLAY ANALYSIS
# ============================================================

analysis = st.session_state.analysis


if analysis:

    st.divider()

    st.header("📊 Compliance Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Score",
            f"{analysis.get('score', 0)}%"
        )

    with col2:
        st.metric(
            "PASS",
            analysis.get("pass", 0)
        )

    with col3:
        st.metric(
            "MISSING",
            analysis.get("missing", 0)
        )

    with col4:
        st.metric(
            "FAIL",
            analysis.get("fail", 0)
        )

    st.write(
        f"**Contract:** "
        f"{analysis.get('contract_name', 'Uploaded Contract')}"
    )

    st.write(
        f"**Contract Type:** "
        f"{analysis.get('contract_type', 'Unknown')}"
    )


    # ========================================================
    # PLAIN ENGLISH SUMMARY
    # ========================================================

    st.divider()

    st.header("📝 Plain-English Summary")

    summary = analysis.get(
        "summary",
        "No summary available."
    )

    st.markdown(summary)


    # ========================================================
    # CHECKLIST
    # ========================================================

    st.divider()

    st.header("✅ Compliance Checklist")

    checklist = analysis.get(
        "checklist",
        []
    )

    for item in checklist:

        name = item.get(
            "name",
            "Unknown"
        )

        status = item.get(
            "status",
            "UNKNOWN"
        )

        description = item.get(
            "description",
            ""
        )

        if status == "PASS":

            st.success(
                f"✅ **{name}** — {description}"
            )

        elif status == "MISSING":

            st.warning(
                f"⚠️ **{name}** — {description}"
            )

        elif status == "FAIL":

            st.error(
                f"❌ **{name}** — {description}"
            )

        else:

            st.info(
                f"ℹ️ **{name}** — {description}"
            )


    # ========================================================
    # FOLLOW-UP QUESTIONS
    # ========================================================

    st.divider()

    st.header("💬 Ask About This Contract")

    question = st.text_input(
        "Ask a question about the analyzed contract",
        placeholder="Example: What is the confidentiality period?"
    )

    if st.button(
        "Ask AI",
        type="primary"
    ):

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            with st.spinner(
                "Searching the contract and generating an answer..."
            ):

                try:

                    response = requests.post(
                        f"{API_BASE}/api/ask",
                        json={
                            "question": question
                        },
                        timeout=300
                    )

                    data = response.json()

                    if data.get("success"):

                        st.session_state.answer = data

                    else:

                        st.error(
                            data.get(
                                "error",
                                "Could not answer the question."
                            )
                        )

                except Exception as e:

                    st.error(
                        f"Error connecting to backend: {e}"
                    )


# ============================================================
# ANSWER + SOURCE CLAUSE
# ============================================================

if st.session_state.answer:

    answer_data = st.session_state.answer

    st.subheader("🤖 Answer")

    st.write(
        answer_data.get(
            "answer",
            "No answer available."
        )
    )

    source_clause = answer_data.get(
        "source_clause",
        ""
    )

    if source_clause:

        st.subheader("📌 Source Clause")

        st.code(
            source_clause,
            language="text"
        )

        st.caption(
            "The answer above was generated using the retrieved "
            "contract clause shown here."
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "ContractGuard AI — Contract Compliance Assistant"
)

st.caption(
    "⚖️ Not a substitute for a licensed lawyer's review."
)