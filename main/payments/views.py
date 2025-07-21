from django.views import View
from django.shortcuts import render, redirect
from django.conf import settings
import requests
import json
from .models import ShippingMethod, Order, Payment, PaymentMethod, PaymentStatus
from .forms import Step1Form, Step2Form, ManualPaymentForm, PaymentformInOrder
from carts.models import Cart
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import Http404
from formtools.wizard.views import SessionWizardView
from .servise import OrderService
from common.utils import SendSMS 

ZP_API_REQUEST = 'https://sandbox.zarinpal.com/pg/v4/payment/request.json'
ZP_API_VERIFY = 'https://sandbox.zarinpal.com/pg/v4/payment/verify.json'
ZP_API_STARTPAY = 'https://sandbox.zarinpal.com/pg/StartPay/'

print(settings.ADMIN_PHONE)

#ویو مدیریت درخواست برای پرداخت 
class PaymentProcessView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            form = PaymentformInOrder(request.POST)
            
            if not form.is_valid():
                print("خطای فرم:", form.errors)
                return redirect('payment_error_page')

            cleaned_data = form.cleaned_data
            order_id = cleaned_data.get('order_id')
            payment_method = cleaned_data.get('payment_method')
            
            print(f"پرداخت شروع شد - سفارش: {order_id} - روش: {payment_method}")

            if payment_method == 'gateway':
                return redirect(reverse('payments:cartpayment_start', kwargs={'order_id': order_id}))
            elif payment_method == 'manual':
                return redirect(reverse('payments:manual_payment', kwargs={'order_id': order_id}))
            else:
                print("روش پرداخت نامعتبر:", payment_method)
                return redirect('payment_error_page')

        except Exception as e:
            print("خطای سیستمی:", str(e))
            return redirect('payment_error_page')

# ویو پرداخت کارت به کارت 
class PhotoPaymentRequestView(LoginRequiredMixin, View):
    def post(self, request):
        form = ManualPaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.status = 'pending'
            payment.save()
            
            # ارسال پیامک به کاربر
            SendSMS.send_sms(
                number=request.user.phone_number,
                message="درخواست پرداخت کارت به کارت شما ثبت شد و در انتظار تایید است"
            )
            
            # ارسال پیامک به ادمین
            SendSMS.send_sms(
                number=settings.ADMIN_PHONE,
                message=f"درخواست پرداخت کارت به کارت جدید از {request.user.fullname}"
            )
            
            messages.success(request, "پرداخت شما ثبت شد و منتظر تایید است.")
            return redirect('somewhere')
        else:
            form = ManualPaymentForm()
        return render(request, 'manual_payment.html', {'form': form})



class ManualPayment(LoginRequiredMixin, View):
    def get(self, request, order_id):
        user = request.user
        order_id = order_id
        session_key = request.session.session_key
        order = Order.objects.get(id=order_id, status="pending")
        order.status = 'waiting_approval'
        order.save()
        order.update_total_price()
        
        try:
            OrderService.stock_manage(session_key)
            
            # ارسال پیامک به کاربر
            massage = SendSMS.send_sms(
                number=request.user.phone_number,
                message="درخواست پرداخت کارت به کارت شما ثبت شد و در انتظار تایید است"
            )

            print(massage)
            # ارسال پیامک به ادمین
            admin_massage = SendSMS.send_sms(
                number=settings.ADMIN_PHONE,
                message=f"درخواست پرداخت کارت به کارت جدید از {request.user.fullname}"
            )

            print(admin_massage)

        except Exception as e:
            order.status = 'canceled'
            order.save()
            
            # ارسال پیامک خطا به کاربر
            massage = SendSMS.send_sms(
                number=user.phone_number,
                message="متأسفانه سفارش شما به دلیل مشکل در موجودی لغو شد"
            )
            
            return render(request, 'payment_error.html', {'message': 'خطا در مدیریت موجودی! لطفاً دوباره تلاش کنید.'})
        
        context = {
            'user': user,
            'order': order,
            'message':'مشخص نیست'
        }
        return render(request, 'orders/factor_detail.html', context)

