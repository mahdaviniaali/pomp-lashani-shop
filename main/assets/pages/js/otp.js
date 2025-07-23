// اسکریپت برای مدیریت فیلدهای OTP
document.addEventListener('DOMContentLoaded', function() {
    const otpInputs = document.querySelectorAll('.otp-input');
    
    // تغییر ترتیب فیلدها برای نمایش از راست به چپ
    const orderedInputs = Array.from(otpInputs).reverse();
    
    // حرکت خودکار بین فیلدها
    orderedInputs.forEach((input, index) => {
        input.addEventListener('input', (e) => {
            if (e.target.value.length === 1) {
                if (index < orderedInputs.length - 1) {
                    orderedInputs[index + 1].focus();
                }
            }
        });
        
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && e.target.value.length === 0) {
                if (index > 0) {
                    orderedInputs[index - 1].focus();
                }
            }
        });
    });
    
    // شمارش معکوس
    function startCountdown() {
        let timeLeft = 120;
        const countdownElement = document.getElementById('countdown');
        const resendBtn = document.getElementById('resendBtn');
        const resendTimer = document.getElementById('resendTimer');
        
        const timer = setInterval(() => {
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            
            countdownElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            resendTimer.textContent = timeLeft > 60 ? Math.floor(timeLeft - 60) : timeLeft;
            
            if (timeLeft <= 0) {
                clearInterval(timer);
                resendBtn.disabled = false;
                resendBtn.innerHTML = 'ارسال مجدد کد';
            }
            
            timeLeft--;
        }, 1000);
    }
    
    startCountdown();
    
    // ارسال مجدد کد
    document.getElementById('resendBtn').addEventListener('click', function() {
        // اینجا می‌توانید درخواست AJAX برای ارسال مجدد کد اضافه کنید
        alert('کد جدید ارسال شد!');
        this.disabled = true;
        startCountdown();
    });
    
    // ترکیب فیلدهای OTP هنگام ارسال فرم
    document.getElementById('otpForm').addEventListener('submit', function(e) {
        const otpCode = Array.from(otpInputs).reverse().map(input => input.value).join('');
        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = 'otp_code';
        hiddenInput.value = otpCode;
        this.appendChild(hiddenInput);
    });
});