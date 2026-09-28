// =====================================================
// CONTRACTGUARD AI - DASHBOARD
// =====================================================

const ANALYSIS_HISTORY_KEY = "contractGuardAnalysisHistory";


// =====================================================
// GET SAVED ANALYSES
// =====================================================

function getAnalysisHistory() {

    const saved =
        localStorage.getItem(
            ANALYSIS_HISTORY_KEY
        );

    if (!saved) {
        return [];
    }

    try {

        return JSON.parse(saved);

    } catch (error) {

        console.error(
            "Could not read analysis history:",
            error
        );

        return [];
    }
}


// =====================================================
// UPDATE DASHBOARD
// =====================================================

function updateDashboard() {

    const history =
        getAnalysisHistory();


    // -----------------------------------------------
    // TOTAL CONTRACTS
    // -----------------------------------------------

    const contractsAnalyzed =
        document.getElementById(
            "contractsAnalyzed"
        );

    if (contractsAnalyzed) {

        contractsAnalyzed.textContent =
            history.length;
    }


    // -----------------------------------------------
    // COMPLIANCE PASSED
    // -----------------------------------------------

    let passed = 0;

    history.forEach(function (contract) {

        passed += Number(
            contract.pass || 0
        );

    });

    const compliancePassed =
        document.getElementById(
            "compliancePassed"
        );

    if (compliancePassed) {

        compliancePassed.textContent =
            passed;
    }


    // -----------------------------------------------
    // COMPLIANCE ISSUES
    // FAIL + MISSING
    // -----------------------------------------------

    let issues = 0;

    history.forEach(function (contract) {

        issues +=
            Number(contract.fail || 0) +
            Number(contract.missing || 0);

    });

    const complianceIssues =
        document.getElementById(
            "complianceIssues"
        );

    if (complianceIssues) {

        complianceIssues.textContent =
            issues;
    }


    // -----------------------------------------------
    // AI QUESTIONS
    // -----------------------------------------------

    const aiQuestions =
        document.getElementById(
            "aiQuestions"
        );

    const questionCount =
        Number(
            localStorage.getItem(
                "contractGuardAIQuestions"
            ) || 0
        );

    if (aiQuestions) {

        aiQuestions.textContent =
            questionCount;
    }


    // -----------------------------------------------
    // RECENT CONTRACTS
    // -----------------------------------------------

    updateRecentContracts(history);
}


// =====================================================
// RECENT CONTRACTS
// =====================================================

function updateRecentContracts(history) {

    const container =
        document.getElementById(
            "recentContracts"
        );

    if (!container) {
        return;
    }


    if (history.length === 0) {

        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">
                    📄
                </div>

                <h3>
                    No contracts analyzed yet
                </h3>

                <p>
                    Upload a contract to start your
                    compliance analysis.
                </p>

                <button
                    class="primary-button"
                    onclick="window.location.href='contracts.html'"
                >
                    Upload Contract
                </button>
            </div>
        `;

        return;
    }


    // Show newest first

    const recent =
        [...history]
            .reverse()
            .slice(0, 5);


    container.innerHTML =
        recent.map(function (contract) {

            const score =
                contract.score ?? 0;

            let scoreClass =
                "score-neutral";

            if (score >= 80) {

                scoreClass =
                    "score-good";

            } else if (score >= 60) {

                scoreClass =
                    "score-warning";

            } else {

                scoreClass =
                    "score-danger";
            }


            return `
                <div class="recent-contract-item">

                    <div class="recent-contract-icon">
                        📄
                    </div>

                    <div class="recent-contract-info">

                        <strong>
                            ${escapeHTML(
                contract.contract_name ||
                "Unnamed Contract"
            )}
                        </strong>

                        <span>
                            ${contract.contract_type ||
                "Contract"
                }
                        </span>

                    </div>

                    <div class="
                        recent-contract-score
                        ${scoreClass}
                    ">
                        ${score}%
                    </div>

                </div>
            `;

        }).join("");
}


// =====================================================
// SAFE HTML
// =====================================================

function escapeHTML(value) {

    const div =
        document.createElement("div");

    div.textContent =
        String(value);

    return div.innerHTML;
}


// =====================================================
// INITIALIZE
// =====================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        updateDashboard();

    }
);