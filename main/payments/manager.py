# product manager
from django.db.models import Manager, QuerySet
from django.db import transaction
from django.db.models import Prefetch








class OrderQuerySet(QuerySet):
    def with_related(self):
        return (self.prefetch_related('items'))


class OrderManager(Manager):
    
    def create_order(self, user, shipping_method, **order_data):
        if not user:
            raise ValueError("کاربر باید برای سفارش تعیین شود")
        # ابتدا خود سفارش را بسازیم تا شناسه داشته باشد
        order = self.model(user=user)
        
        # ست کردن فیلدهای معتبر با setattr
        valid_fields = {f.name for f in self.model._meta.get_fields()}
        for field, value in order_data.items():
            if field in valid_fields:
                setattr(order, field, value)
        
        order.save()

        # اتصال روش ارسال به سفارش پس از ذخیره سفارش
        if shipping_method is not None:
            shipping_method.order = order
            shipping_method.save()
        return order
    

    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)

    def with_related(self):
        return self.get_queryset().with_related()
                            




class OrderItemManager(Manager):
    
    def create_from_cart(self, order, **data):
        with transaction.atomic():
            order_items = [
                self.model(
                    order=order,
                    product_name=item['productname'],
                    quantity=item['quantity'],
                    price=item['price']
                ) for item in data['items']
            ]
            self.bulk_create(order_items)

            return order_items
        


class OrderShippingMethodManager (Manager):

    
    def create_from_dict(self, **data):
        shipping_method = self.model(
            name=data.get('name'),
            price=data.get('price'),
            is_postpaid=data.get('is_postpaid')
        )
        shipping_method.save()
        return shipping_method