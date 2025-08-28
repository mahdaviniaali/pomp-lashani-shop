document.addEventListener("DOMContentLoaded", function () {
    const inputs = document.querySelectorAll(".otp-input");

    inputs.forEach((input, index) => {
        input.addEventListener("input", () => {
            if (input.value && index < inputs.length - 1) {
                inputs[index + 1].focus();
            }
        });

        input.addEventListener("keydown", (e) => {
            if (e.key === "Backspace" && !input.value && index > 0) {
                inputs[index - 1].focus();
            }
        });

        input.addEventListener("paste", (e) => {
            e.preventDefault();
            const data = e.clipboardData.getData("text").trim();
            if (data.length === inputs.length && /^\d+$/.test(data)) {
                inputs.forEach((inp, i) => inp.value = data[i]);
                inputs[inputs.length - 1].focus();
            }
        });
    });
});