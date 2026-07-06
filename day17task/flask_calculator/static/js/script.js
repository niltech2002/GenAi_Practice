// Wrapped in IIFE to avoid polluting global scope
(function () {
    const OP_SYMBOLS = { "+": "+", "-": "−", "*": "×", "/": "÷" };

    // --- State ---
    let currentInput = "0";
    let firstOperand = null;
    let operator = null;
    let awaitingSecond = false;

    // --- DOM refs ---
    const currentEl = document.getElementById("current");
    const expressionEl = document.getElementById("expression");
    const errorEl = document.getElementById("error");
    const equalsBtn = document.getElementById("equalsBtn");

    // --- Digit & decimal buttons ---
    document.querySelectorAll(".btn-digit").forEach((btn) => {
        btn.addEventListener("click", () => handleDigit(btn.dataset.val));
    });

    function handleDigit(val) {
        clearError();
        if (val === ".") {
            if (awaitingSecond) { currentInput = "0."; awaitingSecond = false; }
            else if (!currentInput.includes(".")) { currentInput += "."; }
        } else {
            if (awaitingSecond || currentInput === "0") {
                currentInput = val;
                awaitingSecond = false;
            } else {
                currentInput += val;
            }
        }
        updateDisplay();
    }

    // --- Operator buttons ---
    document.querySelectorAll(".btn-operator").forEach((btn) => {
        btn.addEventListener("click", () => {
            clearError();
            document.querySelectorAll(".btn-operator").forEach((b) => b.classList.remove("active"));
            btn.classList.add("active");
            firstOperand = currentInput;
            operator = btn.dataset.op;
            awaitingSecond = true;
            expressionEl.textContent = `${firstOperand} ${OP_SYMBOLS[operator]}`;
        });
    });

    // --- Equals button ---
    equalsBtn.addEventListener("click", calculate);

    // --- Clear button ---
    document.getElementById("clearBtn").addEventListener("click", () => {
        currentInput = "0";
        firstOperand = null;
        operator = null;
        awaitingSecond = false;
        expressionEl.innerHTML = "&nbsp;";
        document.querySelectorAll(".btn-operator").forEach((b) => b.classList.remove("active"));
        clearError();
        updateDisplay();
    });

    // --- Keyboard support ---
    document.addEventListener("keydown", (e) => {
        if (e.key >= "0" && e.key <= "9") { handleDigit(e.key); }
        else if (e.key === ".") { handleDigit("."); }
        else if (Object.keys(OP_SYMBOLS).includes(e.key)) {
            document.querySelector(`.btn-operator[data-op="${e.key}"]`)?.click();
        } else if (e.key === "Enter" || e.key === "=") { calculate(); }
        else if (e.key === "Escape") { document.getElementById("clearBtn").click(); }
    });

    // --- Calculate: sends to Flask backend ---
    async function calculate() {
        if (!firstOperand || !operator || awaitingSecond) {
            showError("Enter a number, choose an operator, then enter another number.");
            return;
        }

        equalsBtn.disabled = true;

        try {
            const response = await fetch("/calculate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ num1: firstOperand, num2: currentInput, operator }),
            });

            const data = await response.json();

            if (!response.ok) {
                showError(data.error || "An error occurred.");
                currentInput = "Error";
            } else {
                expressionEl.textContent =
                    `${firstOperand} ${OP_SYMBOLS[operator]} ${currentInput} =`;
                currentInput = String(data.result);
                firstOperand = null;
                operator = null;
                awaitingSecond = false;
                document.querySelectorAll(".btn-operator").forEach((b) => b.classList.remove("active"));
            }
        } catch (err) {
            console.error("Calculation request failed:", err);
            showError("Failed to connect to server.");
        } finally {
            equalsBtn.disabled = false;
        }

        updateDisplay();
    }

    function updateDisplay() { currentEl.textContent = currentInput; }
    function showError(msg) { errorEl.textContent = msg; }
    function clearError() { errorEl.textContent = ""; }
})();
