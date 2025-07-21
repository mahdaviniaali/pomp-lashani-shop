from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import *
from products.models import Product, ProductVariant
from .forms import *
from django.http import JsonResponse, HttpResponse
# Create your views here.


######
#cart count
######


#htmx
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




# ajax
#حواست باشه که نسخه پایینی قدیمیه و باید به وایانت سنک بشه 
'''
class ProductQuantityInCartAjax(View):
    def get(self, request, product_id):
        user = request.user
        quantity = 0

        try:
            if user.is_authenticated:
                cart = Cart.objects.filter(user=user).with_related().first()
                item = CartItem.objects.filter(cart=cart, product_id=product_id).first()
                if item:
                    quantity = item.quantity
            else:
                cart = request.session.get('cart', {})
                quantity = cart.get(str(variant), 0)
        except:
            quantity = 0

        return JsonResponse({"quantity": quantity})
        '''

#########
#cart add
#########

#htmx
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

#ajax
'''
class CartAdd(View):
    def gpost(self, request):
        form = CartAddForm(request.POST)
        product = None
        product_variant = None
        quantity = 0
        message = None
        success = False


        product = get_object_or_404(Product, id=product_id)
        variant = product.variants.first()
        if user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=user)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                productvariant = variant,
                defaults={'price': variant.price}
            )

            # بررسی موجودی قبل از اضافه کردن
            current_quantity = cart_item.quantity if not created else 0
            if current_quantity + 1 > variant.stock:
                return JsonResponse({
                    'success': False,
                    'message': f'موجودی کافی نیست. حداکثر موجودی: {variant.stock}',
                    'quantity': current_quantity
                }, status=400)

            # افزایش تعداد و ذخیره
            if not created:
                cart_item.quantity = F('quantity') + 1
                cart_item.save()
                cart_item.refresh_from_db()
            else:
                cart_item.quantity = 1
                cart_item.save()

            cart.update_total_price()

            return JsonResponse({
                'success': True,
                'quantity': cart_item.quantity,
                'cart_total': cart.total_price
            })

        else:
            session_cart = request.session.get('cart', {})
            current_quantity = session_cart.get(str(product_id), 0)

            if current_quantity + 1 > variant.stock:
                return JsonResponse({
                    'success': False,
                    'message': f'موجودی کافی نیست. حداکثر موجودی: {variant.stock}',
                    'quantity': current_quantity
                }, status=400)

            session_cart[str(product_id)] = current_quantity + 1
            request.session['cart'] = session_cart
            request.session.modified = True

            return JsonResponse({
                'success': True,
                'quantity': session_cart[str(product_id)]
            })
'''


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
#ajax
'''

'''


#htmx
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
        
        


#alax
'''
'''

# اینو حس میکنم نمیشه با htmx زد چون مشخص نیست کجا میره... سعی کن تو خود سبد هندلش کنی
#htmx
class CartClear(View):
    def get(self, request):
        user = request.user

        if user.is_authenticated:
            Cart.objects.filter(user=user).delete()
        else:
            request.session['cart'] = {}
            request.session.modified = True

        return JsonResponse({'success': True})

#ajax
class CartClear(View):
    def get(self, request):
        user = request.user

        if user.is_authenticated:
            Cart.objects.filter(user=user).delete()
        else:
            request.session['cart'] = {}
            request.session.modified = True

        return JsonResponse({'success': True})



class CartDetail(View):
    """مشاهده جزئیات سبد خرید"""

    def get(self, request):
        user = request.user
        cart = None
        cart_items = []
        total_price = 0
        if user.is_authenticated:
            cart = Cart.objects.filter(user=user).with_related().first()
            cart.update_total_price()
            cart_items = cart.items.all() if cart else []
            total_price = cart.total_price if cart else 0

        else:
            session_cart = request.session.get('cart', {})
            products = Product.objects.filter(id__in=session_cart.keys())
            cart_items = [
                {
                    'product': product,
                    'quantity': session_cart[str(product.id)],
                    'price': product.variants.first().price
                }
                for product in products
            ]
            total_price = sum(item['quantity'] * item['price'] for item in cart_items)

        return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price, 'cart': cart})



#######
#partials
########


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
    



class CartDecreaseJustNumber(View):
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

        return render(request, 'product_count_number.html', {
            'quantity': quantity,
           
        })
    

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



class CartTotalView(View):

    def get(self, request):

        cart = Cart.objects.get(user=request.user)  # تابعی که سبد خرید کاربر را می‌دهد
        total = cart.get_total_price()      # محاسبه قیمت کل
        
        # فرمت عدد به صورت ۱,۱۵۹,۰۰۰
        formatted_total = "{:,}".format(total)
        
        return HttpResponse(f"{formatted_total} تومان")
    
#ایتم های سبد خرید را به صورت
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
    