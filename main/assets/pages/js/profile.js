
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

    // Auto-dismiss success messages after 5 seconds
    const successAlert = document.querySelector('.alert-success');
    if (successAlert) {
        setTimeout(function() {
            successAlert.style.opacity = '0';
            successAlert.style.transform = 'translateY(-20px)';
            setTimeout(function() {
                successAlert.remove();
            }, 500);
        }, 5000);
    }
});
