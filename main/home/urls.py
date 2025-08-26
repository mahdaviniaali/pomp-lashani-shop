from django.urls import path
from . import views
from products.views import ProductListView

app_name = 'home'

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('conectus', views.ConectUs.as_view(), name='conect_us'),
    path('aboutus', views.AboutUs.as_view(), name='about_us'),
    path('faq', views.FAQ.as_view(), name='faq'),
    # Partials
    path('partials/address', views.UserAddressListView.as_view(), name='address'),
    path('partials/userinfo', views.UserInfoView.as_view(), name='userinfo'),
    path('partials/product_search', ProductListView.as_view(), name='product_search'),
    
]
