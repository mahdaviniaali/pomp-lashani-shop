from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import *
from products.models import Product, ProductVariant
from .forms import *
from django.http import JsonResponse, HttpResponse
import logging

# Create your views here.

logger = logging.getLogger(__name__)

##############
#-----نمایش سبد خرید---------#
##############


# صفحه سبد خرید
class CartDetail(View):
    """کلاس نمایش سبد خرید با قابلیت مدیریت کاربران لاگین کرده و مهمان"""
    
    def get(self, request):
        """
        هندلر درخواست GET برای نمایش سبد خرید
        
        Args:
            request: درخواست دریافتی از کاربر
            
        Returns:
            رندر تمپلیت cart.html با اطلاعات سبد خرید
        """
        logger.info("درخواست نمایش سبد خرید دریافت شد")
        
        user = request.user
        context = {'total_price': 0, 'cart_items': []}
        
        if user.is_authenticated:
            logger.info(f"کاربر لاگین کرده: {user.username}")
            
            try:
                # ایجاد یا دریافت سبد خرید کاربر
                cart, created = Cart.objects.get_or_create(user=user)
                logger.info(f"سبد خرید {'ایجاد شد' if created else 'از قبل وجود داشت'} برای کاربر {user.username}")
                
                # دریافت سبد خرید با بهینه‌سازی کوئری‌ها
                cart = Cart.objects.prefetch_related(
                    'items__productvariant',  # پیش‌بارگیری واریانت محصولات
                    'items__product'         # پیش‌بارگیری خود محصولات
                ).get(id=cart.id)
                
                logger.debug(f"سبد خرید با {cart.items.count()} آیتم بارگیری شد")
                
                # پر کردن context با اطلاعات سبد خرید
                context.update({
                    'cart': cart,
                    'total_price': cart.total_price,
                    'cart_items': cart.items.all()
                })
                
            except Exception as e:
                logger.error(f"خطا در دریافت سبد خرید کاربر: {str(e)}")
                context['error'] = "خطا در دریافت سبد خرید"
                
        else:
            logger.info("کاربر مهمان تشخیص داده شد")
            
            try:
                # دریافت سبد خرید از session
                session_cart = request.session.get('cart', {})
                logger.debug(f"سبد خرید session: {session_cart}")
                
                # تبدیل کلیدهای session به integer (آی دی واریانت)
                variant_ids = [int(k) for k in session_cart.keys() if k.isdigit()]
                
                items = []
                total = 0
                
                if variant_ids:
                    # دریافت واریانت‌های محصول از دیتابیس
                    variants = ProductVariant.objects.filter(
                        id__in=variant_ids
                    ).select_related('product')  # بهینه‌سازی کوئری
                    
                    logger.debug(f"تعداد واریانت‌های یافت شده: {variants.count()}")
                    
                    for variant in variants:
                        quantity = session_cart.get(str(variant.id), 1)
                        item_total = quantity * variant.price
                        
                        items.append({
                            'variant': variant,
                            'product': variant.product,
                            'quantity': quantity,
                            'price': variant.price,
                            'total': item_total
                        })
                        
                        total += item_total
                        logger.debug(f"آیتم افزوده شده: {variant.product.title} - تعداد: {quantity}")
                
                context.update({
                    'cart_items': items,
                    'total_price': total
                })
                
            except Exception as e:
                logger.error(f"خطا در پردازش سبد خرید مهمان: {str(e)}")
                context['error'] = "خطا در نمایش سبد خرید"
        
        logger.info(f"سبد خرید با {len(context['cart_items'])} آیتم و قیمت کل {context['total_price']} آماده نمایش است")
        return render(request, 'cart.html', context)

#cart count:
#نمایش تعداد محصول در سبد
class ProductQuantityInCart(View):
    def get(self, request, product_id):
        user = request.user
        quantity = 0
        product = None
        productvariant = None

        try:
            product = get_object_or_404(Product, id=product_id)
            variant_id = request.GET.get('variant')
            productvariant = get_object_or_404(ProductVariant, product=product, id=variant_id)

            if user.is_authenticated:
                cart = Cart.objects.filter(user=user).with_related().first()
                item = CartItem.objects.get(cart=cart, product_id=product_id, productvariant=productvariant)
                quantity = item.quantity
            else:
                cart = request.session.get('cart', {})
                print(variant_id)
                quantity = cart.get(str(variant_id), 0)
                print(quantity)


        except Exception as e:
            quantity = 0

        return render(request, 'product_count.html', {
            "quantity": quantity,
            "product": product,
            "variant": productvariant
        })

