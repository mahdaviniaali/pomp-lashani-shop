document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.shipping-method-card');
    const costInput = document.getElementById('shipping-cost');
    const nameInput = document.getElementById('shipping-name');
    
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
        });
    });
});