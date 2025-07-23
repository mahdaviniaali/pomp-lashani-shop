// تابع انتخاب روش پرداخت
function selectPayment(method) {
    // حذف کلاس selected از همه روش‌ها
    document.querySelectorAll('.payment-method').forEach(item => {
        item.classList.remove('selected');
        item.querySelector('input[type="radio"]').checked = false;
    });
    
    // اضافه کردن کلاس selected به روش انتخاب شده
    event.currentTarget.classList.add('selected');
    
    // پیدا کردن input مربوطه در همان payment-method
    const input = event.currentTarget.querySelector('input[type="radio"]');
    if (input) {
        input.checked = true;
    }
}

// انتخاب اولین روش پرداخت به صورت پیش‌فرض هنگام لود صفحه
document.addEventListener('DOMContentLoaded', function() {
    const firstPaymentMethod = document.querySelector('.payment-method');
    if (firstPaymentMethod) {
        firstPaymentMethod.classList.add('selected');
        const input = firstPaymentMethod.querySelector('input[type="radio"]');
        if (input) {
            input.checked = true;
        }
    }
});