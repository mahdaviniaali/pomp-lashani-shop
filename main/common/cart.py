from carts.models import Cart , CartItem
from products.models import ProductVariant

def merge_cart (user , session_cart):
    
    if not session_cart:
        return    
    Cart.objects.filter(user=user).delete()

    cart, _ = Cart.objects.get_or_create(user=user)
    variant = ProductVariant.objects.filter(id__in=session_cart).select_related('product')
    print(variant)
    for variant_id, quantity in session_cart.items():
        variant_cart = variant.get(id=variant_id)
        print(variant_cart)
        if not variant:
            continue 

        CartItem.objects.create(cart=cart, product=variant_cart.product, productvariant=variant_cart, quantity=quantity, price=variant_cart.price)

    return {}