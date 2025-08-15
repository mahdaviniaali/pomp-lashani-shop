const payable_amount = document.getElementById('payable-amount');
const shippingDisplay = document.getElementById('shipping-cost-display');
const shippingDisplayValue = 0;
let productTotal;

document.body.addEventListener('htmx:afterSwap', (e) => {
  if (e.detail.target.id === 'product-total-hidden') {
    let productTotalValue = e.detail.target.textContent.trim();

    function parsePrice(text) {
        return Number(text.replace(/[^0-9]/g, '')) || 0;
    }

    
    productTotal = parsePrice(productTotalValue);
    $('#product-total-s').text(`${productTotal} تومان`);

    let payable = productTotal + shippingDisplayValue;
    payable_amount.textContent =  payable.toLocaleString('fa-IR') + " تومان"
  }
});


    
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

    if (isPostpaid) {
        shippingDisplay.textContent = 'پس‌کرایه';
        shippingDisplay.className = 'text-success';
        payable_amount.textContent = (productTotal).toLocaleString('fa-IR') + " تومان";
    } else if (cost === 0) {
        shippingDisplay.textContent = 'رایگان';
        shippingDisplay.className = 'text-success';
        payable_amount.textContent = (productTotal).toLocaleString('fa-IR') + " تومان";
    } else {
        shippingDisplay.textContent = cost.toLocaleString('fa-IR') + ' تومان';
        shippingDisplay.className = 'text-warning';

        let payable = productTotal + cost;
        payable_amount.textContent = payable.toLocaleString('fa-IR') + " تومان";
    }
}

