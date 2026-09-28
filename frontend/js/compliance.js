// =====================================================
// CONTRACTGUARD AI - COMPLIANCE RULES
// =====================================================

document.addEventListener("DOMContentLoaded", function () {

    const ruleSearch =
        document.getElementById("ruleSearch");

    const categoryFilter =
        document.getElementById("categoryFilter");

    const resetRulesButton =
        document.getElementById("resetRulesButton");

    const noRulesMessage =
        document.getElementById("noRulesMessage");

    const ruleCards =
        Array.from(
            document.querySelectorAll(
                "#rulesContainer .rule-card"
            )
        );


    // =====================================================
    // FILTER RULES
    // =====================================================

    function filterRules() {

        const searchText =
            ruleSearch
                ? ruleSearch.value.trim().toLowerCase()
                : "";

        const selectedCategory =
            categoryFilter
                ? categoryFilter.value.trim().toLowerCase()
                : "all";

        let visibleCount = 0;


        ruleCards.forEach(function (row) {

            const rowText =
                row.textContent.toLowerCase();

            const rowCategory =
                (
                    row.dataset.category || ""
                ).toLowerCase();


            const matchesSearch =
                searchText === "" ||
                rowText.includes(searchText);


            const matchesCategory =
                selectedCategory === "all" ||
                rowCategory === selectedCategory;


            const shouldShow =
                matchesSearch &&
                matchesCategory;


            // Use hidden instead of display.
            // This works correctly with table rows.

            row.hidden = !shouldShow;


            if (shouldShow) {
                visibleCount++;
            }

        });


        // =================================================
        // NO RESULTS MESSAGE
        // =================================================

        if (noRulesMessage) {

            noRulesMessage.style.display =
                visibleCount === 0
                    ? "block"
                    : "none";

        }

    }


    // =====================================================
    // SEARCH
    // =====================================================

    if (ruleSearch) {

        ruleSearch.addEventListener(
            "input",
            filterRules
        );

    }


    // =====================================================
    // CATEGORY FILTER
    // =====================================================

    if (categoryFilter) {

        categoryFilter.addEventListener(
            "change",
            filterRules
        );

    }


    // =====================================================
    // RESET
    // =====================================================

    if (resetRulesButton) {

        resetRulesButton.addEventListener(
            "click",
            function () {

                if (ruleSearch) {
                    ruleSearch.value = "";
                }

                if (categoryFilter) {
                    categoryFilter.value = "all";
                }


                ruleCards.forEach(function (row) {

                    row.hidden = false;

                });


                if (noRulesMessage) {

                    noRulesMessage.style.display =
                        "none";

                }

            }
        );

    }


    // =====================================================
    // INITIAL STATE
    // =====================================================

    filterRules();


    console.log(
        "Compliance Rules page loaded successfully."
    );

});