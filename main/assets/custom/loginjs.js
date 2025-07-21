
        document.addEventListener('DOMContentLoaded', function() {
            const otpInputs = document.querySelectorAll('.otp-input');
            const firstInput = document.getElementById('otp1');
            
            // راه‌حل قطعی برای قرار دادن مکان‌نما در سمت چپ
            function forceLTR(input) {
                input.style.textAlign = 'left';
                input.style.direction = 'ltr';
                input.style.unicodeBidi = 'isolate';
                input.setSelectionRange(0, 0);
            }
            
            // اعمال روی همه فیلدها
            otpInputs.forEach(input => {
                forceLTR(input);
                
                input.addEventListener('focus', function() {
                    forceLTR(this);
                    this.setSelectionRange(0, 0);
                });
            });
            
            // فوکوس اولیه
            setTimeout(() => {
                firstInput.focus();
                firstInput.setSelectionRange(0, 0);
            }, 100);
            
            // مدیریت حرکت بین فیلدها
            otpInputs.forEach((input, index) => {
                input.addEventListener('input', (e) => {
                    e.target.value = e.target.value.replace(/\D/g, '');
                    
                    if (e.target.value.length === 1) {
                        if (index < otpInputs.length - 1) {
                            otpInputs[index + 1].focus();
                            otpInputs[index + 1].setSelectionRange(0, 0);
                        }
                    }
                });
                
                input.addEventListener('keydown', (e) => {
                    if (e.key === 'Backspace' && e.target.value.length === 0) {
                        if (index > 0) {
                            otpInputs[index - 1].focus();
                            otpInputs[index - 1].setSelectionRange(1, 1);
                        }
                    }
                    
                    if (e.key === 'ArrowRight') {
                        e.preventDefault();
                        if (index < otpInputs.length - 1) {
                            otpInputs[index + 1].focus();
                            otpInputs[index + 1].setSelectionRange(0, 0);
                        }
                    }
                    
                    if (e.key === 'ArrowLeft') {
                        e.preventDefault();
                        if (index > 0) {
                            otpInputs[index - 1].focus();
                            otpInputs[index - 1].setSelectionRange(1, 1);
                        }
                    }
                });
                
                input.addEventListener('click', function() {
                    this.setSelectionRange(0, 0);
                });
            });
            
            // تایمرها
            let timeLeft = 120;
            const countdownElement = document.getElementById('countdown');
            const resendBtn = document.getElementById('resendBtn');
            const resendTimerElement = document.getElementById('resendTimer');
            let resendTimeLeft = 60;
            
            const countdownInterval = setInterval(() => {
                const minutes = Math.floor(timeLeft / 60);
                const seconds = timeLeft % 60;
                
                countdownElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                
                if (timeLeft <= 0) {
                    clearInterval(countdownInterval);
                    countdownElement.textContent = "کد منقضی شد";
                    countdownElement.style.color = "#e74a3b";
                } else {
                    timeLeft--;
                }
            }, 1000);
            
            const resendInterval = setInterval(() => {
                resendTimerElement.textContent = resendTimeLeft;
                
                if (resendTimeLeft <= 0) {
                    clearInterval(resendInterval);
                    resendBtn.textContent = "ارسال مجدد کد";
                    resendBtn.disabled = false;
                    resendBtn.classList.add("text-primary");
                } else {
                    resendTimeLeft--;
                }
            }, 1000);
            
            resendBtn.addEventListener('click', function() {
                alert('کد تأیید جدید برای شما ارسال شد.');
                resendBtn.disabled = true;
                resendBtn.classList.remove("text-primary");
                resendTimeLeft = 60;
                
                const newResendInterval = setInterval(() => {
                    resendTimerElement.textContent = resendTimeLeft;
                    
                    if (resendTimeLeft <= 0) {
                        clearInterval(newResendInterval);
                        resendBtn.textContent = "ارسال مجدد کد";
                        resendBtn.disabled = false;
                        resendBtn.classList.add("text-primary");
                    } else {
                        resendTimeLeft--;
                    }
                }, 1000);
                
                // ریست فیلدهای OTP
                otpInputs.forEach(input => {
                    input.value = '';
                    forceLTR(input);
                });
                firstInput.focus();
                firstInput.setSelectionRange(0, 0);
            });
            
            document.getElementById('otpForm').addEventListener('submit', function(e) {
                e.preventDefault();
                let otpCode = '';
                otpInputs.forEach(input => {
                    otpCode += input.value;
                });
                
                if (otpCode.length === 5) {
                    alert('کد با موفقیت تأیید شد: ' + otpCode);
                } else {
                    alert('لطفاً کد ۵ رقمی را کامل وارد کنید.');
                }
            });
        });
    