class CartPaymentRequestView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        cart_id = order_id
        cart = Order.objects.get(id=cart_id, status="pending")
        session_key = request.session.session_key
        
        if not cart:
            raise Http404("سبد خرید پیدا نشد یا قبلاً پرداخت شده است!")

        amount = cart.get_total_price()
        if amount <= 0:
            return render(request, 'payment_error.html', {'message': 'سبد خرید شما خالی است یا مبلغ نامعتبر است!'})

        description = f"پرداخت سبد خرید شماره {cart.order_number}"
        phone = getattr(cart.user, 'phone_number', '')

        callback_url = request.build_absolute_uri(reverse('payments:cart_payment_verify', kwargs={'order_id': cart_id})+ f"?session_key={session_key}")

        data = {
            "merchant_id": settings.MERCHANT,
            "amount": amount,
            "description": description,
            "phone": phone,
            "callback_url": callback_url,
        }

        json_data = json.dumps(data)
        headers = {'content-type': 'application/json', 'content-length': str(len(json_data))}

        try:
            response = requests.post(ZP_API_REQUEST, data=json_data, headers=headers, timeout=10)

            if response.status_code == 200:
                result = response.json()
                data = result.get('data', {})
                if data.get('code') == 100:
                    cart.payment_authority = data['authority']
                    address = request.POST.get('address')
                    cart.address = address
                    cart.save()
                    
                    # ارسال پیامک به کاربر
                    SendSMS.send_sms(
                        number=request.user.phone_number,
                        message=f"لینک پرداخت برای سفارش {cart.order_number} ایجاد شد. مبلغ: {amount} تومان"
                    )
                    
                    return redirect(ZP_API_STARTPAY + str(data['authority']))

                return render(request, 'payment_error.html', {'message': f"خطا در پرداخت: {result.get('message')}"})

            return render(request, 'payment_error.html', {'message': 'پاسخ نامعتبر از زرین‌پال'})

        except requests.exceptions.RequestException as e:
            return render(request, 'payment_error.html', {'message': str(e)})

class CartPaymentVerifyView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        cart_id = order_id
        authority = request.GET.get('Authority')
        status = request.GET.get('Status')
        session_key = request.GET.get('session_key')
        base_context = {
            'payment_method': 'زرین پال',
        }

        if status != 'OK':
            # ارسال پیامک به کاربر در صورت لغو پرداخت
            SendSMS.send_sms(
                number=request.user.phone_number,
                message="پرداخت شما توسط درگاه پرداخت لغو شد"
            )
            
            context = {
                **base_context,
                'error_code': 'USER-CANCELED',
                'error_message': 'پرداخت توسط کاربر لغو شد',
                'amount': 0,
            }
            return render(request, 'payment_error.html', context)

        try:
            cart = Order.objects.get(id=cart_id, status="pending")
        except Order.DoesNotExist:
            context = {
                **base_context,
                'error_code': 'CART-NOT-FOUND',
                'error_message': 'سبد خرید پیدا نشد!',
                'amount': 0,
            }
            return render(request, 'payment_error.html', context)

        data = {
            "merchant_id": settings.MERCHANT,
            "amount": cart.get_total_price(),
            "authority": authority,
        }

        json_data = json.dumps(data)
        headers = {'content-type': 'application/json', 'content-length': str(len(json_data))}

        try:
            response = requests.post(ZP_API_VERIFY, data=json_data, headers=headers)

            if response.status_code == 200:
                result = response.json()
                data = result.get('data', {})
                
                if data.get('code') == 100:  # پرداخت موفق
                    cart.status = 'paid'
                    cart.payment_ref_id = data.get('ref_id', '')
                    cart.save()
                    
                    payment = Payment.objects.create(
                        user=request.user,
                        order=cart,
                        method=PaymentMethod.GATEWAY,
                        amount=cart.get_total_price(),
                        gateway_transaction_id=data.get('ref_id', ''),
                        status=PaymentStatus.SUCCESS
                    )
                    
                    OrderService.stock_manage(session_key)

                    # ارسال پیامک موفقیت پرداخت به کاربر
                    SendSMS.send_payment_success(
                        number=request.user.phone_number,
                        amount=cart.get_total_price(),
                        order_id=f'ORD-{cart.id}'
                    )
                    
                    # ارسال پیامک به ادمین
                    SendSMS.send_new_order_admin(
                        admin_phone=settings.ADMIN_PHONE,
                        order_id=f'ORD-{cart.id}',
                        customer_name=request.user.get_full_name()
                    )
                    
                    context = {
                        **base_context,
                        'order_id': f'ORD-{cart.id}',
                        'ref_id': data.get('ref_id', ''),
                        'payment': payment,
                        'order': cart,
                        'user': request.user,
                    }
                    return render(request, 'payment_success.html', context)

                # پرداخت ناموفق
                Payment.objects.create(
                    user=request.user,
                    order=cart,
                    method=PaymentMethod.GATEWAY,
                    amount=cart.get_total_price(),
                    gateway_transaction_id=authority,
                    status=PaymentStatus.FAILED,
                    description=f"کد خطای زرین پال: {data.get('code')}"
                )
                
                # ارسال پیامک خطا به کاربر
                SendSMS.send_sms(
                    number=request.user.phone_number,
                    message=f"پرداخت شما ناموفق بود. کد خطا: {data.get('code')}"
                )
                
                context = {
                    **base_context,
                    'order_id': f'ORD-{cart.id}',
                    'amount': cart.get_total_price(),
                    'error_code': f"ZP-{data.get('code')}",
                    'error_message': self._get_zarinpal_error_message(data.get('code')),
                }
                return render(request, 'payment_error.html', context)

            # خطا در ارتباط با زرین پال
            Payment.objects.create(
                user=request.user,
                order=cart,
                method=PaymentMethod.GATEWAY,
                amount=cart.get_total_price(),
                gateway_transaction_id=authority,
                status=PaymentStatus.FAILED,
                description='پاسخ نامعتبر از زرین‌پال'
            )
            
            context = {
                **base_context,
                'order_id': f'ORD-{cart.id}',
                'amount': cart.get_total_price(),
                'error_code': 'ZP-COMM-ERROR',
                'error_message': 'پاسخ نامعتبر از زرین‌پال',
            }
            return render(request, 'payment_error.html', context)

        except requests.exceptions.RequestException as e:
            Payment.objects.create(
                user=request.user,
                order=cart,
                method=PaymentMethod.GATEWAY,
                amount=cart.get_total_price(),
                gateway_transaction_id=authority,
                status=PaymentStatus.FAILED,
                description='خطا در ارتباط با درگاه پرداخت'
            )
            
            context = {
                **base_context,
                'order_id': f'ORD-{cart.id if cart else ""}',
                'amount': cart.get_total_price() if cart else 0,
                'error_code': 'NETWORK-ERROR',
                'error_message': 'خطا در ارتباط با درگاه پرداخت',
            }
            return render(request, 'payment_error.html', context)

    def _get_zarinpal_error_message(self, error_code):
        errors = {
            101: "تراکنش قبلا تایید شده است",
            102: "مبلغ نامعتبر است",
            103: "درخواست نامعتبر",
            104: "آی پی یا مرچنت کد نامعتبر است",
        }
        return errors.get(error_code, f"خطای پرداخت با کد {error_code}")

