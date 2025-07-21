document.addEventListener('DOMContentLoaded', function() {
    // مدیریت رویدادهای HTMX
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) loadingOverlay.style.display = 'none';
        
        if (evt.detail.successful) {
            // به‌روزرسانی شماره سبد خرید
            updateCartBadge();
            
            // به‌روزرسانی خلاصه سبد خرید
            updateCartSummary();
        }
    });
    
    // تابع به‌روزرسانی نشانگر سبد خرید
    function updateCartBadge() {
        fetch('{% url "carts:cart_count" %}', {
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.count !== undefined) {
                const cartBadge = document.getElementById('cart-count-badge');
                if (cartBadge) {
                    cartBadge.textContent = data.count;
                    animateElement(cartBadge);
                }
            }
        });
    }
    
    // تابع به‌روزرسانی خلاصه سبد خرید
    function updateCartSummary() {
        fetch('{% url "carts:cart_summary" %}', {
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.total_items !== undefined) {
                const totalItemsElement = document.getElementById('total-items');
                if (totalItemsElement) totalItemsElement.textContent = data.total_items;
            }
            
            if (data.total_price !== undefined) {
                const totalPriceElement = document.getElementById('total-price');
                if (totalPriceElement) {
                    totalPriceElement.textContent = new Intl.NumberFormat('fa-IR').format(data.total_price);
                }
                
                const totalPayable = document.querySelector('.summary-total .text-primary');
                if (totalPayable) {
                    totalPayable.textContent = new Intl.NumberFormat('fa-IR').format(data.total_price) + ' تومان';
                }
            }
        });
    }
    
    // تابع انیمیشن برای المان‌ها
    function animateElement(element) {
        element.classList.add('animate');
        setTimeout(() => {
            element.classList.remove('animate');
        }, 300);
    }
    
    // نمایش لودینگ هنگام درخواست
    document.body.addEventListener('htmx:beforeRequest', function(evt) {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) loadingOverlay.style.display = 'flex';
    });
    
    // مدیریت حذف آیتم
    document.addEventListener('htmx:beforeSwap', function(evt) {
        if (evt.detail.requestConfig.path.includes('/cart_remove')) {
            setTimeout(() => {
                updateCartBadge();
                updateCartSummary();
            }, 300);
        }
    });
});