#فقط برای اعداد
class ProductQuantityInCartJustNumber(View):
    def get(self, request, product_id):
        user = request.user
        quantity = 0
        product = None
        productvariant = None

        try:
            product = get_object_or_404(Product, id=product_id)
            variant_id = request.GET.get('variant')
            productvariant = get_object_or_404(ProductVariant, product=product, id=variant_id)

            if user.is_authenticated:
                cart = Cart.objects.filter(user=user).with_related().first()
                item = CartItem.objects.get(cart=cart, product_id=product_id, productvariant=productvariant)
                quantity = item.quantity
            else:
                cart = request.session.get('cart', {})
                print(variant_id)
                quantity = cart.get(str(variant_id), 0)
                print(quantity)


        except Exception as e:
            quantity = 0

        return render(request, 'product_count_number.html', {
            "quantity": quantity,
        })



# قیمت سبد خریدو به صورت جدا
class CartTotalView(View):

    def get(self, request):

        cart = Cart.objects.get(user=request.user) 
        total = cart.get_total_price()    
        
        formatted_total = "{:,}".format(total)
        
        return HttpResponse(f"{formatted_total} تومان")
    
#ایتم های سبد خرید را به صورت جدا
class CartItemListViewHtmx(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            cart = Cart.objects.get(user=request.user)
            cart_items = cart.items.all() if cart else []
        else:
            session_cart = request.session.get('cart', {})
            cart_items = []
            variant = ProductVariant.objects.filter(id__in=session_cart.keys())
            Product = Product.objects.filter(variants__in=variant)
            for product in Product:
                quantity = session_cart.get(str(product.variants.first().id), 0)
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                })

        return render(request, 'cart_items_list.html', {'cart_items': cart_items})
    


##############
#-----کم کردن تعداد سبد خرید---------#
##############

#htmx
class CartRemove(View):
    def post(self, request):
        form = CartRemoveForm(request.POST)
        product = None
        product_variant = None
        quantity = 0
        message = None
        success = False
        user = request.user
        if form.is_valid():
            product_id = form.cleaned_data['product_id']
            variant_id = form.cleaned_data['variant']

            product = get_object_or_404(Product, id=product_id)
            product_variant = get_object_or_404(ProductVariant, product=product, id=variant_id)
            if user.is_authenticated:
                cart = Cart.objects.filter(user=user).first()
                if cart:
                    cart_item = cart.items.filter(product_id=product_id).first()
                    if cart_item:
                        cart_item.delete()
            else:
                session_cart = request.session.get('cart', {})
                variant_key = variant_id
                
                if str(variant_key) in session_cart:
                    del session_cart[str(variant_key)]
                    request.session['cart'] = session_cart
                    request.session.modified = True

            return render(request, 'product_count.html', {
            'message': message,
            'quantity': quantity,
            'product': product,
            'variant': product_variant,
            'success': success})
        else:
            message = "اطلاعات ارسال شده نامعتبر است."

        return render(request, 'product_count.html', {
            'message': message,
            'quantity': quantity,
            'product': product,
            'variant': product_variant,
            'success': success
        })



#htmx
# برای کم کردن و نشون دادن عدد در جزئیات
class CartDecrease(View):
    def post(self, request):
        form = CartRemoveForm(request.POST)
        user = request.user
        
        if form.is_valid():
            product_id = form.cleaned_data['product_id']
            variant_id = form.cleaned_data['variant']

            product = get_object_or_404(Product, id=product_id)
            product_variant = get_object_or_404(ProductVariant, product=product, id=variant_id)
            
            if user.is_authenticated:
                cart = Cart.objects.filter(user=user).first()
                if cart:
                    cart_item = cart.items.filter(product_id=product_id).first()
                    if cart_item:
                        quantity = cart_item.decrease_one()
            else:
                session_cart = request.session.get('cart', {})
                variant_key = variant_id
                current_quantity = session_cart.get(str(variant_key), 0)
                print(session_cart)
                print(variant_key)
                print(current_quantity)

                if current_quantity < 1:
                    quantity = 0
                else:
                    quantity = current_quantity - 1  
                    session_cart[variant_key] = quantity
                    request.session['cart'] = session_cart
                    request.session.modified = True
        return render(request, 'product_count.html', {
            'quantity': quantity,
            'product': product,
            'variant': product_variant,
        })
        
        


