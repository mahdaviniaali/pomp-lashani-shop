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


class CartDetail(View):
    """کلاس نمایش سبد خرید با ساختار یکسان برای کاربران لاگین کرده و مهمان"""
    
    def get_cart_items_for_authenticated_user(self, user):
        """استخراج آیتم‌های سبد خرید برای کاربر لاگین کرده"""
        try:
            cart = Cart.objects.prefetch_related(
                'items__productvariant',
                'items__product'
            ).get(user=user)
            
            items = []
            total_items = 0
            for item in cart.items.all():
                items.append({
                    'id': item.id,
                    'product': item.product,
                    'productvariant': item.productvariant,
                    'quantity': item.quantity,
                    'price': item.productvariant.price,
                    'total': item.quantity * item.productvariant.price
                })
                total_items += item.quantity
            
            return {
                'cart_items': items,
                'total_price': cart.total_price,
                'total_items': total_items,
                'cart': cart
            }
        except Exception as e:
            logger.error(f"خطا در دریافت سبد خرید کاربر: {str(e)}")
            return {'error': "خطا در دریافت سبد خرید"}

    def get_cart_items_for_guest(self, session_cart):
        """استخراج آیتم‌های سبد خرید برای کاربر مهمان"""
        try:
            variant_ids = [int(k) for k in session_cart.keys() if k.isdigit()]
            items = []
            total = 0
            total_items = 0
            
            if variant_ids:
                variants = ProductVariant.objects.filter(
                    id__in=variant_ids
                ).select_related('product')
                
                for variant in variants:
                    quantity = session_cart.get(str(variant.id), 1)
                    item_total = quantity * variant.price
                    
                    items.append({
                        'id': variant.id,  # استفاده از variant.id به جای item.id
                        'product': variant.product,
                        'productvariant': variant,
                        'quantity': quantity,
                        'price': variant.price,
                        'total': item_total
                    })
                    
                    total += item_total
                    total_items += quantity
            
            return {
                'cart_items': items,
                'total_price': total,
                'total_items': total_items,
                'cart': None  # برای یکسان‌سازی با حالت لاگین کرده
            }
        except Exception as e:
            logger.error(f"خطا در پردازش سبد خرید مهمان: {str(e)}")
            return {'error': "خطا در نمایش سبد خرید"}

    def get(self, request):
        logger.info("درخواست نمایش سبد خرید دریافت شد")
        
        context = {
            'total_price': 0,
            'cart_items': [],
            'cart': None,
            'total_items': 0,
        }
        
        if request.user.is_authenticated:
            logger.info(f"کاربر لاگین کرده: {request.user.username}")
            context.update(self.get_cart_items_for_authenticated_user(request.user))
        else:
            logger.info("کاربر مهمان تشخیص داده شد")
            session_cart = request.session.get('cart', {})
            context.update(self.get_cart_items_for_guest(session_cart))
        
        logger.info(f"سبد خرید با {len(context['cart_items'])} آیتم آماده نمایش است")
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
                quantity = cart.get(str(variant_id), 0)


        except Exception as e:
            quantity = 0

        return render(request, 'product_count.html', {
            "quantity": quantity,
            "product": product,
            "variant": productvariant
        })

#نمایش تعداد محصول در سبد برای موبایل
class ProductQuantityInCartMobile(View):
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
                quantity = cart.get(str(variant_id), 0)


        except Exception as e:
            quantity = 0

        return render(request, 'product_count_mobile.html', {
            "quantity": quantity,
            "product": product,
            "variant": productvariant
        })

#افزایش تعداد محصول در سبد برای موبایل
class CartAddMobile(View):
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
             

                if current_quantity + 1 > product_variant.stock:
                    message = f'موجودی کافی نیست. حداکثر موجودی: {product_variant.stock}'
                    quantity = current_quantity
                else:
                    quantity = current_quantity + 1
                    session_cart[str(variant_key)] = quantity
                    request.session['cart'] = session_cart
                    request.session.modified = True
                    success = True
        

            return render(request, 'product_count_mobile.html', {
                'message': message,
                'quantity': quantity,
                'product': product,
                'variant': product_variant,
                'success': success
            })

