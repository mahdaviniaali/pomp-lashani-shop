from django.urls import path
from .views import UserRegister, OTPVerify, LogoutView, UserProfile, AddAddress, EditUserView, AddressListView, UserOrderDetailView

app_name = 'users'

urlpatterns = [
    path('login',UserRegister.as_view(),name='login'),
    path('verify',OTPVerify.as_view(),name='verify'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfile.as_view(), name='profile'),
    path('partials/add_address', AddAddress.as_view(), name='add_address'),
    path('partials/compleateprofile', EditUserView.as_view(), name='compleateprofile'),
    path('partials/user_addreaa', AddressListView.as_view(), name='user_address_list'),
    path('user_order/<order_id>', UserOrderDetailView.as_view(), name='user_order_detail'),

]