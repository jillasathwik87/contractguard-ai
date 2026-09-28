// =====================================================
// CONTRACTGUARD AI - ASK AI
// =====================================================

const API_BASE = typeof getApiBaseUrl === "function" ? getApiBaseUrl() : "http://127.0.0.1:8000";

const aiContractSelector =
    document.getElementById("aiContractSelector");

const aiContractStatus =
    document.getElementById("aiContractStatus");

const aiQuestion =
    document.getElementById("aiQuestion");

const askAIButton =
    document.getElementById("askAIButton");

const aiStatus =
    document.getElementById("aiStatus");

const aiAnswerSection =
    document.getElementById("aiAnswerSection");

const aiSourceSection =
    document.getElementById("aiSourceSection");

const aiAnswer =
    document.getElementById("aiAnswer");

const aiSource =
    document.getElementById("aiSource");

const exampleQuestionButtons =
    document.querySelectorAll(".question-card");


// =====================================================
// ASK AI
// =====================================================

if (askAIButton) {

    askAIButton.addEventListener(
        "click",
        askQuestion
    );

}


// =====================================================
// ASK QUESTION FUNCTION
// =====================================================

async function askQuestion() {

    const question =
        aiQuestion.value.trim();


    if (!question) {

        aiStatus.textContent =
            "Please enter a question.";

        aiStatus.style.color =
            "#dc2626";

        aiQuestion.focus();

        return;

    }


    // Disable button while processing

    askAIButton.disabled =
        true;

    askAIButton.textContent =
        "Thinking...";


    aiStatus.textContent =
        "Searching the analyzed contract...";

    aiStatus.style.color =
        "#6b7280";


    // Hide previous result

    aiAnswerSection.style.display =
        "none";

    aiSourceSection.style.display =
        "none";


    try {

        // =================================================
        // SEND QUESTION TO BACKEND
        // =================================================

        const response =
            await fetch(
                `${API_BASE}/api/ask`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        question: question
                    })
                }
            );


        const data =
            await response.json();
        if (data.success) {

            let questionCount =
                Number(
                    localStorage.getItem(
                        "contractGuardAIQuestions"
                    ) || 0
                );

            questionCount++;

            localStorage.setItem(
                "contractGuardAIQuestions",
                questionCount
            );
        }


        console.log(
            "Ask AI response:",
            data
        );


        // =================================================
        // CHECK HTTP RESPONSE
        // =================================================

        if (!response.ok) {

            throw new Error(
                data.error ||
                data.detail ||
                `Backend error: ${response.status}`
            );

        }


        // =================================================
        // CHECK APPLICATION RESPONSE
        // =================================================

        if (!data.success) {

            throw new Error(
                data.error ||
                data.answer ||
                "Unable to answer the question."
            );

        }


        // =================================================
        // DISPLAY ANSWER
        // =================================================

        aiAnswer.textContent =
            data.answer ||
            "No answer was returned.";


        aiAnswerSection.style.display =
            "block";


        // =================================================
        // DISPLAY SOURCE CLAUSE
        // =================================================

        if (data.source_clause) {

            aiSource.textContent =
                data.source_clause;

            aiSourceSection.style.display =
                "block";

        } else {

            aiSource.textContent =
                "No source clause was returned.";

            aiSourceSection.style.display =
                "block";

        }


        aiStatus.textContent =
            "Answer generated from the analyzed contract.";

        aiStatus.style.color =
            "#16a34a";


        // Scroll to answer

        aiAnswerSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });


    } catch (error) {

        console.error(
            "Ask AI error:",
            error
        );


        aiStatus.textContent =
            error.message;

        aiStatus.style.color =
            "#dc2626";


        aiAnswerSection.style.display =
            "none";

        aiSourceSection.style.display =
            "none";


    } finally {

        askAIButton.disabled =
            false;

        askAIButton.textContent =
            "Ask AI";

    }

}


// =====================================================
// EXAMPLE QUESTIONS
// =====================================================

exampleQuestionButtons.forEach(
    function (button) {

        button.addEventListener(
            "click",
            function () {

                const question =
                    button.dataset.question;


                if (question) {

                    aiQuestion.value =
                        question;

                    aiQuestion.focus();

                }

            }
        );

    }
);


// =====================================================
// ENTER KEY SUPPORT
// =====================================================

if (aiQuestion) {

    aiQuestion.addEventListener(
        "keydown",
        function (event) {

            // Ctrl + Enter sends the question

            if (
                event.key === "Enter" &&
                event.ctrlKey
            ) {

                event.preventDefault();

                askQuestion();

            }

        }
    );

}


// =====================================================
// CONTRACT SELECTION & STATUS
// =====================================================

function escapeHTML(value) {
    const div = document.createElement("div");
    div.textContent = String(value);
    return div.innerHTML;
}

function initContractSelection() {
    const currentContract = localStorage.getItem("contractGuardCurrentContract");
    let history = [];
    try {
        const saved = localStorage.getItem("contractGuardAnalysisHistory");
        if (saved) {
            history = JSON.parse(saved);
        }
    } catch (e) {
        history = [];
    }

    if (aiContractSelector) {
        aiContractSelector.innerHTML = '<option value="">Select an analyzed contract</option>';
        const seen = new Set();

        if (currentContract) {
            seen.add(currentContract);
            const opt = document.createElement("option");
            opt.value = currentContract;
            opt.textContent = `${currentContract} (Active)`;
            opt.selected = true;
            aiContractSelector.appendChild(opt);
        }

        history.forEach(function (item) {
            const name = item.contract_name;
            if (name && !seen.has(name)) {
                seen.add(name);
                const opt = document.createElement("option");
                opt.value = name;
                opt.textContent = name;
                aiContractSelector.appendChild(opt);
            }
        });

        aiContractSelector.addEventListener("change", function () {
            if (aiContractSelector.value) {
                localStorage.setItem("contractGuardCurrentContract", aiContractSelector.value);
                if (aiContractStatus) {
                    aiContractStatus.innerHTML = `Active contract: <strong>${escapeHTML(aiContractSelector.value)}</strong>.`;
                    aiContractStatus.style.color = "#16a34a";
                }
            }
        });
    }

    if (aiContractStatus) {
        if (currentContract) {
            aiContractStatus.innerHTML = `Active contract: <strong>${escapeHTML(currentContract)}</strong>. Ready for questions.`;
            aiContractStatus.style.color = "#16a34a";
        } else {
            aiContractStatus.innerHTML = `ℹ️ No active contract loaded yet. <a href="contracts.html" style="color:#4f46e5;font-weight:600;text-decoration:underline;">Upload & analyze a contract first</a>.`;
            aiContractStatus.style.color = "#d97706";
        }
    }
}

document.addEventListener("DOMContentLoaded", function () {
    initContractSelection();
});

// =====================================================
// PAGE LOADED
// =====================================================

console.log("Ask AI page loaded.");
console.log("Ask AI backend:", `${API_BASE}/api/ask`);