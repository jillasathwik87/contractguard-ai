// =====================================================
// CONTRACTGUARD AI - CONTRACTS PAGE
// =====================================================

const API_BASE = typeof getApiBaseUrl === "function" ? getApiBaseUrl() : "http://127.0.0.1:8000";


// =====================================================
// ELEMENTS
// =====================================================

const contractFile = document.getElementById("contractFile");
const chooseFileButton = document.getElementById("chooseFileButton");
const analyzeButton = document.getElementById("analyzeButton");

const selectedFileText = document.getElementById("selectedFile");
const contractStatus = document.getElementById("contractStatus");

const contractSelectionArea =
    document.getElementById("contractSelectionArea");

const contractSelector =
    document.getElementById("contractSelector");

const analysisResults =
    document.getElementById("analysisResults");

const resultContractName =
    document.getElementById("resultContractName");

const resultContractType =
    document.getElementById("resultContractType");

const resultPassed =
    document.getElementById("resultPassed");

const resultFailed =
    document.getElementById("resultFailed");

const resultMissing =
    document.getElementById("resultMissing");

const resultScore =
    document.getElementById("resultScore");

const scoreBar =
    document.getElementById("scoreBar");

const resultStatus =
    document.getElementById("resultStatus");

const checklistContainer =
    document.getElementById("checklistContainer");

const summaryContainer =
    document.getElementById("summaryContainer");

const sourceContainer =
    document.getElementById("sourceContainer");


// =====================================================
// VARIABLES
// =====================================================

let selectedFile = null;


// =====================================================
// CHOOSE PDF
// =====================================================

if (chooseFileButton && contractFile) {

    chooseFileButton.addEventListener("click", function () {

        contractFile.click();

    });

}


// =====================================================
// FILE SELECTED
// =====================================================

if (contractFile) {

    contractFile.addEventListener("change", async function () {

        const file = contractFile.files[0];

        if (!file) {
            return;
        }


        // Check PDF
        const isPDF =
            file.type === "application/pdf" ||
            file.name.toLowerCase().endsWith(".pdf");


        if (!isPDF) {

            alert("Please select a PDF contract.");

            contractFile.value = "";

            return;
        }


        selectedFile = file;

        selectedFileText.textContent =
            file.name;

        contractStatus.textContent =
            "Reading available contracts...";

        analyzeButton.disabled = true;

        analysisResults.style.display = "none";


        try {

            // =================================================
            // FIRST REQUEST
            // Get available contracts from the dataset
            // =================================================

            const formData = new FormData();

            formData.append(
                "file",
                selectedFile
            );


            const response = await fetch(
                `${API_BASE}/api/analyze`,
                {
                    method: "POST",
                    body: formData
                }
            );


            const data = await response.json();


            console.log(
                "Available contracts response:",
                data
            );


            if (!response.ok) {

                throw new Error(
                    data.error ||
                    data.detail ||
                    `Backend error: ${response.status}`
                );

            }


            if (!data.success) {

                throw new Error(
                    data.error ||
                    "Could not read the contract dataset."
                );

            }


            // =================================================
            // BACKEND REQUIRES CONTRACT SELECTION
            // =================================================

            if (data.selection_required) {

                showContractSelection(
                    data.available_contracts
                );

                contractStatus.textContent =
                    "Select a contract and then click Analyze Contract.";

            }


        } catch (error) {

            console.error(
                "Contract loading error:",
                error
            );


            contractStatus.textContent =
                "Could not load contracts.";


            alert(
                "Could not load contracts.\n\n" +
                error.message
            );

        }

    });

}


// =====================================================
// SHOW CONTRACT DROPDOWN
// =====================================================

function showContractSelection(
    contracts
) {

    if (!contractSelectionArea ||
        !contractSelector) {

        console.error(
            "Contract selector elements not found."
        );

        return;
    }


    // Clear old options
    contractSelector.innerHTML =
        `<option value="">
            Select a contract
        </option>`;


    contracts.forEach(function (contractName) {

        const option =
            document.createElement("option");

        option.value =
            contractName;

        option.textContent =
            contractName;

        contractSelector.appendChild(
            option
        );

    });


    // Show dropdown
    contractSelectionArea.style.display =
        "block";


    // Don't enable until user selects one
    analyzeButton.disabled = true;


    console.log(
        "Available contracts:",
        contracts
    );

}


