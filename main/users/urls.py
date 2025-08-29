from django.urls import path
from .views import UserRegister , OTPVerify , LogoutView, UserProfile,UserAddressListView, UserOrderDetailView , AddAddress, AddressListView , EditUserView , factor_detail
from .views import DeleteAddress, EditAddress

app_name = 'users'

urlpatterns = [
    path('login/', UserRegister.as_view(), name='login'),
    path('verify/', OTPVerify.as_view(), name='verify'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfile.as_view(), name='profile'),
    path('user-order/<int:order_id>/', UserOrderDetailView.as_view(), name='user_order_detail'),

    #partials
    path('partials/add_address', AddAddress.as_view(), name='add_address'),
    path('partials/user_addreaa', AddressListView.as_view(), name='user_address_list'),
    path('partials/compleateprofile', EditUserView.as_view(), name='compleateprofile'),

    # address actions
    path('address/delete/<int:pk>/', DeleteAddress.as_view(), name='address_delete'),
    path('address/edit/<int:pk>/', EditAddress.as_view(), name='address_edit'),

    path('factor/<int:order_id>/', factor_detail, name='factor_detail')
]