// محاسبات سمت کلاینت دیگر لازم نیست؛ مقادیر از سرور در قالب context تزریق می‌شوند
const payable_amount = document.getElementById('payable-amount');
const shippingDisplay = document.getElementById('shipping-cost-display');


    
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

    // پر کردن فیلدهای فرم برای ارسال سمت سرور
    let shipping_cost = document.getElementById('shipping-cost').value = isPostpaid ? 'پس کرایه' : cost;
    if(isPostpaid) {
        shipping_cost = 'پس کرایه';
    } else if (cost == 0 || !cost) {
        shipping_cost = 'رایگان';
    } else {
        shipping_cost = `${cost} تومان`;
    }

    shippingDisplay.textContent = shipping_cost;
    
    document.getElementById('shipping-name').value = name;
    document.getElementById('shipping-is-postpaid').value = isPostpaid;
    document.getElementById('shipping-method-id').value = id;

    // باقی محاسبات توسط سرور انجام می‌شود
}

