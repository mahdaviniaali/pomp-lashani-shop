from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('sales/', views.sales_report, name='sales_report'),
    path('users/', views.users_report, name='users_report'),
    path('products/', views.products_report, name='products_report'),
    path('inventory/', views.inventory_report, name='inventory_report'),
    path('blog/', views.blog_report, name='blog_report'),
    path('ajax-data/', views.ajax_dashboard_data, name='ajax_data'),
]
