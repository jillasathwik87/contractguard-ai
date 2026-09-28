// =====================================================
// CONTRACTGUARD AI - SETTINGS
// =====================================================

const SETTINGS_STORAGE_KEY = "contractGuardSettings";


// =====================================================
// DEFAULT SETTINGS
// =====================================================

const defaultSettings = {
    darkMode: false,
    compactMode: false,
    aiResponseStyle: "concise",
    showSourceClause: true,
    generateSummary: true,
    automaticAnalysis: false,
    complianceChecks: true,
    sourceRetrieval: true,
    analysisNotifications: true,
    complianceNotifications: true,
    savePreferences: true
};


// =====================================================
// GET ELEMENTS
// =====================================================

const darkModeToggle =
    document.getElementById("darkModeToggle");

const compactModeToggle =
    document.getElementById("compactModeToggle");

const aiResponseStyle =
    document.getElementById("aiResponseStyle");

const sourceClauseToggle =
    document.getElementById("sourceClauseToggle");

const summaryToggle =
    document.getElementById("summaryToggle");

const automaticAnalysisToggle =
    document.getElementById("automaticAnalysisToggle");

const complianceChecksToggle =
    document.getElementById("complianceChecksToggle");

const sourceRetrievalToggle =
    document.getElementById("sourceRetrievalToggle");

const analysisNotificationToggle =
    document.getElementById("analysisNotificationToggle");

const complianceNotificationToggle =
    document.getElementById("complianceNotificationToggle");

const savePreferencesToggle =
    document.getElementById("savePreferencesToggle");

const apiUrlInput =
    document.getElementById("apiUrlInput");

const testApiButton =
    document.getElementById("testApiButton");

const apiConnectionStatus =
    document.getElementById("apiConnectionStatus");

const saveButton =
    document.getElementById("saveSettingsButton");

const resetButton =
    document.getElementById("resetSettingsButton");

const clearButton =
    document.getElementById("clearSettingsButton");

const statusMessage =
    document.getElementById("settingsStatus");


// =====================================================
// GET SAVED SETTINGS
// =====================================================

function getSavedSettings() {

    const saved =
        localStorage.getItem(
            SETTINGS_STORAGE_KEY
        );

    if (!saved) {
        return { ...defaultSettings };
    }

    try {

        return {
            ...defaultSettings,
            ...JSON.parse(saved)
        };

    } catch (error) {

        console.error(
            "Could not read settings:",
            error
        );

        return { ...defaultSettings };
    }
}


// =====================================================
// APPLY THEME
// =====================================================

function applyTheme(settings) {

    document.body.classList.toggle(
        "dark-mode",
        settings.darkMode === true
    );

    document.body.classList.toggle(
        "compact-mode",
        settings.compactMode === true
    );
}


// =====================================================
// LOAD CONTROLS
// =====================================================

function loadControls(settings) {

    darkModeToggle.checked =
        settings.darkMode;

    compactModeToggle.checked =
        settings.compactMode;

    aiResponseStyle.value =
        settings.aiResponseStyle;

    sourceClauseToggle.checked =
        settings.showSourceClause;

    summaryToggle.checked =
        settings.generateSummary;

    automaticAnalysisToggle.checked =
        settings.automaticAnalysis;

    complianceChecksToggle.checked =
        settings.complianceChecks;

    sourceRetrievalToggle.checked =
        settings.sourceRetrieval;

    analysisNotificationToggle.checked =
        settings.analysisNotifications;

    complianceNotificationToggle.checked =
        settings.complianceNotifications;

    savePreferencesToggle.checked =
        settings.savePreferences;

    if (apiUrlInput) {
        apiUrlInput.value = localStorage.getItem("contractGuardApiUrl") || "";
    }
}


// =====================================================
// GET CURRENT SETTINGS
// =====================================================

function getCurrentSettings() {

    return {

        darkMode:
            darkModeToggle.checked,

        compactMode:
            compactModeToggle.checked,

        aiResponseStyle:
            aiResponseStyle.value,

        showSourceClause:
            sourceClauseToggle.checked,

        generateSummary:
            summaryToggle.checked,

        automaticAnalysis:
            automaticAnalysisToggle.checked,

        complianceChecks:
            complianceChecksToggle.checked,

        sourceRetrieval:
            sourceRetrievalToggle.checked,

        analysisNotifications:
            analysisNotificationToggle.checked,

        complianceNotifications:
            complianceNotificationToggle.checked,

        savePreferences:
            savePreferencesToggle.checked

    };
}


