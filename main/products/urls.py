from django.urls import path 
from .views import ProductListView, ProductListView, ProductDetailView, ProductPartials

app_name = 'products'

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('category/<persianslug:slug>/', ProductListView.as_view(), name='product_list_by_category'),
    path('<persianslug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/partials/', ProductPartials.as_view(), name="product_partial"),
    path('category/partials/<persianslug:slug>/', ProductPartials.as_view(), name="product_list_by_category_partial"),
]




