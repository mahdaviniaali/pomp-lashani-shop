
document.addEventListener('DOMContentLoaded', function() {
    // فعال کردن دکمه هنگام تغییر اطلاعات
    document.querySelectorAll('#user-info-form input').forEach(input => {
        input.addEventListener('input', function() {
            const saveBtn = document.getElementById('save-btn');
            saveBtn.disabled = false;
            saveBtn.classList.remove('bg-gray');
            saveBtn.classList.add('bg-green2');
        });
    });
});

// تابع مدیریت پاسخ ذخیره
function handleSaveResponse(event) {
    const button = document.getElementById('save-btn');
    const btnText = button.querySelector('.btn-text');
    
    if (event.detail.xhr.status === 200) {
        // نمایش پیام موفقیت
        btnText.textContent = 'تغییرات ثبت شد';
        button.classList.remove('bg-green2');
        button.classList.add('bg-gray');
        button.disabled = true;
        
        // بعد از 2 ثانیه دکمه را به حالت اولیه برگردان
        setTimeout(function() {
            btnText.textContent = 'ذخیره کردن';
        }, 2000);
    }
}