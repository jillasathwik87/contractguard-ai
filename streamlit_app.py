import streamlit as st

from contract_engine import (
    analyze_contract,
    extract_contracts_from_pdf,
    answer_question,
)

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


st.success("🟢 ContractGuard AI engine is ready")

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

                pdf_bytes = uploaded_file.getvalue()

                contracts = extract_contracts_from_pdf(
                    pdf_bytes
                )

                # ------------------------------------------------
                # Multiple contracts detected
                # ------------------------------------------------

                if len(contracts) > 1:

                    st.session_state.available_contracts = list(
                        contracts.keys()
                    )

                    st.session_state.contract_documents = contracts

                    st.info(
                        "This PDF contains multiple contracts. "
                        "Please select one below."
                    )

                # ------------------------------------------------
                # Single contract detected
                # ------------------------------------------------

                else:

                    contract_name = list(
                        contracts.keys()
                    )[0]

                    contract_text = contracts[
                        contract_name
                    ]

                    data = analyze_contract(
                        contract_text,
                        contract_name
                    )

                    st.session_state.analysis = data

                    st.session_state.available_contracts = []

                    st.session_state.contract_documents = contracts

                    st.success(
                        "✅ Contract analyzed successfully!"
                    )

            except Exception as e:

                st.error(
                    f"Contract analysis failed: {e}"
                )


# ============================================================
# MULTIPLE CONTRACT SELECTION
# ============================================================

if st.session_state.available_contracts:

    selected_contract = st.selectbox(
        "Select a contract to analyze:",
        st.session_state.available_contracts,
        key="contract_selector"
    )

    if st.button(
        "📋 Analyze Selected Contract",
        type="primary",
        key="analyze_selected_contract"
    ):

        with st.spinner(
            "Analyzing selected contract..."
        ):

            try:

                contract_text = (
                    st.session_state.contract_documents[
                        selected_contract
                    ]
                )

                data = analyze_contract(
                    contract_text,
                    selected_contract
                )

                st.session_state.analysis = data

                st.session_state.selected_contract = (
                    selected_contract
                )

                st.session_state.available_contracts = []

                st.success(
                    f"✅ {selected_contract} analyzed successfully!"
                )

            except Exception as e:

                st.error(
                    f"Contract analysis failed: {e}"
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

                    data = answer_question(
                    question,
                    analysis.get("contract_text", ""),
                    analysis.get("clauses", [])
                    )

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