// =====================================================
// CONTRACT SELECTED
// =====================================================

if (contractSelector) {

    contractSelector.addEventListener(
        "change",
        function () {

            if (contractSelector.value) {

                analyzeButton.disabled =
                    false;

                contractStatus.textContent =
                    "Contract selected. Ready to analyze.";

            } else {

                analyzeButton.disabled =
                    true;

                contractStatus.textContent =
                    "Please select a contract.";

            }

        }
    );

}


// =====================================================
// ANALYZE SELECTED CONTRACT
// =====================================================

if (analyzeButton) {

    analyzeButton.addEventListener(
        "click",
        async function () {

            if (!selectedFile) {

                alert(
                    "Please choose a PDF first."
                );

                return;

            }


            const selectedContract =
                contractSelector
                    ? contractSelector.value
                    : "";


            if (!selectedContract) {

                alert(
                    "Please select a contract."
                );

                return;

            }


            analyzeButton.disabled =
                true;

            analyzeButton.textContent =
                "Analyzing...";


            contractStatus.textContent =
                "Analyzing selected contract...";


            try {

                // =================================================
                // SECOND REQUEST
                // Send PDF + contract_name
                // =================================================

                const formData =
                    new FormData();


                formData.append(
                    "file",
                    selectedFile
                );


                console.log(
                    "Analyzing:",
                    selectedContract
                );


                const response =
                    await fetch(
                        `${API_BASE}/api/analyze?contract_name=${encodeURIComponent(selectedContract)}`,
                        {
                            method: "POST",
                            body: formData
                        }
                    );


                const data =
                    await response.json();
                saveAnalysisForDashboard(data);


                console.log(
                    "Analysis response:",
                    data
                );


                // =================================================
                // CHECK RESPONSE
                // =================================================

                if (!response.ok) {

                    throw new Error(
                        data.error ||
                        data.detail ||
                        `Backend error: ${response.status}`
                    );

                }


                if (!data.success) {

                    throw new Error(
                        data.error ||
                        "Contract analysis failed."
                    );

                }


                // =================================================
                // DISPLAY RESULTS
                // =================================================

                displayAnalysisResults(
                    data
                );


                contractStatus.textContent =
                    "Contract analyzed successfully.";


            } catch (error) {

                console.error(
                    "Analysis error:",
                    error
                );


                contractStatus.textContent =
                    "Analysis failed.";


                alert(
                    "Could not analyze the contract.\n\n" +
                    error.message
                );


            } finally {

                analyzeButton.disabled =
                    false;

                analyzeButton.textContent =
                    "Analyze Contract";

            }

        }
    );

}


// =====================================================
// DISPLAY RESULTS
// =====================================================

function displayAnalysisResults(data) {

    analysisResults.style.display =
        "block";


    // =================================================
    // CONTRACT NAME
    // =================================================

    resultContractName.textContent =
        data.contract_name ||
        "Selected Contract";


    // =================================================
    // CONTRACT TYPE
    // =================================================

    resultContractType.textContent =
        data.contract_type ||
        "Not available";


    // =================================================
    // PASS / FAIL / MISSING
    // =================================================

    resultPassed.textContent =
        data.pass ?? 0;


    resultFailed.textContent =
        data.fail ?? 0;


    resultMissing.textContent =
        data.missing ?? 0;


    // =================================================
    // SCORE
    // =================================================

    const score =
        Number(data.score ?? 0);


    resultScore.textContent =
        `${score}%`;


    scoreBar.style.width =
        `${score}%`;


    // =================================================
    // RESULT STATUS
    // =================================================

    if (score === 100) {

        resultStatus.textContent =
            "Fully Compliant";

        resultStatus.style.color =
            "#16a34a";

    } else if (score >= 70) {

        resultStatus.textContent =
            "Needs Review";

        resultStatus.style.color =
            "#d97706";

    } else {

        resultStatus.textContent =
            "Attention Required";

        resultStatus.style.color =
            "#dc2626";

    }


    // =================================================
    // CHECKLIST
    // =================================================

    displayChecklist(
        data.checklist || []
    );


    // =================================================
    // SUMMARY
    // =================================================

    if (data.summary) {

        summaryContainer.textContent =
            data.summary;

    } else {

        summaryContainer.textContent =
            "No summary available.";

    }


    // =================================================
    // SOURCE
    // =================================================

    if (data.retrieval_test) {

        sourceContainer.textContent =
            data.retrieval_test;

    } else {

        sourceContainer.textContent =
            "No source information available.";

    }


    // =================================================
    // SCROLL TO RESULTS
    // =================================================

    analysisResults.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

}


