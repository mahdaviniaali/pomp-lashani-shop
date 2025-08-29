// cart.js - نسخه پیشرفته با مدیریت حذف و به‌روزرسانی سبد خرید

document.addEventListener('DOMContentLoaded', function() {
    class CartManager {
        constructor() {
            this.cartItems = [];
            this.init();
        }

        init() {
            this.cacheElements();
            this.setupEventListeners();
            this.loadInitialData();
            this.updateSummary();
        }

        cacheElements() {
            this.elements = {
                totalItemsCount: document.getElementById('total-items'),
                totalPriceElement: document.querySelector('.summary-total span.text-primary'),
                cartContainer: document.querySelector('.cart-container'),
                loadingOverlay: document.getElementById('loading-overlay'),
                cartBody: document.querySelector('.cart-body')
            };
        }

        setupEventListeners() {
            // HTMX event listeners
            document.body.addEventListener('htmx:afterSwap', this.handleHTMXAfterSwap.bind(this));
            document.body.addEventListener('htmx:beforeRequest', this.showLoading.bind(this));
            document.body.addEventListener('htmx:afterRequest', this.hideLoading.bind(this));
            document.body.addEventListener('htmx:responseError', this.handleHTMXError.bind(this));
            
            // حذف دستی محصولات
            this.elements.cartBody?.addEventListener('click', this.handleRemoveClick.bind(this));
        }

        loadInitialData() {
            document.querySelectorAll('.product-card').forEach(item => {
                this.cartItems.push(this.getItemData(item));
            });
        }

        getItemData(itemElement) {
            return {
                element: itemElement,
                price: parseInt(itemElement.querySelector('.product-price').textContent.replace(/[^0-9]/g, '')),
                quantityElement: itemElement.querySelector('.quantity-input'),
                quantity: parseInt(itemElement.querySelector('.quantity-input').textContent) || 0,
                id: itemElement.querySelector('.quantity-input').id,
                productId: itemElement.dataset.productId,
                variantId: itemElement.dataset.variantId
            };
        }

        handleHTMXAfterSwap(event) {
            const target = event.detail.target;
            
            // اگر مقدار تعداد تغییر کرد
            if (target.id && target.id.startsWith('number')) {
                const raw = (target.textContent || '').trim();
                const parsed = parseInt(raw, 10);
                const newQuantity = Number.isFinite(parsed) ? parsed : 0;
                
                // اگر تعداد صفر/نامعتبر شد، ابتدا حذف سمت سرور را قطعی کن، سپس از DOM حذف کن
                if (newQuantity <= 0) {
                    const productCard = target.closest('.product-card');
                    this.requestServerRemove(productCard);
                } else {
                    // در غیر این صورت فقط به‌روزرسانی کن
                    this.animateQuantityChange(target);
                    this.updateItemData(target);
                    this.updateSummary();
                }
            }
        }

        handleHTMXError(evt) {
            // اگر سرور آیتمی را پیدا نکرد (مثلاً 404/410)، از DOM حذف کن تا UI همگام شود
            const status = evt.detail.xhr ? evt.detail.xhr.status : 0;
            if (status === 404 || status === 410) {
                const target = evt.target;
                const productCard = target && target.closest ? target.closest('.product-card') : null;
                if (productCard) this.removeItemFromDOM(productCard);
            }
        }

        handleRemoveClick(event) {
            const removeBtn = event.target.closest('.remove-btn');
            if (!removeBtn) return;
            
            const productCard = removeBtn.closest('.product-card');
            // به‌جای حذف فوری در DOM، ابتدا درخواست حذف سمت سرور ارسال می‌شود
            this.requestServerRemove(productCard);
        }

        // ارسال درخواست حذف به سرور (هماهنگ با سشن/دیتابیس)
        requestServerRemove(itemElement) {
            const item = this.getItemData(itemElement);
            if (!item || !item.productId || !item.variantId) {
                // اگر داده کافی نبود، فقط حذف ظاهری انجام شود تا UI گیر نکند
                this.removeItemFromDOM(itemElement);
                return;
            }

            const url = '/carts/cart/remove/';
            const values = { product_id: item.productId, variant: item.variantId };
            const headers = { 'X-CSRFToken': this.getCSRFToken() };

            try {
                if (window.htmx && htmx.ajax) {
                    const xhr = htmx.ajax('POST', url, { values, headers, swap: 'none' });
                    xhr.addEventListener('load', () => {
                        this.removeItemFromDOM(itemElement);
                    });
                    xhr.addEventListener('error', () => {
                        // در صورت خطا، UI را برنگردانیم اما می‌توان پیام خطا نمایش داد
                        console.error('خطا در حذف آیتم از سرور');
                    });
                } else {
                    // fallback به fetch در صورت نبود htmx
                    fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                            'X-CSRFToken': this.getCSRFToken()
                        },
                        body: new URLSearchParams(values)
                    }).then(res => {
                        if (res.ok) this.removeItemFromDOM(itemElement);
                    }).catch(() => console.error('خطا در حذف آیتم (fetch)'));
                }
            } catch (e) {
                console.error(e);
            }
        }

        // حذف از DOM + بروزرسانی وضعیت داخلی
        removeItemFromDOM(itemElement) {
            // انیمیشن حذف
            itemElement.style.transition = 'all 0.3s ease';
            itemElement.style.opacity = '0';
            itemElement.style.height = '0';
            itemElement.style.padding = '0';
            itemElement.style.margin = '0';
            
            setTimeout(() => {
                // حذف از آرایه cartItems
                const itemId = itemElement.querySelector('.quantity-input').id;
                this.cartItems = this.cartItems.filter(item => item.id !== itemId);
                
                // حذف از DOM
                itemElement.remove();
                
                // به‌روزرسانی خلاصه سبد خرید
                this.updateSummary();
                
                // بررسی اگر سبد خرید خالی شد
                if (this.cartItems.length === 0) {
                    this.showEmptyCart();
                }
            }, 300);
        }

        showEmptyCart() {
            // کد نمایش سبد خرید خالی
            this.elements.cartContainer.innerHTML = `
                <div class="empty-cart">
                    <div class="empty-cart-icon">
                        <i class="fas fa-shopping-cart"></i>
                    </div>
                    <h3 class="empty-cart-text">سبد خرید شما خالی است</h3>
                    <a href="{% url 'products:product_list' %}" class="empty-cart-btn">
                        بازگشت به فروشگاه
                    </a>
                </div>
            `;
        }

        animateQuantityChange(element) {
            element.style.transform = 'scale(1.2)';
            setTimeout(() => {
                element.style.transform = 'scale(1)';
            }, 300);
        }

        updateItemData(quantityElement) {
            const itemId = quantityElement.id;
            const item = this.cartItems.find(item => item.id === itemId);
            if (item) {
                const raw = (quantityElement.textContent || '').trim();
                const parsed = parseInt(raw, 10);
                item.quantity = Number.isFinite(parsed) ? parsed : 0;
            }
        }

        calculateTotals() {
            let totalItems = 0;
            let totalPrice = 0;

            this.cartItems.forEach(item => {
                totalItems += item.quantity;
                totalPrice += item.quantity * item.price;
            });

            return { totalItems, totalPrice };
        }

        updateSummary() {
            const { totalItems, totalPrice } = this.calculateTotals();
            
            // قالب‌بندی اعداد به فارسی
            const formatter = new Intl.NumberFormat('fa-IR');
            
            // به‌روزرسانی DOM با انیمیشن
            this.animateValueChange(this.elements.totalItemsCount, totalItems, formatter);
            this.animateValueChange(this.elements.totalPriceElement, totalPrice, formatter);
        }

        animateValueChange(element, newValue, formatter) {
            if (!element) return;
            
            element.style.transform = 'translateY(-5px)';
            element.style.opacity = '0.5';
            element.style.transition = 'all 0.3s ease';
            
            setTimeout(() => {
                element.textContent = formatter.format(newValue);
                element.style.transform = 'translateY(0)';
                element.style.opacity = '1';
            }, 150);
        }

        showLoading() {
            if (this.elements.loadingOverlay) {
                this.elements.loadingOverlay.style.display = 'flex';
            }
        }

        hideLoading() {
            if (this.elements.loadingOverlay) {
                this.elements.loadingOverlay.style.display = 'none';
            }
        }

        getCSRFToken() {
            const name = 'csrftoken=';
            const decodedCookie = decodeURIComponent(document.cookie || '');
            const ca = decodedCookie.split(';');
            for (let i = 0; i < ca.length; i++) {
                let c = ca[i];
                while (c.charAt(0) === ' ') c = c.substring(1);
                if (c.indexOf(name) === 0) return c.substring(name.length, c.length);
            }
            return '';
        }
    }

    // Initialize cart manager
    const cartManager = new CartManager();
});