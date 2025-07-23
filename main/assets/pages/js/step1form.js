 // تابع انتخاب روش ارسال با پشتیبانی از پس‌کرایه
    function selectShipping(id, cost, name, isPostpaid = false) {
        // حذف کلاس selected از همه کارت‌ها
        document.querySelectorAll('.shipping-method-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // اضافه کردن کلاس selected به کارت انتخاب شده
        event.currentTarget.classList.add('selected');
        
        // آپدیت رادیو باتن انتخاب شده
        document.querySelector(`input[value="${id}"]`).checked = true;
        
        // آپدیت فیلدهای مخفی
        document.getElementById('shipping-cost').value = isPostpaid ? 0 : cost;
        document.getElementById('shipping-name').value = name;
        document.getElementById('shipping-is-postpaid').value = isPostpaid;
        
        // آپدیت نمایش هزینه ارسال
        const shippingDisplay = document.getElementById('shipping-cost-display');
        if(isPostpaid) {
            shippingDisplay.textContent = 'پس‌کرایه';
            shippingDisplay.className = 'text-info';
        } else if(cost === 0) {
            shippingDisplay.textContent = 'رایگان';
            shippingDisplay.className = 'text-success';
        } else {
            shippingDisplay.textContent = cost.toLocaleString() + ' تومان';
            shippingDisplay.className = 'text-warning';
        }
    }