from django.urls import path 
from .views import ProductListView, ProductListView, ProductDetailView, ProductPartials, PriceRangeView
from .views_crop import crop_image, crop_form_view

app_name = 'products'

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('category/<int:pk>-<slug>/', ProductListView.as_view(), name='product_list_by_category'),
    path('d/<int:pk>-<slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/partials/', ProductPartials.as_view(), name="product_partial"),
    path('category/partials/', ProductPartials.as_view(), name="product_list_by_category_partial"),
    path('price-range/', PriceRangeView.as_view(), name="price_range"),
    path('crop-image/', crop_image, name='crop_image'),
    path('crop-form/', crop_form_view, name='crop_form'),
]




