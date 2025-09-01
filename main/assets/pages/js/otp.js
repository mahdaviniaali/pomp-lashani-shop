document.addEventListener("DOMContentLoaded", function () {
    const inputs = document.querySelectorAll(".otp-input");

    // فوکوس و ورود از چپ به راست (اولین خانه سمت چپ)
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
                inputs[data.length - 1].focus();
            }
        });
    });
    // فوکوس اولیه روی اولین input سمت چپ
    if (inputs.length > 0) {
        inputs[0].focus();
    }

    // اضافه کردن مقدار otp_code به صورت داینامیک قبل از ارسال فرم
    var otpForm = document.getElementById('otpForm');
    if (otpForm) {
        otpForm.addEventListener('submit', function(e) {
            // ترتیب ورود از چپ به راست (otp1 تا otp5)
            var code = '';
            for (let i = 1; i <= 5; i++) {
                let inp = document.getElementsByName('otp' + i)[0];
                if (inp) code += inp.value;
            }
            var otpCodeInput = document.getElementById('otp_code');
            if (otpCodeInput) {
                otpCodeInput.value = code;
            }
        });
    }
});