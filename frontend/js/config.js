// =====================================================
// CONTRACTGUARD AI - CONFIGURATION & DYNAMIC API BASE
// =====================================================

(function () {
    function resolveApiBase() {
        // 1. Explicit window override
        if (window.CONTRACTGUARD_API_URL && typeof window.CONTRACTGUARD_API_URL === "string") {
            return window.CONTRACTGUARD_API_URL.replace(/\/+$/, "");
        }

        // 2. Saved preference in localStorage (allows configuration via Settings UI)
        try {
            const saved = localStorage.getItem("contractGuardApiUrl");
            if (saved && saved.trim() !== "") {
                return saved.trim().replace(/\/+$/, "");
            }
        } catch (e) {
            console.warn("Could not read localStorage for API URL:", e);
        }

        // 3. Meta tag in HTML head: <meta name="api-base" content="...">
        const metaTag = document.querySelector('meta[name="api-base"]');
        if (metaTag && metaTag.content && metaTag.content.trim() !== "") {
            return metaTag.content.trim().replace(/\/+$/, "");
        }

        // 4. Same-origin deployment: when frontend and FastAPI backend are served together
        if (window.location && window.location.protocol && (window.location.protocol === "http:" || window.location.protocol === "https:")) {
            return window.location.origin;
        }

        // 5. Localhost fallback for local file:// previews
        return "http://127.0.0.1:8000";
    }

    const apiBase = resolveApiBase();
    window.CONTRACTGUARD_API_BASE = apiBase;
    console.log("ContractGuard AI API Base configured as:", apiBase);
})();

function getApiBaseUrl() {
    if (window.CONTRACTGUARD_API_BASE) {
        return window.CONTRACTGUARD_API_BASE;
    }
    return (window.location && window.location.origin && window.location.protocol.startsWith("http"))
        ? window.location.origin
        : "http://127.0.0.1:8000";
}
