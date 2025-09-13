// اضافه کردن CSS برای انیمیشن
const style = document.createElement('style');
style.textContent = `
    .num {
        transition: transform 0.2s ease-in-out;
    }
`;
document.head.appendChild(style);

// تابع برای به‌روزرسانی تعداد کل آیتم‌های سبد خرید در navbar
function updateCartCount() {
    // دریافت تعداد کل از سرور
    fetch('/carts/cart/count-update/')
        .then(response => response.text())
        .then(count => {
            // به‌روزرسانی تمام عناصر navbar
            const navbarCount = document.getElementById('cart-count-navbar');
            const mobileNavbarCount = document.getElementById('cart-count-mobile-navbar');
            const offcanvasCount = document.getElementById('cart-count-offcanvas');
            
            if (navbarCount) navbarCount.textContent = count;
            if (mobileNavbarCount) mobileNavbarCount.textContent = count;
            if (offcanvasCount) offcanvasCount.textContent = count;
            
            // اضافه کردن انیمیشن برای تغییر
            [navbarCount, mobileNavbarCount, offcanvasCount].forEach(element => {
                if (element) {
                    element.style.transform = 'scale(1.2)';
                    setTimeout(() => {
                        element.style.transform = 'scale(1)';
                    }, 200);
                }
            });
        })
        .catch(error => {
            console.error('خطا در به‌روزرسانی تعداد سبد خرید:', error);
        });
}

// اضافه کردن event listener برای HTMX events
document.addEventListener('DOMContentLoaded', function() {
    // به‌روزرسانی اولیه
    updateCartCount();
});

// تابع عمومی برای استفاده در جاهای دیگر
window.updateCartCount = updateCartCount;