// =====================================================
// STATUS
// =====================================================

function showStatus(message) {

    statusMessage.textContent =
        message;

    statusMessage.style.color =
        "#16a34a";

    setTimeout(function () {

        statusMessage.textContent = "";

    }, 3000);
}


// =====================================================
// SAVE
// =====================================================

function saveSettings() {

    const settings =
        getCurrentSettings();

    localStorage.setItem(
        SETTINGS_STORAGE_KEY,
        JSON.stringify(settings)
    );

    if (apiUrlInput) {
        const customUrl = apiUrlInput.value.trim();
        if (customUrl) {
            localStorage.setItem("contractGuardApiUrl", customUrl);
            window.CONTRACTGUARD_API_BASE = customUrl.replace(/\/+$/, "");
        } else {
            localStorage.removeItem("contractGuardApiUrl");
            if (typeof getApiBaseUrl === "function") {
                window.CONTRACTGUARD_API_BASE = getApiBaseUrl();
            }
        }
    }

    applyTheme(settings);

    showStatus(
        "Settings saved successfully."
    );

    console.log(
        "Settings saved:",
        settings
    );
}


// =====================================================
// RESET
// =====================================================

function resetSettings() {

    if (
        !window.confirm(
            "Reset all settings to default?"
        )
    ) {
        return;
    }

    const settings =
        { ...defaultSettings };

    localStorage.setItem(
        SETTINGS_STORAGE_KEY,
        JSON.stringify(settings)
    );

    loadControls(settings);

    applyTheme(settings);

    showStatus(
        "Settings reset successfully."
    );
}


// =====================================================
// CLEAR
// =====================================================

function clearSettings() {

    if (
        !window.confirm(
            "Clear all saved settings?"
        )
    ) {
        return;
    }

    localStorage.removeItem(
        SETTINGS_STORAGE_KEY
    );

    const settings =
        { ...defaultSettings };

    loadControls(settings);

    applyTheme(settings);

    showStatus(
        "Saved settings cleared."
    );
}


// =====================================================
// DARK MODE
// =====================================================

darkModeToggle.addEventListener(
    "change",
    function () {

        document.body.classList.toggle(
            "dark-mode",
            this.checked
        );

    }
);


// =====================================================
// COMPACT MODE
// =====================================================

compactModeToggle.addEventListener(
    "change",
    function () {

        document.body.classList.toggle(
            "compact-mode",
            this.checked
        );

    }
);


// =====================================================
// BUTTONS
// =====================================================

saveButton.addEventListener(
    "click",
    saveSettings
);

resetButton.addEventListener(
    "click",
    resetSettings
);

clearButton.addEventListener(
    "click",
    clearSettings
);

if (testApiButton) {
    testApiButton.addEventListener("click", async function () {
        const urlToTest = (apiUrlInput && apiUrlInput.value.trim())
            ? apiUrlInput.value.trim().replace(/\/+$/, "")
            : (typeof getApiBaseUrl === "function" ? getApiBaseUrl() : window.location.origin);

        apiConnectionStatus.textContent = "Testing connection to " + urlToTest + "...";
        apiConnectionStatus.style.color = "#4f46e5";

        try {
            const resp = await fetch(`${urlToTest}/api/health`, { method: "GET" });
            if (resp.ok) {
                const data = await resp.json();
                apiConnectionStatus.textContent = `✓ Connected successfully (${data.message || 'Running'}). Ollama model: ${data.models?.llm || 'llama3.2'}`;
                apiConnectionStatus.style.color = "#16a34a";
            } else {
                apiConnectionStatus.textContent = `⚠️ Connected, but server returned HTTP status: ${resp.status}`;
                apiConnectionStatus.style.color = "#d97706";
            }
        } catch (err) {
            apiConnectionStatus.textContent = `✕ Connection failed: ${err.message}. Please verify the URL and backend status.`;
            apiConnectionStatus.style.color = "#dc2626";
        }
    });
}


// =====================================================
// INITIALIZE
// =====================================================

const initialSettings =
    getSavedSettings();

loadControls(
    initialSettings
);

applyTheme(
    initialSettings
);

console.log(
    "SETTINGS.JS IS RUNNING"
);