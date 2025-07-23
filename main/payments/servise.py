import logging
import json
from django.db import transaction
from django.db.models import F, Case, When
from django.contrib.sessions.backends.db import SessionStore
from django.shortcuts import get_object_or_404

from .models import Order, OrderItem, OrderShippingMethod, ShippingMethod
from carts.models import Cart, CartItem
from products.models import ProductVariant, Product

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self, order):
        self.order = order

    @staticmethod
    def create_order(user, **data):
        try:
            with transaction.atomic():
                cart = Cart.objects.filter(user=user).first()
                if not cart:
                    logger.warning(f"⛔ سبد خرید برای کاربر {user.id} یافت نشد.")
                    raise ValueError("سبد خرید یافت نشد.")

                cart_items = CartItem.objects.filter(cart=cart).select_related('product')
                if not cart_items.exists():
                    logger.warning(f"⚠️ سبد خرید کاربر {user.id} خالی است.")
                    raise ValueError("سبد خرید خالی است.")

                shipping_method_id = data.get('shippingmethod')
                shipping_method = get_object_or_404(ShippingMethod, id=shipping_method_id)
                logger.info(f"🚚 روش ارسال انتخاب شده برای کاربر {user.id}: {shipping_method.name} ({shipping_method.price} تومان)")

                cart.update_total_price()

                order_shipping = OrderShippingMethod.objects.create_from_dict(
                    name=shipping_method.name,
                    price=shipping_method.price,
                    is_postpaid=shipping_method.is_postpaid
                )

                order = Order.objects.create_order(user, order_shipping, **data)
                logger.info(f"✅ سفارش جدید برای کاربر {user.id} با شناسه {order.id} ایجاد شد.")

                order_items = []
                for item in cart_items:
                    order_items.append(OrderItem(
                        order=order,
                        product_name=item.product.title,
                        price=item.price,
                        quantity=item.quantity,
                    ))
                    logger.debug(f"📦 آیتم سفارش: {item.product.title} × {item.quantity} | قیمت: {item.price}")

                OrderItem.objects.bulk_create(order_items)
                logger.info(f"🛒 مجموعاً {len(order_items)} آیتم برای سفارش {order.id} ذخیره شد.")

                # آپدیت موجودی
                variants_to_update = [
                    (item.variant.id, item.quantity)
                    for item in cart_items
                    if hasattr(item, 'variant') and item.variant
                ]

                if variants_to_update:
                    ProductVariant.objects.filter(
                        id__in=[vid for vid, _ in variants_to_update]
                    ).update(
                        stock=F('stock') - Case(
                            *[When(id=vid, then=quantity) for vid, quantity in variants_to_update],
                            default=0
                        )
                    )
                    logger.info(f"📉 موجودی {len(variants_to_update)} واریانت به‌روزرسانی شد.")

                cart_items.delete()
                logger.info(f"🧹 آیتم‌های سبد خرید کاربر {user.id} حذف شد.")

                order.update_total_price()
                logger.info(f"💰 قیمت نهایی سفارش {order.id} محاسبه شد.")
                return order.id

        except Exception as e:
            logger.exception(f"🔥 خطا در ساخت سفارش برای کاربر {user.id}: {str(e)}")
            raise

    @staticmethod
    def stock_manage(session_key):
        try:
            session = SessionStore(session_key=session_key)
            if 'pending_stock_updates' not in session:
                logger.warning(f"❌ هیچ اطلاعاتی برای آپدیت موجودی در سشن {session_key} یافت نشد.")
                raise ValueError("اطلاعات موجودی در سشن یافت نشد.")

            cart_data = json.loads(session['pending_stock_updates'])

            variant_updates = {}
            product_updates = {}

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

                logger.debug(f"📊 برای واریانت {variant_id} → موجودی فعلی: {current_stock}، کسر: {quantity}")

            with transaction.atomic():
                variants = ProductVariant.objects.select_for_update().filter(
                    id__in=variant_updates.keys()
                )

                valid_variant_ids = {
                    v.id for v in variants
                    if v.stock == variant_updates[v.id]['current_stock']
                }

                if valid_variant_ids:
                    ProductVariant.objects.filter(id__in=valid_variant_ids).update(
                        stock=F('stock') - Case(
                            *[When(id=vid, then=variant_updates[vid]['quantity'])
                              for vid in valid_variant_ids],
                            default=0
                        )
                    )
                    logger.info(f"📦 موجودی واریانت‌های معتبر ({len(valid_variant_ids)}) آپدیت شد.")

                Product.objects.filter(id__in=product_updates.keys()).update(
                    sold_count=F('sold_count') + Case(
                        *[When(id=pid, then=quantity)
                          for pid, quantity in product_updates.items()],
                        default=0
                    )
                )
                logger.info(f"📈 تعداد فروش محصولات ({len(product_updates)}) به‌روزرسانی شد.")

            del session['pending_stock_updates']
            session.save()
            logger.info(f"🧹 سشن {session_key} برای آپدیت موجودی پاک‌سازی شد.")

        except Exception as e:
            logger.exception(f"🔥 خطا در مدیریت موجودی سشن {session_key}: {str(e)}")
            raise
