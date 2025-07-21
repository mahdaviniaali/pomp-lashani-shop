from django.urls import path
from .views import (
    CartAdd, CartRemove, CartDecrease, CartClear, CartDetail, ProductQuantityInCart, ProductQuantityInCartJustNumber, CartAddJustNumber
,CartDecreaseJustNumber, CartTotalView, CartItemListViewHtmx
)

app_name = 'carts'

urlpatterns = [
    path('cart/add', CartAdd.as_view(), name='cartadd'),
    path('cart/count/<product_id>', ProductQuantityInCart.as_view(), name='cart_count'),
    path('cart/remove/', CartRemove.as_view(), name='cart_remove'),
    path('cart/decrease/', CartDecrease.as_view(), name='cart_decrease'),
    path('cart/clear/', CartClear.as_view(), name='cart_clear'),
    path('cart/', CartDetail.as_view(), name='cart_detail'),
    #partials
    path('partials/number', ProductQuantityInCartJustNumber.as_view(), name='cart_just_number' ),
    path('partials/add', CartAddJustNumber.as_view(), name='cart_add_just_number' ),
    path('partials/decrease', CartDecreaseJustNumber.as_view(), name='cart_decrease_just_number' ),
    path('cart/total/', CartTotalView.as_view(), name='get_cart_total'),
        path('cart/items/', CartItemListViewHtmx.as_view(), name='cart_items_partial'),


]
