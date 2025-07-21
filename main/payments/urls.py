from django.urls import path
from .views import *

app_name = 'payments'


urlpatterns = [
    # سبد خرید
    path('checkout', PaymentWizard.as_view(), name='checkout'),
    path('payment/cart/request/<int:order_id>', CartPaymentRequestView.as_view(), name='cartpayment_start'),
    path('payment/cart/verify/<order_id>', CartPaymentVerifyView.as_view(), name='cart_payment_verify'),
    path('partials/load-shipping-methods/', load_shipping_methods, name='load_shipping_methods'),
    path('payment/manual/<int:order_id>', ManualPayment.as_view(), name='manual_payment'),
    path('payment/process/', PaymentProcessView.as_view(), name='payment_process'),
] 