# فقط برای نشون دادن یدونه عدد
class CartDecreaseJustNumber(View):
    def post(self, request):
        form = CartRemoveForm(request.POST)
        user = request.user
        
        if form.is_valid():
            variant_id = form.cleaned_data['variant']

            if user.is_authenticated:
                cart = Cart.objects.filter(user=user).first()
                if cart:
                    cart_item = get_object_or_404(CartItem, cart=cart, productvariant=variant_id)
                    if cart_item:
                        quantity = cart_item.decrease_one()
            else:
                session_cart = request.session.get('cart', {})
                variant_key = variant_id
                current_quantity = session_cart.get(str(variant_key), 0)
                print(session_cart)
                print(variant_key)
                print(current_quantity)

                if current_quantity < 1:
                    quantity = 0
                else:
                    quantity = current_quantity - 1  
                    session_cart[variant_key] = quantity
                    request.session['cart'] = session_cart
                    request.session.modified = True

        return render(request, 'product_count_number.html', {
            'quantity': quantity,
           
        })
    


# اینو حس میکنم نمیشه با htmx زد چون مشخص نیست کجا میره... سعی کن تو خود سبد هندلش کنی
#htmx
#پاک کردن کل سبد
class CartClear(View):
    def get(self, request):
        user = request.user

        if user.is_authenticated:
            Cart.objects.filter(user=user).delete()
        else:
            request.session['cart'] = {}
            request.session.modified = True

        return JsonResponse({'success': True})


##############
#-----افزایش تعداد سبد خرید---------#
##############



#cart add:

class CartAdd(View):
    def post(self, request):
        form = CartAddForm(request.POST)
        product = None
        product_variant = None
        quantity = 0
        message = None
        success = False

        if form.is_valid():
            product_id = form.cleaned_data['product_id']
            variant_id = form.cleaned_data['variant']

            product = get_object_or_404(Product, id=product_id)
            product_variant = get_object_or_404(ProductVariant, product=product, id=variant_id)

            if request.user.is_authenticated:
                user = request.user
                cart, _ = Cart.objects.get_or_create(user=user)
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    productvariant=product_variant,
                    defaults={'price': product_variant.price}
                )

                current_quantity = cart_item.quantity if not created else 0
                if current_quantity + 1 > product_variant.stock:
                    message = f'موجودی کافی نیست. حداکثر موجودی: {product_variant.stock}'
                    quantity = current_quantity
                else:
                    quantity = cart_item.add_one()
                    success = True

            else:
                session_cart = request.session.get('cart', {})
                variant_key = variant_id
                current_quantity = session_cart.get(str(variant_key), 0)
                print(session_cart)
                print(variant_key)
                print(current_quantity)

                if current_quantity + 1 > product_variant.stock:
                    message = f'موجودی کافی نیست. حداکثر موجودی: {product_variant.stock}'
                    quantity = current_quantity
                else:
                    quantity = current_quantity + 1
                    session_cart[str(variant_key)] = quantity
                    request.session['cart'] = session_cart
                    request.session.modified = True
                    success = True
        

            return render(request, 'product_count.html', {
                'message': message,
                'quantity': quantity,
                'product': product,
                'variant': product_variant,
                'success': success
            })

# برای اضافه کردن و ایجاد یدونه عدد
class CartAddJustNumber(View):
    def post(self, request):
        form = CartAddForm(request.POST)
        product = None
        product_variant = None
        quantity = 0
        if form.is_valid():
            product_id = form.cleaned_data['product_id']
            variant_id = form.cleaned_data['variant']

            product = get_object_or_404(Product, id=product_id)
            product_variant = get_object_or_404(ProductVariant, product=product, id=variant_id)

            if request.user.is_authenticated:
                user = request.user
                cart, _ = Cart.objects.get_or_create(user=user)
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    productvariant=product_variant,
                    defaults={'price': product_variant.price}
                )

                current_quantity = cart_item.quantity if not created else 0
                if current_quantity + 1 > product_variant.stock:
                    message = f'موجودی کافی نیست. حداکثر موجودی: {product_variant.stock}'
                    quantity = current_quantity
                else:
                    quantity = cart_item.add_one()
                    success = True

            else:
                session_cart = request.session.get('cart', {})
                variant_key = variant_id
                current_quantity = session_cart.get(str(variant_key), 0)
                print(session_cart)
                print(variant_key)
                print(current_quantity)

                if current_quantity + 1 > product_variant.stock:
                    message = f'موجودی کافی نیست. حداکثر موجودی: {product_variant.stock}'
                    quantity = current_quantity
                else:
                    quantity = current_quantity + 1
                    session_cart[str(variant_key)] = quantity
                    request.session['cart'] = session_cart
                    request.session.modified = True
                    success = True
        

            return render(request, 'product_count_number.html', {
                'quantity': quantity,
            })



