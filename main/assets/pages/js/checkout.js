document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.shipping-method-card');
    const costInput = document.getElementById('shipping-cost');
    const nameInput = document.getElementById('shipping-name');
    const productTotalElement = document.getElementById('product-total');
    const shippingFeeElement = document.getElementById('shipping-fee');
    const payableAmountElement = document.getElementById('payable-amount');
    
    // تابع محاسبه و نمایش مبلغ نهایی
    function updateTotalPrice() {
        const productTotal = parseInt(productTotalElement.getAttribute('data-price')) || 0;
        const shippingFee = parseInt(costInput.value) || 0;
        
        // بروزرسانی نمایش هزینه ارسال
        if (shippingFee === 0) {
            shippingFeeElement.textContent = 'رایگان';
        } else {
            shippingFeeElement.textContent = shippingFee.toLocaleString() + ' تومان';
        }
        
        // محاسبه و نمایش مبلغ نهایی
        const finalPrice = productTotal + shippingFee;
        payableAmountElement.textContent = finalPrice.toLocaleString() + ' تومان';
        
        // ذخیره مقدار نهایی برای استفاده در فرم پرداخت
        if (document.getElementById('final-price-input')) {
            document.getElementById('final-price-input').value = finalPrice;
        }
    }
    
    // اجرای اولیه برای نمایش مقادیر پیش‌فرض
    updateTotalPrice();
    
    cards.forEach(card => {
        card.addEventListener('click', function() {
            // حذف حالت انتخاب از همه کارت‌ها
            cards.forEach(c => c.classList.remove('border-primary'));
            
            // اضافه کردن حالت انتخاب به کارت کلیک شده
            this.classList.add('border-primary');
            
            // آپدیت فیلدهای مخفی
            const radio = this.querySelector('input[type="radio"]');
            radio.checked = true;
            
            // آپدیت هزینه و نام روش ارسال
            if(radio.value === '1') {
                costInput.value = '0';
                nameInput.value = 'پست پیشتاز';
            } else if(radio.value === '2') {
                costInput.value = '15000';
                nameInput.value = 'تیپاکس';
            } else {
                costInput.value = '30000';
                nameInput.value = 'ارسال اکسپرس';
            }
            
            // بروزرسانی قیمت نهایی پس از تغییر روش ارسال
            updateTotalPrice();
        });
    });
});