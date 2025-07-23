
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