class PaymentWizard(LoginRequiredMixin, SessionWizardView):
    form_list = [
        ("step1", Step1Form),
        ("step2", Step2Form),
    ]
    
    templates = {
        "step1": "formwizard/step1form.html",  
        "step2": "formwizard/step2form.html", 
    }
    
    def get_template_names(self):
        return [self.templates[self.steps.current]]
    
    def done(self, form_list, **kwargs):
        user = self.request.user
        form_data = self.process_forms(form_list)
        cart = self.get_user_cart(user)
        
        if not cart:
            return self.handle_empty_cart()
            
        self.prepare_cart_data(cart)
        order = OrderService.create_order(user, **form_data)
        
        # ارسال پیامک ایجاد سفارش
        SendSMS.send_sms(
            number=user.phone_number,
            message=f"سفارش شما با کد {order} ایجاد شد. مبلغ کل: {cart.get_total_price()} تومان"
        )
        
        return self.handle_payment_flow(form_data, order, cart)
    
    def process_forms(self, form_list):
        form_data = {}
        for form in form_list:
            form_data.update(form.cleaned_data)
        return form_data
    
    def get_user_cart(self, user):
        return Cart.objects.filter(user=user).with_related().first()
    
    def prepare_cart_data(self, cart):
        cart.update_total_price()
        variants_to_update = [
            {
                'variant_id': item.productvariant.id,
                'product_id': item.product.id,
                'quantity': item.quantity,
                'current_stock': item.productvariant.stock
            }
            for item in cart.items.all()
        ]
        
        self.request.session['pending_stock_updates'] = json.dumps(variants_to_update)
        self.request.session['current_cart_id'] = cart.id
        self.request.session.set_expiry(3600)
    
    def handle_empty_cart(self):
        messages.error(self.request, "سبد خرید شما خالی است")
        return redirect('cart:view')
    
    def handle_payment_flow(self, form_data, order, cart):
        if form_data.get('payment_method') == 'gateway':
            return redirect(reverse('payments:cartpayment_start', kwargs={
                'order_id': order,
            }))
        
        if form_data.get('payment_method') == 'manual':
            # ارسال پیامک راهنمای پرداخت کارت به کارت
            SendSMS.send_sms(
                number=self.request.user.phone_number,
                message=f"برای پرداخت سفارش {order} مبلغ {cart.get_total_price()} تومان به شماره کارت XXXX-XXXX-XXXX-XXXX واریز نمایید"
            )
            return redirect(reverse('payments:manual_payment', kwargs={
                'order_id': order,
            }))
        
        try:
            cart.delete()
            messages.success(self.request, "پرداخت با موفقیت انجام شد")
        except Exception as e:
            messages.error(self.request, "خطا در پردازش سفارش")
            return redirect('checkout_error')
        
        return render(self.request, 'wiz.html', {
            'form_data': form_data,
            'cart_items': cart.items.all(),
            'total_price': cart.total_price,
            'order': order
        })

def load_shipping_methods(request):
    methods = ShippingMethod.objects.filter(active=True).order_by('price')
    return render(request, 'partials/shipping_methods_partial.html', {
        'shipping_methods': methods
    })