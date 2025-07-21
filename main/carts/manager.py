# product manager
from django.db.models import Manager , QuerySet



class CartItemQuerySet(QuerySet):

    def with_related(self):
        ''' این متد برای بارگذاری داده‌های مرتبط با محصول استفاده می‌شود.
        '''
        return (
            self.select_related('product', 'productvariant')
            
                )
    

    def with_product(self):
        ''' این متد برای بارگذاری داده‌های مرتبط با محصول استفاده می‌شود.
        '''
        return (
            self.select_related('product'))

class CartItemManager(Manager):
    def get_queryset(self):
        return CartItemQuerySet(self.model, using=self._db)

    def with_related(self):
        return self.get_queryset().with_related()
    


class CartQuerySet(QuerySet):
    def with_related(self):
        return (self.prefetch_related('items'))

class CartManager(Manager):

    def get_queryset(self):
        return CartQuerySet(self.model, using=self._db)

    def with_related(self):
        return self.get_queryset().with_related()