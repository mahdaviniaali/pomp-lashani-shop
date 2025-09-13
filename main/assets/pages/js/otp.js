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

    // تایمر OTP - محاسبه زمان باقیمانده از سرور
    let timeLeft = window.initialRemainingTime || 120; // زمان باقیمانده از سرور
    let resendTimeLeft = 60; // 1 دقیقه برای ارسال مجدد
    let countdownInterval;
    let resendInterval;

    const countdownElement = document.getElementById('countdown');
    const resendBtn = document.getElementById('resendBtn');
    const resendTimerElement = document.getElementById('resendTimer');

    function updateCountdown() {
        if (timeLeft <= 0) {
            clearInterval(countdownInterval);
            if (countdownElement) {
                countdownElement.textContent = "00:00";
                countdownElement.classList.add('expired');
            }
            return;
        }
        
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        if (countdownElement) {
            countdownElement.textContent = timeString;
        }
        
        timeLeft--;
    }

    function updateResendTimer() {
        if (resendTimerElement) {
            resendTimerElement.textContent = resendTimeLeft;
        }

        if (resendTimeLeft <= 0) {
            clearInterval(resendInterval);
            if (resendBtn) {
                resendBtn.disabled = false;
                resendBtn.innerHTML = 'ارسال مجدد کد';
                resendBtn.style.color = "#0d6efd";
            }
        }
        resendTimeLeft--;
    }

    // شروع تایمرها
    if (timeLeft > 0) {
        countdownInterval = setInterval(updateCountdown, 1000);
    } else {
        // اگر زمان تمام شده، نمایش 00:00
        if (countdownElement) {
            countdownElement.textContent = "00:00";
            countdownElement.classList.add('expired');
        }
    }
    
    // شروع تایمر ارسال مجدد
    if (resendTimeLeft > 0) {
        resendInterval = setInterval(updateResendTimer, 1000);
    } else {
        // اگر زمان ارسال مجدد تمام شده، فعال کردن دکمه
        if (resendBtn) {
            resendBtn.disabled = false;
            resendBtn.innerHTML = 'ارسال مجدد کد';
            resendBtn.style.color = "#0d6efd";
        }
    }
    
    // نمایش اولیه تایمر
    updateCountdown();
    updateResendTimer();
    
    // اضافه کردن console.log برای debug
    console.log('OTP Timer initialized:', {
        timeLeft: timeLeft,
        resendTimeLeft: resendTimeLeft,
        countdownElement: !!countdownElement,
        resendBtn: !!resendBtn,
        initialRemainingTime: window.initialRemainingTime
    });
    
    // اضافه کردن event listener برای debug
    if (countdownElement) {
        countdownElement.addEventListener('DOMSubtreeModified', function() {
            console.log('Countdown element changed:', this.textContent);
        });
    }
    
    // اضافه کردن MutationObserver برای debug
    if (countdownElement) {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' || mutation.type === 'characterData') {
                    console.log('Countdown element changed:', countdownElement.textContent);
                }
            });
        });
        observer.observe(countdownElement, {
            childList: true,
            characterData: true,
            subtree: true
        });
    }
    
    // اضافه کردن debug برای تایمر
    setInterval(function() {
        console.log('Timer status:', {
            timeLeft: timeLeft,
            resendTimeLeft: resendTimeLeft,
            countdownText: countdownElement ? countdownElement.textContent : 'N/A'
        });
    }, 5000);

    // مدیریت دکمه ارسال مجدد
    if (resendBtn) {
        resendBtn.addEventListener('click', function() {
            if (!this.disabled) {
                // ارسال درخواست برای ارسال مجدد کد
                fetch(window.location.href, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: 'resend=true'
                })
                .then(response => {
                    if (response.ok) {
                        // ریست کردن تایمرها
                        timeLeft = 120;
                        resendTimeLeft = 60;
                        
                        // ریست کردن CSS class
                        if (countdownElement) {
                            countdownElement.classList.remove('expired');
                        }
                        
                        // شروع مجدد تایمرها
                        clearInterval(countdownInterval);
                        clearInterval(resendInterval);
                        countdownInterval = setInterval(updateCountdown, 1000);
                        resendInterval = setInterval(updateResendTimer, 1000);
                        
                        // غیرفعال کردن دکمه
                        this.disabled = true;
                        this.style.color = "#6c757d";
                        
                        // نمایش پیام موفقیت
                        showMessage('کد جدید ارسال شد', 'success');
                    } else {
                        showMessage('خطا در ارسال مجدد کد', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showMessage('خطا در ارسال مجدد کد', 'error');
                });
            }
        });
    }

    // تابع نمایش پیام
    function showMessage(message, type) {
        // ایجاد عنصر پیام
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // اضافه کردن پیام به بالای فرم
        const form = document.getElementById('otpForm');
        if (form) {
            form.insertBefore(alertDiv, form.firstChild);
            
            // حذف خودکار پیام بعد از 5 ثانیه
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, 5000);
        }
    }
});