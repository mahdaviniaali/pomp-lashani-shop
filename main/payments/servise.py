from .models import Order, OrderItem, OrderShippingMethod, ShippingMethod
from carts.models import Cart, CartItem
from django.db import transaction
from products.models import ProductVariant, Product
from django.contrib.sessions.backends.db import SessionStore
import json
from django.db.models import F, Case, When


class OrderService:
    def __init__(self, order):
        self.order = order

    @staticmethod
    def create_order(user, **data):
        """ایجاد یک سفارش جدید"""
        with transaction.atomic():
            cart = Cart.objects.filter(user=user).first()
            if not cart:
                raise ValueError("سبد خرید وجود ندارد.")
                
            cart_items = CartItem.objects.filter(cart=cart).select_related('product')
            if not cart_items.exists():
                raise ValueError("سبد خرید خالی است.")
                
            shipping_method = ShippingMethod.objects.get(id=data.get('shippingmethod'))
            
            # ساخت سفارش
            cart.update_total_price()
            order_shipping = OrderShippingMethod.objects.create_from_dict(
                name=shipping_method.name,
                price=shipping_method.price,
                is_postpaid=shipping_method.is_postpaid
            )
            order = Order.objects.create_order(user, order_shipping, **data)
            
            # ایجاد آیتم‌های سفارش
            order_items = [
                OrderItem(
                    order=order,
                    product_name=item.product.title,
                    price=item.price,
                    quantity=item.quantity,
                )
                for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)
            
            # به‌روزرسانی موجودی به صورت اتمیک
            variant_updates = []
            for item in cart_items:
                if hasattr(item, 'variant'):
                    variant_updates.append(item.variant)
                    
            if variant_updates:
                ProductVariant.objects.filter(
                    id__in=[v.id for v in variant_updates]
                ).update(stock=F('stock') - 1)  # مقدار مناسب را قرار دهید
            
            # پاک کردن سبد خرید
            cart_items.delete()
            order.update_total_price()
            return order.id



    def stock_manage(session_key):
        try:
            session = SessionStore(session_key=session_key)
            
            if 'pending_stock_updates' not in session:
                
                raise ValueError("اطلاعات سبد خرید یافت نشد")
            
            cart_data = json.loads(session['pending_stock_updates'])
            
            # جمع‌آوری داده‌ها
            variant_updates = {}
            product_updates = {}
            valid_variant_ids = set()
            
            for item in cart_data:
                variant_id = item['variant_id']
                product_id = item['product_id']
                quantity = item['quantity']
                current_stock = item['current_stock']
                
                variant_updates[variant_id] = {
                    'quantity': quantity,
                    'current_stock': current_stock
                }
                product_updates[product_id] = product_updates.get(product_id, 0) + quantity
            
            # 1. قفل و بررسی موجودی‌ها در یک کوئری
            with transaction.atomic():
                # کوئری اول: قفل کردن و بررسی موجودی
                variants = ProductVariant.objects.select_for_update().filter(
                    id__in=variant_updates.keys()
                )
                
                # فیلتر واریانت‌های معتبر
                valid_variant_ids = {
                    v.id for v in variants 
                    if v.stock == variant_updates[v.id]['current_stock']
                }
                
                # کوئری دوم: به‌روزرسانی دسته‌جمعی واریانت‌های معتبر
                if valid_variant_ids:
                    ProductVariant.objects.filter(id__in=valid_variant_ids).update(
                        stock=F('stock') - Case(
                            *[When(id=vid, then=variant_updates[vid]['quantity']) 
                            for vid in valid_variant_ids],
                            default=0
                        )
                    )
                
                # کوئری سوم: به‌روزرسانی محصولات
                Product.objects.filter(id__in=product_updates.keys()).update(
                    sold_count=F('sold_count') + Case(
                        *[When(id=pid, then=quantity) 
                        for pid, quantity in product_updates.items()],
                        default=0
                    )
                )
            
            # پاک کردن سشن
            del session['pending_stock_updates']
            session.save()
            
        except Exception as e:
            print(f"خطا: {str(e)}")
            raise








