#کاهش تعداد محصول در سبد برای موبایل
class CartDecreaseMobile(View):
    def post(self, request):
        form = CartRemoveForm(request.POST)
        user = request.user
        quantity = 0
        product = None
        product_variant = None
        
        if form.is_valid():
            product_id = form.cleaned_data['product_id']
            variant_id = form.cleaned_data['variant']

            product = get_object_or_404(Product, id=product_id)
            product_variant = get_object_or_404(ProductVariant, product=product, id=variant_id)
            
            if user.is_authenticated:
                cart = Cart.objects.filter(user=user).first()
                if cart:
                    cart_item = cart.items.filter(product_id=product_id, productvariant=product_variant).first()
                    if cart_item:
                        quantity = cart_item.decrease_one()
            else:
                session_cart = request.session.get('cart', {})
                variant_key = str(variant_id)
                current_quantity = session_cart.get(variant_key, 0)
              

                if current_quantity <= 1:
                    quantity = 0
                    if variant_key in session_cart:
                        del session_cart[variant_key]
                else:
                    quantity = current_quantity - 1  
                    session_cart[variant_key] = quantity
                request.session['cart'] = session_cart
                request.session.modified = True
        return render(request, 'product_count_mobile.html', {
            'quantity': quantity,
            'product': product,
            'variant': product_variant,
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
                quantity = cart.get(str(variant_id), 0)


        except Exception as e:
            quantity = 0

        return render(request, 'product_count_number.html', {
            "quantity": quantity,
        })



# قیمت سبد خریدو به صورت جدا
class CartTotalView(View):

    def get(self, request):
        try:
            if request.user.is_authenticated:
                cart = Cart.objects.filter(user=request.user).first()
                if cart:
                    total = cart.get_final_price()
                else:
                    total = 0
            else:
                # محاسبه قیمت برای کاربران مهمان
                session_cart = request.session.get('cart', {})
                total = 0
                for variant_id, quantity in session_cart.items():
                    try:
                        variant = ProductVariant.objects.get(id=variant_id)
                        total += variant.price * quantity
                    except ProductVariant.DoesNotExist:
                        continue
            
            formatted_total = "{:,}".format(total)
            return HttpResponse(f"{formatted_total} تومان")
        except Exception as e:
            logger.error(f"خطا در محاسبه قیمت کل: {str(e)}")
            return HttpResponse("0 تومان")
    
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
            # اصلاح: بر اساس واریانت‌های موجود در سشن، آیتم‌ها را بساز
            variant_ids = [int(k) for k in session_cart.keys() if str(k).isdigit()]
            variants = ProductVariant.objects.filter(id__in=variant_ids).select_related('product')
            for variant in variants:
                quantity = session_cart.get(str(variant.id), 0)
                if quantity > 0:
                    cart_items.append({
                        'product': variant.product,
                        'quantity': quantity,
                        'productvariant': variant,
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
                    cart_item = cart.items.filter(product_id=product_id, productvariant=product_variant).first()
                    if cart_item:
                        cart_item.delete()
            else:
                session_cart = request.session.get('cart', {})
                variant_key = str(variant_id)
                
                if variant_key in session_cart:
                    del session_cart[variant_key]
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
                    cart_item = cart.items.filter(product_id=product_id, productvariant=product_variant).first()
                    if cart_item:
                        quantity = cart_item.decrease_one()
            else:
                session_cart = request.session.get('cart', {})
                variant_key = str(variant_id)
                current_quantity = session_cart.get(variant_key, 0)
              

                if current_quantity <= 1:
                    quantity = 0
                    if variant_key in session_cart:
                        del session_cart[variant_key]
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
                variant_key = str(variant_id)
                current_quantity = session_cart.get(variant_key, 0)
            
                if current_quantity <= 1:
                    quantity = 0
                    if variant_key in session_cart:
                        del session_cart[variant_key]
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