// =====================================================
// DISPLAY CHECKLIST
// =====================================================

function displayChecklist(checklist) {

    checklistContainer.innerHTML = "";


    if (!checklist.length) {

        checklistContainer.innerHTML = `
            <div class="empty-state">
                <h4>No checklist results</h4>
                <p>
                    No compliance rules were returned.
                </p>
            </div>
        `;

        return;

    }


    checklist.forEach(function (item) {

        const status =
            item.status || "UNKNOWN";


        const rule =
            item.rule ||
            item.name ||
            item.requirement ||
            "Compliance Rule";


        const message =
            item.message ||
            item.description ||
            item.details ||
            "";


        const row =
            document.createElement("div");


        row.style.cssText = `
            display:flex;
            align-items:center;
            gap:12px;
            padding:14px;
            margin-bottom:8px;
            border:1px solid #e5e7eb;
            border-radius:10px;
            background:#ffffff;
        `;


        let icon = "•";
        let iconBackground = "#f3f4f6";
        let iconColor = "#6b7280";
        let statusColor = "#6b7280";


        if (status === "PASS") {

            icon = "✓";
            iconBackground = "#dcfce7";
            iconColor = "#16a34a";
            statusColor = "#16a34a";

        } else if (status === "FAIL") {

            icon = "✕";
            iconBackground = "#fee2e2";
            iconColor = "#dc2626";
            statusColor = "#dc2626";

        } else if (status === "MISSING") {

            icon = "?";
            iconBackground = "#fef3c7";
            iconColor = "#d97706";
            statusColor = "#d97706";

        }


        row.innerHTML = `

            <div
                style="
                    width:32px;
                    height:32px;
                    flex-shrink:0;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    border-radius:8px;
                    background:${iconBackground};
                    color:${iconColor};
                    font-weight:700;
                "
            >
                ${icon}
            </div>


            <div style="flex:1;">

                <strong
                    style="
                        display:block;
                        font-size:11px;
                        color:#111827;
                        margin-bottom:4px;
                    "
                >
                    ${escapeHTML(rule)}
                </strong>


                ${message
                ? `
                        <span
                            style="
                                display:block;
                                font-size:9px;
                                color:#6b7280;
                                line-height:1.5;
                            "
                        >
                            ${escapeHTML(message)}
                        </span>
                    `
                : ""
            }

            </div>


            <span
                style="
                    font-size:9px;
                    font-weight:700;
                    color:${statusColor};
                "
            >
                ${escapeHTML(status)}
            </span>

        `;


        checklistContainer.appendChild(
            row
        );

    });

}


// =====================================================
// ESCAPE HTML
// =====================================================

function escapeHTML(value) {

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

}


// =====================================================
// PAGE LOADED
// =====================================================

console.log(
    "ContractGuard Contracts page loaded."
);

console.log(
    "Backend:",
    API_BASE
);
// =====================================================
// SAVE ANALYSIS FOR DASHBOARD
// =====================================================

function saveAnalysisForDashboard(data) {

    if (!data || !data.success) {
        return;
    }

    if (data.selection_required) {
        return;
    }

    const historyKey =
        "contractGuardAnalysisHistory";

    let history = [];

    const saved =
        localStorage.getItem(historyKey);

    if (saved) {

        try {

            history =
                JSON.parse(saved);

        } catch (error) {

            history = [];
        }
    }


    const analysis = {

        contract_name:
            data.contract_name || "Unknown Contract",

        contract_type:
            data.contract_type || "Contract",

        pass:
            Number(data.pass || 0),

        fail:
            Number(data.fail || 0),

        missing:
            Number(data.missing || 0),

        total:
            Number(data.total || 0),

        score:
            Number(data.score || 0),

        date:
            new Date().toISOString()

    };


    history.push(analysis);


    // Keep last 20 analyses

    if (history.length > 20) {

        history =
            history.slice(-20);

    }


    localStorage.setItem(
        historyKey,
        JSON.stringify(history)
    );

    localStorage.setItem(
        "contractGuardCurrentContract",
        analysis.contract_name
    );
}