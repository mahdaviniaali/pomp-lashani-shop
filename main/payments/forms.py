from django import forms
from users.forms import AddUserInfoForm
from users.models import Address
from django.utils.translation import gettext_lazy as _


class PaymentformInOrder(forms.Form):
    GATEWAY = 'gateway'
    MANUAL = 'manual'
    
    CHOICES = (
        (GATEWAY, _('درگاه بانکی')),
        (MANUAL, _('کارت به کارت')),
    )
    payment_method = forms.ChoiceField(
        choices=CHOICES,
        required=True,
        label=_('روش پرداخت')
    )
    order_id = forms.IntegerField(
        required=True,
        widget=forms.HiddenInput(),
        label=_('شناسه سفارش')
    )



class AddressForm(forms.ModelForm):
    
    class Meta:
        model = Address
        fields = '__all__'
        exclude = ['user', 'id', 'is_default'] 


class Step1Form(forms.Form):
    description = forms.CharField(
        label="توضیحات",
        widget=forms.Textarea,
        required=False,
    )

    shippingmethod = forms.CharField(label='شناسه روش ارسال', max_length=2, required=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # ایجاد نمونه‌های فرم‌های اصلی
        self.user_info_form = AddUserInfoForm(*args, **kwargs)
        self.address_form = AddressForm(*args, **kwargs)
        
        # اضافه کردن فیلدهای هر دو فرم به این فرم
        for field_name, field in self.user_info_form.fields.items():
            self.fields[f'user_{field_name}'] = field
            
        for field_name, field in self.address_form.fields.items():
            self.fields[f'address_{field_name}'] = field
    
    def clean(self):
        cleaned_data = super().clean()
               
        # استخراج و اعتبارسنجی داده‌های هر فرم
        user_data = {k.replace('user_', ''): v for k, v in cleaned_data.items() if k.startswith('user_')}
        address_data = {k.replace('address_', ''): v for k, v in cleaned_data.items() if k.startswith('address_')}
        
        # اعتبارسنجی جداگانه هر فرم
        self.user_info_form = AddUserInfoForm(data=user_data)
        self.address_form = AddressForm(data=address_data)
        
        if not self.user_info_form.is_valid():
            for field, errors in self.user_info_form.errors.items():
                self.add_error(f'user_{field}', errors)
                
        if not self.address_form.is_valid():
            for field, errors in self.address_form.errors.items():
                self.add_error(f'address_{field}', errors)
        
        return cleaned_data
    
    def get_description(self):
        """متد برای دسترسی به مقدار فیلد توضیحات"""
        return self.cleaned_data.get('description')
    
    @property
    def user_cleaned_data(self):
        return self.user_info_form.cleaned_data
    
    @property
    def address_cleaned_data(self):
        return self.address_form.cleaned_data
    
# step 2
class PaymentMethod:
    GATEWAY = 'gateway'
    MANUAL = 'manual'
    
    CHOICES = (
        (GATEWAY, _('درگاه بانکی')),
        (MANUAL, _('کارت به کارت')),
    )

class Step2Form(forms.Form):
    payment_method = forms.ChoiceField(
        choices=PaymentMethod.CHOICES,
        required=True,
        label='روش پرداخت'
    )
    

class ManualPaymentForm(forms.Form):
    card_number = forms.CharField(
        label=_("شماره کارت"),
        max_length=16,
        min_length=16,
        required=True,
        help_text=_("شماره 16 رقمی کارت بانکی خود را وارد کنید.")
    )
    
    receipt_image = forms.ImageField(
        label=_("تصویر رسید"),
        required=False,
        help_text=_("تصویر رسید پرداخت خود را بارگذاری کنید (اختیاری).")
    )
    
    description = forms.CharField(
        label=_("توضیحات"),
        widget=forms.Textarea,
        required=False,
        help_text=_("توضیحات اضافی در مورد پرداخت (اختیاری).")
    )