from django.shortcuts import render,redirect,reverse
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import login
from .models import User, OTP, Address  
from django.contrib.auth import logout
from common.utils import SendSMS  
from common.cart import merge_cart
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import AddressForm , AddUserInfoForm
from django.contrib import messages
from users.models import Address
from payments.models import Order
from django.conf import settings
from payments.models import CartNumber




##############
#user register
##############

class UserRegister(View):
    def get(self, request):
        next_url = request.GET.get('next', '')  
        return render(request, 'login.html', {'next': next_url})

    def post(self, request):
        phone_number = request.POST.get("phone_number")
        next_url = request.POST.get("next", "")
        
        if not phone_number:
            messages.error(request, "شماره تلفن الزامی است.")
            return render(request, 'login.html', {'next': next_url})

        code = OTP.objects.create_otp_code(phone_number)
        print(code)
        if not code:
            messages.error(request, "خطا در ایجاد کد OTP.")
            return render(request, 'login.html', {'next': next_url})
        
        success = SendSMS.send_verify_code(
            number = phone_number,
            template_id = settings.SMSIR_VERIFY_TEMPLATE_ID,
            parameters = [
                {
                    "name": "Code",
                    "value": code
                }
            ]
        )
        if success:
            print("کد تأیید ارسال شد")
        else:
            print("خطا در ارسال")
        
        # ذخیره شماره تلفن در session برای استفاده در مرحله بعد
        request.session['otp_phone'] = phone_number
        request.session['otp_next'] = next_url
        
        messages.success(request, "کد OTP ارسال شد.")
        return redirect(reverse('users:verify'))  


class OTPVerify(View):
    def get(self, request):
        phone_number = request.session.get('otp_phone')
        next_url = request.session.get('otp_next', '')
        
        if not phone_number:
            return redirect('user_register')
            
        return render(request, 'otp.html', {
            'phone_number': phone_number,
            'next': next_url
        })

    def post(self, request):
        phone_number = request.POST.get("phone_number")
        input_code = request.POST.get("otp_code")
        next_url = request.POST.get("next", "")
        
        if not phone_number or not input_code:
            messages.error(request, "شماره تلفن و کد OTP الزامی هستند.")
            return render(request, 'otp.html', {
                'phone_number': phone_number,
                'next': next_url
            })

        try:
            otp = OTP.objects.get(phone_number=phone_number)
            
            if not otp.is_valid():
                messages.error(request, "کد OTP منقضی شده است.")
                return render(request, 'otp.html', {
                    'phone_number': phone_number,
                    'next': next_url
                })
                
            if otp.code != input_code:
                messages.error(request, "کد OTP نادرست است.")
                return render(request, 'otp.html', {
                    'phone_number': phone_number,
                    'next': next_url
                })

            user, created = User.objects.get_or_create(phone_number=phone_number)
            login(request, user)

            session_cart = request.session.get('cart', {})
            request.session['cart'] = merge_cart(user, session_cart)
            request.session.modified = True
            otp.delete()

            # پاک کردن اطلاعات session مربوط به OTP
            if 'otp_phone' in request.session:
                del request.session['otp_phone']
            if 'otp_next' in request.session:
                del request.session['otp_next']

            if next_url:
                return redirect(next_url)
            return redirect('/')

        except OTP.DoesNotExist:
            messages.error(request, "کد OTP نادرست است.")
            return render(request, 'otp.html', {
                'phone_number': phone_number,
                'next': next_url
            })




class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('/')

# پروفایل کاربر 
class UserProfile(LoginRequiredMixin, View):
    def get (self , request):
        user = request.user
        context={
            'user':user
        }
        return render (request, 'profile.html', context )
    



class UserAddressListView(LoginRequiredMixin, View):
    def get (self, request):
        user = request.user
        adress = user.user_address()
        if adress :
            return JsonResponse(adress)
        else:
            return None

# کلاس برای نمایش جزئیات سفارش کاربر
class UserOrderDetailView(LoginRequiredMixin, View):
    def get (self, request, order_id):
        user = request.user
        order = Order.objects.get(user=user, id=order_id)
        cart_number = CartNumber.objects.filter(available=True).first()

        context = {
        'user': user,
        'order': order,
        'cart_number':cart_number,
        }
        return render(request, 'orders/factor_detail.html', context)





##############
#partials  ویو های 
##############
class AddAddress(LoginRequiredMixin, View):
    def get (self, request):
        return render(request, 'partials/add_address_form.html', )

    def post (self,request):
        user = request.user
        form = AddressForm(request.POST)  # ایجاد فرم با داده‌های POST
        if form.is_valid():  # اینجا اعتبارسنجی انجام می‌شود
            cleaned_data = form.cleaned_data # داده‌های معتبر
            # پردازش داده‌ها...
            address, create = Address.objects.add_address(user, **cleaned_data)  # ذخیره آدرس در دیتابیس
            address = Address.objects.get(id=address)
            print(address)
            return render(request, 'partials/address_list.html', {'addresses': address, 'create':create})
        else:
            errors = form.errors  # خطاهای اعتبارسنجی
            print(errors)
            return render(request, 'partials/add_address_form.html', {'errors': errors})


class AddressListView(LoginRequiredMixin, View):
    'برای گرفتن ادرس های کاربر'

    def get (self, request):
        user = request.user
        address = Address.objects.filter(user=user)
        
        context = {
            'addresses' : address,
        }
        return render(request, 'partials/user_addresses.html', context)





# ادیت یا اضافه کردن اطلاعات کاربر 
class EditUserView(LoginRequiredMixin , View):
    def get (self, request):
        user = request.user
        context={
            'user':user
        }
        return render(request , 'partials/add_user_info_form.html', context )

    def post (self, request):
        form = AddUserInfoForm(request.POST)
        user = request.user

        if form.is_valid(): 
            cleaned_data = form.cleaned_data
            print(cleaned_data)
            user.add_and_edit_user_info(cleaned_data)
            return render(request, 'partials/user_info.html', {'user':user})    
        else:
            errors = form.errors  # خطاهای اعتبارسنجی
            print(errors)
            return render(request, 'partials/add_user_info_form.html', {'errors': errors})    
        




def factor_detail(request, order_id):
    user = request.user
    order = Order.objects.get(id=order_id, user=user)
    cart_number = CartNumber.objects.filter(available=True).first()
    print(cart_number)
    if not order:
        messages.error(request, "سفارش یافت نشد.")
        return redirect('users:profile')

    context = {
        'user': user,
        'order': order,
        'cart_number':cart_number,
    }
    
    return render(request, 'orders/factor_detail.html', context)