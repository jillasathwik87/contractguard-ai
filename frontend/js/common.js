// =====================================================
// CONTRACTGUARD AI - GLOBAL THEME
// =====================================================

const SETTINGS_KEY = "contractGuardSettings";


// =====================================================
// APPLY THEME
// =====================================================

function applyGlobalSettings() {

    const savedSettings =
        localStorage.getItem(SETTINGS_KEY);

    let settings = {
        darkMode: false,
        compactMode: false
    };


    if (savedSettings) {

        try {

            settings = {
                ...settings,
                ...JSON.parse(savedSettings)
            };

        } catch (error) {

            console.error(
                "Could not read saved settings:",
                error
            );

        }

    }


    // IMPORTANT:
    // Always explicitly add OR remove the class.

    if (settings.darkMode === true) {

        document.body.classList.add(
            "dark-mode"
        );

    } else {

        document.body.classList.remove(
            "dark-mode"
        );

    }


    // Compact mode

    if (settings.compactMode === true) {

        document.body.classList.add(
            "compact-mode"
        );

    } else {

        document.body.classList.remove(
            "compact-mode"
        );

    }

}


// =====================================================
// RUN ON PAGE LOAD
// =====================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        applyGlobalSettings();

    }
);